import matplotlib.pyplot as plt
from matplotlib import animation

import pymunk
import pymunk.matplotlib_util

import components

def simulateModule(module:components.Module, displayFigure:bool=False, animateSimulation:bool=False, numberOfSimSteps:int=5000)->None:
    def init():
        module.space.debug_draw(drawOption)
        return []

    def animate(_):
        ax.clear()
        ax.set_xlim(figureXLim[0],figureXLim[1])
        ax.set_ylim(figureYLim[0],figureYLim[1])

        for x in range(stepsPerFrame):
            module.space.step(1 / 50 / 10 / 2)

        module.space.debug_draw(drawOption)
        

    if (displayFigure and animateSimulation):
    # module.displayModule()
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
        for x in range(numberOfSimSteps):
            module.space.step(1 / 50 / 10 / 2)

        if (displayFigure):
                
            module.displayModule()

    module.simulated = True


if __name__ == "__main__":
    m = components.Module(20,components.modelParameters.MODULE_BANDO_COUNT)
    # simulateModule(m,True, True)

    print(f"Width: {m.getTotalWidth():1.3f}mm")
    m.displayModule()