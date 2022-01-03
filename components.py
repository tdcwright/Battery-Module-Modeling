###############
# components.py
# TOM WRIGHT 2021
###############

"""
Class definitions to handle the interactions between cells, bandoliers and modules. A module is created with
a set of model parameters (by default set to the values specified in modelParameters.py). Creating a module
creates a set of bandoliers, containing a set of cells. Since the simulation is a physics based simulaion,
some initial distance between bandoliers must be set, by default this is minimised, but can be increased if
needed. All other paremeters of cell spacing, cell count, bandolier count, etc are set in modelParameters.py.
"""

from typing import List, Tuple
import pymunk
from dataclasses import dataclass, field

import modelParameters
from endConstraints import EndConstraint, EndLimit

import numpy as np
import matplotlib.pyplot as plt

# Set up simulation space with arbitary gravity and low damping
def setupSpace() -> pymunk.Space:
    space = pymunk.Space()
    space.gravity = -1000,0
    space.damping = 0.00000000000000000000000001
    
    return space

# Definition of Cell class containing cell id (working from lowest cell to highest cell) and its positions
@dataclass
class Cell:
    id:int # cell ID
    xOffset:float # the variance in cell placement based on tolerance
    yOffset:float # the variance in cell placement based on tolerance
    xNominal:float # the CAD perfect position of the cell in a bandolier
    yNominal:float # the CAD perfect position of the cell in a bandolier
    xStart:float # the offset for the physics based simulation
    yStart:float # the offset for the physics based simulation
    space:pymunk.Space # simulation space
    cellDiameter:float # mm radius
    static:bool = False # Defines if the cell is fixed for the purposes of the simulation
    colour:Tuple[int, int, int, int] = field(default=(-1,-1,-1,-1)) # colour for visualisation purposes
    modelParams:modelParameters.ModelParams = modelParameters.DEFAULT_PARAMETERS

    def __post_init__(self) -> None:
        
        if (self.static):
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            cellMass = 10 # arbitary pymunk simulation variable, ignore
            momentOfInertia = 10 # arbitary pymunk simulation variable, ignore
            self.body = pymunk.Body(cellMass, momentOfInertia, body_type=pymunk.Body.DYNAMIC)
                   
        self.body.position = (self.xPosition, self.yPosition)
        self.shape = pymunk.Circle(self.body,self.cellDiameter/2)
        self.shape.elasticity = 0.0
        # self.shape.friction = 0.2
        
        if (min(self.colour) >= 0):
            self.shape.color = self.colour

        self.setFilter(1,1)

        self.space.add(self.body, self.shape)
    
    @property
    def xPosition(self) -> float:
        return self.xStart + self.xNominal + self.xOffset
    
    @property
    def yPosition(self) -> float:
        return self.yStart + self.yNominal + self.yOffset
    
    @property
    def simXPos(self) -> float:
        return self.body.position.x
    
    @property
    def simYPos(self) -> float:
        return self.body.position.y

    @property
    def velocity(self) -> float:
        return self.body.velocity

    def setStart(self, xPos:float, yPos:float) -> None:
        self.xStart = xPos
        self.yStart = yPos
        
        self.body.position = (self.xPosition, self.yPosition)
    
    def setFilter(self, category:int, mask:int) -> None:
        self.shape.filter = pymunk.ShapeFilter(categories=category, mask=mask)

