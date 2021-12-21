import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np

import pymunk
import pymunk.matplotlib_util

import components
import modelParameters

def simulateModule(module:components.Module, displayFigure:bool=False, animateSimulation:bool=False, numberOfSimSteps:int=-1)->bool:
    
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

        frames = numberOfSimSteps/stepsPerFrame
        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=int(frames), interval=10, blit=False, repeat=False)
        plt.show()
    else:
        finalBandoVelocities = []
        countInTreshold = 0

        for x in range(modelParameters.MODEL_MAX_STEPS if numberOfSimSteps < 0 else numberOfSimSteps):

            currVelocities = [x.velocity[0] for x in module.bandoliers[-1].cells]
            finalBandoVelocities.append(currVelocities)

            if (numberOfSimSteps < 0):
                if (max(np.absolute(currVelocities)) < modelParameters.MODEL_MIN_VELOCITY):
                    countInTreshold+=1
                else:
                    countInTreshold = 0
                
                
                if (countInTreshold >= modelParameters.MODEL_IN_VELOCITY_THRESHOLD_COUNT):
                    stable = True
                    break
            module.space.step(0.001)


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


if __name__ == "__main__":
    m = components.Module(modelParameters.MODULE_BANDO_COUNT)
    # simulateModule(m,True, True)
    simulateModule(m, True, False)

    print(f"Width: {m.getTotalWidth():1.3f}mm")