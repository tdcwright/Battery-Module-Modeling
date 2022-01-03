###############
# simulation.py
# TOM WRIGHT 2021
###############

"""
This file can be run independantly.
Functions to simulate a single model. The simulation will continue until the final (rightmost) bandolier
is sufficiently stable (its max velocity is below a threshold for a certain number of steps). If the simulation
is stable, then it will cease. The simulation can also be run in animation mode to demonstrate how the
simulation/model works. The simulation will run on the input module. Analytics can then be run on the module to
determine the total width, bandolier positions, etc.
"""

import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np

from tqdm import tqdm

import pymunk
import pymunk.matplotlib_util

import components
import modelParameters

def simulateModule(module:components.Module, displayFigure:bool=False, animateSimulation:bool=False, numberOfSimSteps:int=-1,simulationTitle="",includeProgressBar=True, progressBarLeave=True)->bool:
    modelParams:modelParameters.ModelParams = module.modelParams
    stable = False

    def init():
        module.space.debug_draw(drawOption)
        return []

    def animate(_):
        ax.clear()
        ax.set_xlim(figureXLim[0],figureXLim[1])
        ax.set_ylim(figureYLim[0],figureYLim[1])

        for x in range(stepsPerFrame):
            module.space.step(0.001)

        module.space.debug_draw(drawOption)
        

    if (displayFigure and animateSimulation):
        if (numberOfSimSteps < 0):
            numberOfSimSteps = 5000

        leftMostX = min([cell.simXPos for cell in module.bandoliers[0].cells])
        rightMostX = max([cell.simXPos for cell in module.bandoliers[-1].cells])
        bottomMostY = min([bando.cells[0].simYPos for bando in module.bandoliers])
        topMostY = max([bando.cells[-1].simYPos for bando in module.bandoliers])
        figureXLim = (leftMostX-25, rightMostX+25)
        figureYLim = (bottomMostY-25, topMostY+25)
        
        stepsPerFrame = 10

        fig = plt.figure()
        ax = plt.axes(xlim=figureXLim, ylim=figureYLim)
        ax.set_aspect("equal")

        drawOption = pymunk.matplotlib_util.DrawOptions(ax)
        drawOption.flags = pymunk.SpaceDebugDrawOptions.DRAW_SHAPES | \
                            pymunk.SpaceDebugDrawOptions.DRAW_COLLISION_POINTS | \
                            (pymunk.SpaceDebugDrawOptions.DRAW_CONSTRAINTS if modelParameters.DISPLAY_CONSTRAINTS else 0)

        frames = numberOfSimSteps/stepsPerFrame
        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=int(frames), interval=10, blit=False, repeat=False)
        plt.show()
    else:
        finalBandoVelocities = []
        countInTreshold = 0

        stepDt = 0.001


        for x in tqdm(range(modelParameters.MODEL_MAX_STEPS if numberOfSimSteps < 0 else numberOfSimSteps), desc=simulationTitle, leave=progressBarLeave, unit="step", disable=(not includeProgressBar)):

            currVelocities = [x.velocity[0] for x in module.bandoliers[-1].cells]
            maxVelocity = max(np.absolute(currVelocities))
           
            finalBandoVelocities.append(currVelocities)

            if (numberOfSimSteps < 0):
                if (maxVelocity < modelParameters.MODEL_MIN_VELOCITY):
                    countInTreshold+=1
                else:
                    countInTreshold = 0
                
                
                if (countInTreshold >= modelParameters.MODEL_IN_VELOCITY_THRESHOLD_COUNT):
                    stable = True
                    break
            module.space.step(stepDt)


        if (displayFigure):
            
            stableString = "Stability Ignored" if numberOfSimSteps > 0 else str(stable)

            plt.figure()
            plt.title(f"Maximum Velocity of final Bando, Stable: {stableString}")
            plt.xlabel("Simulation Step Count")
            plt.ylabel("Maximum cell x velocity")
            plt.plot([max(x) for x in finalBandoVelocities])         
            

            module.displayModule()

    module.simulated = True

    return stable

def simulationAnalytics(module:components.Module, stable:bool):
    analytics = {
                    "stable":stable,
                    "totalModuleWidth":module.getTotalWidth(),
                    "bandoliers":[]
                }

    for bandolier in module.bandoliers:
        upperDistance = bandolier.distanceFromUpperLimit()
        lowerDistance = bandolier.distanceFromLowerLimit()
        bandoAnalysis = {
                            "upperDistanceX":upperDistance[0],
                            "upperDistanceY":upperDistance[1],
                            "lowerDistanceX":lowerDistance[0],
                            "lowerDistanceY":lowerDistance[1]
                        }

        analytics["bandoliers"].append(bandoAnalysis)

    return analytics

if __name__ == "__main__":
    m = components.Module()
    # simulateModule(m,True, True)
    simulateModule(m, True, False)

    for i,b in enumerate(m.bandoliers):
        print(f"Bandolier {i}\n\tUpper: {b.distanceFromUpperLimit()}\n\tLower: {b.distanceFromLowerLimit()}")

    print(f"Width: {m.getTotalWidth():1.3f}mm")