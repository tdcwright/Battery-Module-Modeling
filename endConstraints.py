from dataclasses import dataclass, field
from typing import List, Tuple
import pymunk

import modelParameters


@dataclass
class EndConstraint:
    xNominal:float
    yNominalInner:float
    yNominalOuter:float
    xStart:float
    yStart:float
    space:pymunk.Space
    adjacentCellBodies:List[pymunk.Body]
    colour:Tuple[int, int, int, int] = field(default=(-1,-1,-1,-1))
    xThickness:float = 5 #mm
    static:bool=False
    modelParams:modelParameters.ModelParams = modelParameters.DEFAULT_PARAMETERS

    def __post_init__ (self) -> None:
        if (self.static):
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        else:
            momentOfInertia = 10
            self.body = pymunk.Body(10, momentOfInertia, body_type=pymunk.Body.DYNAMIC)
        
        self.body.position = (self.xStart+self.xNominal, self.yStart+self.yNominalOuter)

        xLimitFace = 0
        yLimitFace = 0

        self.shape = pymunk.Poly(self.body, [\
                                (xLimitFace, yLimitFace), \
                                (xLimitFace, yLimitFace+(self.yNominalInner-self.yNominalOuter)), \
                                (xLimitFace+self.xThickness, yLimitFace+(self.yNominalInner-self.yNominalOuter)), \
                                (xLimitFace+self.xThickness, yLimitFace), \
                                ])
        self.shape.elasticity = 1

        self.space.add(self.body, self.shape)

        if (min(self.colour) >= 0):
            self.shape.color = self.colour

        self.shape.filter = pymunk.ShapeFilter(categories=2, mask=2)

        for cellBody in self.adjacentCellBodies:
            joint1 = pymunk.PinJoint(cellBody,self.body)
            joint2 = pymunk.PinJoint(cellBody,self.body,anchor_b=(self.xThickness,(self.yNominalOuter-self.yNominalInner)))
            self.space.add(joint1, joint2)
            
    def setFilter(self, category:int, mask:int) -> None:
        self.shape.filter = pymunk.ShapeFilter(categories=category, mask=mask)
   

@dataclass
class EndLimit:
    xOffset:float
    xLimit:float
    yLimit:float
    isUpper:bool
    space:pymunk.Space
    colour:Tuple[int, int, int, int] = field(default=(-1,-1,-1,-1))
    height:float = 20 # mm high walls
    wallThickness:float = 5     #mm thick walls
    modelParams:modelParameters.ModelParams = modelParameters.DEFAULT_PARAMETERS

    def __post_init__ (self) -> None:

        xLim = self.xLimit + self.xOffset
        yInner = self.yLimit-self.height if self.isUpper else self.yLimit+self.height
        yOuter = self.yLimit

        self.body, self.shapes = self.createLimitBox(xLim, yInner, yOuter) # Upper Limit

    def createLimitBox(self, xPos:float, yPosInner:float, yPosOuter:float) -> Tuple[pymunk.Body, List[pymunk.Shape]]:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        shapes:List[pymunk.Shape] = []
        
        shapes.append(pymunk.Poly(body, [\
                                (xPos,yPosOuter), \
                                (xPos-self.wallThickness,yPosOuter), \
                                (xPos,yPosInner), \
                                (xPos-self.wallThickness,yPosInner), \
                                ]))

        if (self.modelParams.END_CONSTRAINT_INCLUDE_Y_CONSTRAINTS):  
            thickness = self.wallThickness if yPosOuter > yPosInner else -self.wallThickness
            shapes.append(pymunk.Poly(body, [\
                                    (xPos,yPosOuter), \
                                    (xPos+self.height,yPosOuter), \
                                    (xPos+self.height,yPosOuter+thickness), \
                                    (xPos,yPosOuter+thickness), \
                                    ]))

        self.space.add(body)
        
        if (min(self.colour) >= 0):
            for shape in shapes:
                shape.color = (self.colour[0]/2,self.colour[1]/2,self.colour[2]/2,self.colour[3]) # make colour darker

        for shape in shapes:
            self.space.add(shape)

            shape.filter = pymunk.ShapeFilter(categories=0,mask=0)

        return (body, shapes)

    def setFilter(self, category:int, mask:int) -> None:
        for shape in self.shapes:
            shape.filter = pymunk.ShapeFilter(categories=category, mask=mask)
