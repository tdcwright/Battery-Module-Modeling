from multiprocessing import Pool
from typing import Tuple
import numpy as np

from simulation import simulateModule
from components import Module
import modelParameters
import matplotlib.pyplot as plt

def worker(_) -> Tuple[Module, float]:
    newModule = Module()
    simulateModule(newModule)
    return (newModule, newModule.getTotalWidth())


def showHistogram(results):
    widths = [x[1] for x in results]

    # q25, q75 = np.percentile(widths, [25, 75])
    # bin_width = 2 * (q75 - q25) * len(widths) ** (-1/3)
    # bins = round((max(widths) - min(widths)) / bin_width)

    fig = plt.figure()
    # plt.hist(widths, density=True, bins=bins)  # density=False would make counts
    plt.hist(widths)
    plt.ylabel('Probability')
    plt.xlabel('Data')


def runSimulation(numIterations:int, displayResults:bool=True):    
    pool = Pool()
    results = pool.map(worker, range(numIterations))

    largest = max(results, key=lambda x: x[1])
    smallest = min(results, key=lambda x: x[1])

    if (displayResults):
        largest[0].displayModule(f"Largest: {largest[1]}mm", False)
        smallest[0].displayModule(f"Smallest {smallest[1]}mm", False)

        showHistogram(results)



if __name__ == "__main__":
    runSimulation(modelParameters.MODEL_NUM_ITERATIONS, True)
    plt.show()