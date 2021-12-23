from typing import List, Tuple
import pymunk
from dataclasses import dataclass, field

import modelParameters
from endConstraints import EndConstraint, EndLimit

import numpy as np
import matplotlib.pyplot as plt


def setupSpace() -> pymunk.Space:
    space = pymunk.Space()
    space.gravity = -1000,0
    space.damping = 0.000001
    return space

@dataclass
class Cell:
    id:int
    xOffset:float
    yOffset:float
    xNominal:float
    yNominal:float
    xStart:float
    yStart:float
    space:pymunk.Space
    cellDiameter:float # mm radius
    static:bool = False
    colour:Tuple[int, int, int, int] = field(default=(-1,-1,-1,-1))
    cellMass = 10 # pymunk variable, ignore

    def __post_init__(self) -> None:
        
        if (self.static):
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            momentOfInertia = 10#pymunk.moment_for_circle(self.cellMass, 0, self.cellDiameter/2)
            self.body = pymunk.Body(self.cellMass, momentOfInertia, body_type=pymunk.Body.DYNAMIC)
                   
        self.body.position = (self.xPosition, self.yPosition)
        self.shape = pymunk.Circle(self.body,self.cellDiameter/2)
        self.shape.elasticity = 1
        
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


@dataclass
class Bandolier:
    id: int
    space:pymunk.space
    x: float = 0
    y: float = 0
    static:bool = False

    def __post_init__(self) -> None:
        self.desiredX:float = self.id*modelParameters.BANDO_DESIRED_SPACING

        self.colour:Tuple[int, int, int, int] = modelParameters.COLOUR_ALL[self.id%(len(modelParameters.COLOUR_ALL))]
        
        self.createCells()

        if (modelParameters.INCLUDE_END_CONSTRAINTS):
            self.setupEndConstraints()

        if (not self.static):
            self.constrainCells()

    def createCells(self) -> None:
        self.cells:List[Cell] = []

        xTolerances = np.random.normal(modelParameters.BANDO_X_MU, modelParameters.BANDO_X_SIGMA, modelParameters.BANDO_CELL_COUNT)
        yTolerances = np.random.normal(modelParameters.BANDO_Y_MU, modelParameters.BANDO_Y_SIGMA, modelParameters.BANDO_CELL_COUNT)
        diameterTolerances = modelParameters.CELL_DIAMETER_CURRENT + np.random.normal(modelParameters.CELL_DIAMETER_MU, modelParameters.CELL_DIAMETER_SIGMA, modelParameters.BANDO_CELL_COUNT)
        for i in range(modelParameters.BANDO_CELL_COUNT):
            xPos = i%2 * modelParameters.BANDO_CELL_X
            
            if (i%2 == 0):
                yPos = (i/2)*modelParameters.BANDO_CELL_Y2
            else:
                yPos = ((i-1)/2)*modelParameters.BANDO_CELL_Y2 + modelParameters.BANDO_CELL_Y1
            
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
                self.colour)

            self.cells.append(newCell)
    
    def setupEndConstraints(self) ->None:
        self.lowerConstraint = EndConstraint(modelParameters.END_CONSTRAINT_LOWER_X,
            self.cells[0].yNominal,
            self.cells[0].yNominal-modelParameters.END_CONSTRAINT_LOWER_Y,
            self.x,
            self.y,
            self.space,
            [x.body for x in self.cells[0:2]],
            self.colour,
            static=self.static)

        self.upperConstraint = EndConstraint(modelParameters.END_CONSTRAINT_UPPER_X,
            self.cells[-1].yNominal,
            self.cells[-1].yNominal+modelParameters.END_CONSTRAINT_UPPER_Y,
            self.x,
            self.y,
            self.space,
            [x.body for x in self.cells[-2:modelParameters.BANDO_CELL_COUNT]],
            self.colour,
            static=self.static)
        
        self.lowerLimit = EndLimit(self.desiredX,
            modelParameters.END_LIMIT_LOWER_X,
            self.cells[0].yNominal-modelParameters.END_LIMIT_LOWER_Y,
            False,                
            self.space,
            self.colour)
        
        self.upperLimit = EndLimit(self.desiredX,
            modelParameters.END_LIMIT_UPPER_X,
            self.cells[-1].yNominal+modelParameters.END_LIMIT_UPPER_Y,
            True,                
            self.space,
            self.colour)
        
        self.constrainBando()

    def constrainCells(self) -> None:
        for i in range(modelParameters.BANDO_CELL_COUNT-1):
            joint1 = pymunk.PinJoint(self.cells[i].body,self.cells[i+1].body)
            
            self.space.add(joint1)
            if i != modelParameters.BANDO_CELL_COUNT-2:
                joint2 = pymunk.PinJoint(self.cells[i].body,self.cells[i+2].body)

                self.space.add(joint2)
    
    def constrainBando(self) -> None:

        category = 2**self.id
        self.upperConstraint.setFilter(category, category)
        self.lowerConstraint.setFilter(category, category)

        self.upperLimit.setFilter(category, category)
        self.lowerLimit.setFilter(category, category)
    
    def distanceFromUpperLimit(self) -> Tuple[float, float]:
        if (not modelParameters.INCLUDE_END_CONSTRAINTS):
            return 0
        
        limitPos = (self.desiredX+modelParameters.END_LIMIT_UPPER_X, self.cells[-1].yNominal+modelParameters.END_LIMIT_UPPER_Y)
        return tuple(np.subtract(self.upperConstraint.body.position, limitPos))
    
    def distanceFromLowerLimit(self) -> Tuple[float, float]:
        if (not modelParameters.INCLUDE_END_CONSTRAINTS):
            return 0
        
        limitPos = (self.desiredX+modelParameters.END_LIMIT_LOWER_X, self.cells[0].yNominal-modelParameters.END_LIMIT_LOWER_Y)
        return tuple(np.subtract(self.lowerConstraint.body.position, limitPos))

    def updatePosition(self) -> None:
        for cell in self.cells:
            cell.setStart(self.x, self.y)
            

class Module:
    def __init__(self, numBandos:int = modelParameters.MODULE_BANDO_COUNT, initialBandolierSpacing:int = 0) -> None:
        self.bandoliers:List[Bandolier] = []
        self.space:pymunk.Space = setupSpace()
        self.simulated = False

        for i in range(numBandos):
            xBandoOrigin = i*(abs(modelParameters.BANDO_CELL_X) + modelParameters.CELL_DIAMETER_CURRENT + 2*(abs(modelParameters.BANDO_X_MU)+3*modelParameters.BANDO_X_SIGMA) + initialBandolierSpacing)
            
            startingDistanceFromEndConstraint = 1 #mm 
            if (i != 0 and modelParameters.INCLUDE_END_CONSTRAINTS and xBandoOrigin < i*modelParameters.BANDO_DESIRED_SPACING+startingDistanceFromEndConstraint):
                xBandoOrigin = i*modelParameters.BANDO_DESIRED_SPACING+startingDistanceFromEndConstraint
            
            yBandoOrigin = 0

            if (i == 0):
                static = True
            else:
                static = False

            self.bandoliers.append(Bandolier(i, self.space, xBandoOrigin, yBandoOrigin, static))
    
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

        if modelParameters.INCLUDE_END_CONSTRAINTS:
            bottomMostY -= max(modelParameters.END_LIMIT_LOWER_Y, modelParameters.END_CONSTRAINT_LOWER_Y)
            topMostY += max(modelParameters.END_LIMIT_UPPER_Y, modelParameters.END_CONSTRAINT_UPPER_Y)

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