# class definition of Bandolier to handle collections of cells and end constraints
@dataclass
class Bandolier:
    id: int
    space:pymunk.space
    x: float = 0
    y: float = 0
    static:bool = False
    modelParams:modelParameters.ModelParams = modelParameters.DEFAULT_PARAMETERS

    def __post_init__(self) -> None:
        self.desiredX:float = self.id*self.modelParams.BANDO_DESIRED_SPACING

        self.colour:Tuple[int, int, int, int] = modelParameters.COLOUR_ALL[self.id%(len(modelParameters.COLOUR_ALL))]
        
        self.createCells()

        if (self.modelParams.INCLUDE_END_CONSTRAINTS):
            self.setupEndConstraints()

        if (not self.static):
            self.constrainCells()

    # Creation of random variation in cell position and diameter
    def createCells(self) -> None:
        self.cells:List[Cell] = []

        xTolerances = np.random.normal(self.modelParams.BANDO_X_MU, self.modelParams.BANDO_X_SIGMA, self.modelParams.BANDO_CELL_COUNT)
        yTolerances = np.random.normal(self.modelParams.BANDO_Y_MU, self.modelParams.BANDO_Y_SIGMA, self.modelParams.BANDO_CELL_COUNT)
        diameterTolerances = self.modelParams.CELL_DIAMETER_CURRENT + np.random.normal(self.modelParams.CELL_DIAMETER_MU, self.modelParams.CELL_DIAMETER_SIGMA, self.modelParams.BANDO_CELL_COUNT)
        for i in range(self.modelParams.BANDO_CELL_COUNT):
            xPos = i%2 * self.modelParams.BANDO_CELL_X
            
            if (i%2 == 0):
                yPos = (i/2)*self.modelParams.BANDO_CELL_Y2
            else:
                yPos = ((i-1)/2)*self.modelParams.BANDO_CELL_Y2 + self.modelParams.BANDO_CELL_Y1
            
            newCell = Cell(i,
                xTolerances[i],
                yTolerances[i],
                xPos,
                yPos,
                self.x,
                self.y,
                self.space,
                diameterTolerances[i],
                self.static,
                self.colour,
                self.modelParams)

            self.cells.append(newCell)
    
    def setupEndConstraints(self) ->None:
        self.lowerConstraint = EndConstraint(self.modelParams.END_CONSTRAINT_LOWER_X,
            self.cells[0].yNominal,
            self.cells[0].yNominal-self.modelParams.END_CONSTRAINT_LOWER_Y,
            self.x,
            self.y,
            self.space,
            [x.body for x in self.cells[0:2]],
            self.colour,
            static=self.static,
            modelParams=self.modelParams)

        self.upperConstraint = EndConstraint(self.modelParams.END_CONSTRAINT_UPPER_X,
            self.cells[-1].yNominal,
            self.cells[-1].yNominal+self.modelParams.END_CONSTRAINT_UPPER_Y,
            self.x,
            self.y,
            self.space,
            [x.body for x in self.cells[-2:self.modelParams.BANDO_CELL_COUNT]],
            self.colour,
            static=self.static,
            modelParams=self.modelParams)
        
        self.lowerLimit = EndLimit(self.desiredX,
            self.modelParams.END_LIMIT_LOWER_X,
            self.cells[0].yNominal-self.modelParams.END_LIMIT_LOWER_Y,
            False,                
            self.space,
            self.colour,
            modelParams=self.modelParams)
        
        self.upperLimit = EndLimit(self.desiredX,
            self.modelParams.END_LIMIT_UPPER_X,
            self.cells[-1].yNominal+self.modelParams.END_LIMIT_UPPER_Y,
            True,                
            self.space,
            self.colour,
            modelParams=self.modelParams)
        
        self.constrainBando()

    def constrainCells(self) -> None:
        for i in range(self.modelParams.BANDO_CELL_COUNT-1):
            joint1 = pymunk.PinJoint(self.cells[i].body,self.cells[i+1].body)

            self.space.add(joint1)
            if i != self.modelParams.BANDO_CELL_COUNT-2:
                joint2 = pymunk.PinJoint(self.cells[i].body,self.cells[i+2].body)

                self.space.add(joint2)
    
    def constrainBando(self) -> None:

        category = 2**self.id
        self.upperConstraint.setFilter(category, category)
        self.lowerConstraint.setFilter(category, category)

        self.upperLimit.setFilter(category, category)
        self.lowerLimit.setFilter(category, category)
    
    def distanceFromUpperLimit(self) -> Tuple[float, float]:
        if (not self.modelParams.INCLUDE_END_CONSTRAINTS):
            return 0
        
        limitPos = (self.desiredX+self.modelParams.END_LIMIT_UPPER_X, self.cells[-1].yNominal+self.modelParams.END_LIMIT_UPPER_Y)
        return tuple(np.subtract(self.upperConstraint.body.position, limitPos))
    
    def distanceFromLowerLimit(self) -> Tuple[float, float]:
        if (not self.modelParams.INCLUDE_END_CONSTRAINTS):
            return 0
        
        limitPos = (self.desiredX+self.modelParams.END_LIMIT_LOWER_X, self.cells[0].yNominal-self.modelParams.END_LIMIT_LOWER_Y)
        return tuple(np.subtract(self.lowerConstraint.body.position, limitPos))

    def updatePosition(self) -> None:
        for cell in self.cells:
            cell.setStart(self.x, self.y)
            

