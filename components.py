from typing import List
import pymunk
from dataclasses import dataclass
import modelParameters
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
    cellMass = 10 # pymunk variable, ignore

    def __post_init__(self) -> None:
        
        if (self.static):
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            momentOfInertia = 10#pymunk.moment_for_circle(self.cellMass, 0, self.cellDiameter/2)
            self.body = pymunk.Body(self.cellMass, momentOfInertia, body_type=pymunk.Body.DYNAMIC)
                   
        self.body.position = (self.xPosition, self.yPosition)
        shape = pymunk.Circle(self.body,self.cellDiameter/2)
        shape.elasticity = 1
        
        self.space.add(self.body, shape)
    
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



@dataclass
class Bandolier:
    id: int
    space:pymunk.space
    x: float = 0
    y: float = 0
    static:bool = False

    def __post_init__(self) -> None:
        self.createCells()

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
            
            newCell = Cell(i, xTolerances[i],yTolerances[i],xPos,yPos,self.x,self.y,self.space,diameterTolerances[i],self.static)

            self.cells.append(newCell)
    
    def constrainCells(self) -> None:
        for i in range(modelParameters.BANDO_CELL_COUNT-1):
            joint1 = pymunk.PinJoint(self.cells[i].body,self.cells[i+1].body)

            self.space.add(joint1)
            if i != modelParameters.BANDO_CELL_COUNT-2:
                joint2 = pymunk.PinJoint(self.cells[i].body,self.cells[i+2].body)
                self.space.add(joint2)
    
    def updatePosition(self) -> None:
        for cell in self.cells:
            cell.setStart(self.x, self.y)
            

class Module:
    def __init__(self, numBandos = modelParameters.MODULE_BANDO_COUNT, initialBandolierSpacing = 0) -> None:
        self.bandoliers:List[Bandolier] = []
        self.space:pymunk.Space = setupSpace()
        self.simulated = False

        for i in range(numBandos):
            xBandoOrigin = i*(abs(modelParameters.BANDO_CELL_X) + modelParameters.CELL_DIAMETER_CURRENT + 2*(abs(modelParameters.BANDO_X_MU)+3*modelParameters.BANDO_X_SIGMA) + initialBandolierSpacing)
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
        figureXLim = (leftMostX-25, rightMostX+25)
        figureYLim = (bottomMostY-25, topMostY+25)
        
        fig = plt.figure()
        ax = plt.axes(xlim=figureXLim, ylim=figureYLim)
        plt.title(title)
        ax.set_aspect("equal")

        drawOption = pymunk.matplotlib_util.DrawOptions(ax)
        self.space.debug_draw(drawOption)
        
        if (blocking):
            plt.show()



if __name__ == "__main__":
    pass