class Module:
    def __init__(self,initialBandolierSpacing:int = 0, modelParams:modelParameters.ModelParams = modelParameters.DEFAULT_PARAMETERS) -> None:
        self.bandoliers:List[Bandolier] = []
        self.space:pymunk.Space = setupSpace()
        self.simulated = False
        self.modelParams:modelParameters.ModelParams = modelParams
        self.numBandos:int = self.modelParams.MODULE_BANDO_COUNT


        for i in range(self.numBandos):
            # xBandoOrigin = i*(abs(self.modelParams.BANDO_CELL_X) + self.modelParams.CELL_DIAMETER_CURRENT + 2*(abs(self.modelParams.BANDO_X_MU)+3*self.modelParams.BANDO_X_SIGMA) + initialBandolierSpacing)
            
            maxCellDiam = self.modelParams.CELL_DIAMETER_CURRENT + self.modelParams.CELL_DIAMETER_MU + 3*self.modelParams.CELL_DIAMETER_SIGMA
            maxCellOffset = self.modelParams.CELL_DIAMETER_MU+3*self.modelParams.CELL_DIAMETER_SIGMA
            xMinimalSpacingOfset=np.sqrt((maxCellDiam+maxCellOffset+1)**2-(self.modelParams.BANDO_CELL_Y2/2)**2)

            xBandoOrigin = i*(abs(self.modelParams.BANDO_CELL_X) + xMinimalSpacingOfset + initialBandolierSpacing)
            
            startingDistanceFromEndConstraint = 1 #mm 
            if (i != 0 and self.modelParams.INCLUDE_END_CONSTRAINTS and xBandoOrigin < i*self.modelParams.BANDO_DESIRED_SPACING+startingDistanceFromEndConstraint):
                xBandoOrigin = i*self.modelParams.BANDO_DESIRED_SPACING+startingDistanceFromEndConstraint
            
            yBandoOrigin = 0

            if (i == 0):
                static = True
            else:
                static = False

            self.bandoliers.append(Bandolier(i, self.space, xBandoOrigin, yBandoOrigin, static,self.modelParams))
    
    def getTotalWidth(self) -> float: #mm
        if (not self.simulated):
            return -1
        
        leftMostX = min([cell.simXPos for cell in self.bandoliers[0].cells])
        rightMostX = max([cell.simXPos for cell in self.bandoliers[-1].cells])

        return rightMostX-leftMostX+self.bandoliers[0].cells[0].cellDiameter
    
    def displayModule(self, title:str="", blocking:bool=True)->None:
        leftMostX = min([cell.simXPos for cell in self.bandoliers[0].cells])
        rightMostX = max([cell.simXPos for cell in self.bandoliers[-1].cells])
        bottomMostY = min([bando.cells[0].simYPos for bando in self.bandoliers])
        topMostY = max([bando.cells[-1].simYPos for bando in self.bandoliers])

        if self.modelParams.INCLUDE_END_CONSTRAINTS:
            bottomMostY -= max(self.modelParams.END_LIMIT_LOWER_Y, self.modelParams.END_CONSTRAINT_LOWER_Y)
            topMostY += max(self.modelParams.END_LIMIT_UPPER_Y, self.modelParams.END_CONSTRAINT_UPPER_Y)

        figureXLim = (leftMostX-25, rightMostX+25)
        figureYLim = (bottomMostY-25, topMostY+25)
        
        fig = plt.figure()
        ax = plt.axes(xlim=figureXLim, ylim=figureYLim)
        plt.title(title)
        ax.set_aspect("equal")

        drawOption = pymunk.matplotlib_util.DrawOptions(ax)
        drawOption.flags = pymunk.SpaceDebugDrawOptions.DRAW_SHAPES | \
                            pymunk.SpaceDebugDrawOptions.DRAW_COLLISION_POINTS | \
                            (pymunk.SpaceDebugDrawOptions.DRAW_CONSTRAINTS if modelParameters.DISPLAY_CONSTRAINTS else 0)
        self.space.debug_draw(drawOption)
        
        if (blocking):
            plt.show()



if __name__ == "__main__":
    pass