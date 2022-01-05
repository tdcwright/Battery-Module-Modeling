###############
# model.py
# TOM WRIGHT 2021
###############

"""
This file can be run independantly.
Functions to simulate a model multiple times. This is the monte-carlo simulation where a new module (with its
cell positioning tolerances) is created each iteration. Since some simulations do not reach stability, they
can be included or ignored as set in modelParameters.py. This program uses multiprocessing, so it may slow down
your computer and fill up RAM while it is running. I recommend closing most other apps before use.
"""

from multiprocessing import Pool
from tqdm import tqdm

from typing import Any, Dict, Tuple, List

from simulation import simulateModule, simulationAnalytics
from components import Module
import modelParameters
import matplotlib.pyplot as plt

def worker(iteration) -> Tuple[Module, Dict[str, Any]]:
    newModule = Module()
    stable = simulateModule(newModule,includeProgressBar=False)

    # print("Stable result\r" if stable else "Unstable result")

    return (newModule, simulationAnalytics(newModule, stable))


def showHistogram(results:List[Tuple[Module, Dict[str, Any]]]) -> None:
    widths = [x[1]["totalModuleWidth"] for x in results]

    # q25, q75 = np.percentile(widths, [25, 75])
    # bin_width = 2 * (q75 - q25) * len(widths) ** (-1/3)
    # bins = round((max(widths) - min(widths)) / bin_width)

    fig = plt.figure()
    # plt.hist(widths, density=True, bins=bins)  # density=False would make counts    

    plt.hist(widths, density=True)
    plt.ylabel('Probability')
    plt.xlabel('Data')


def runSimulation(numIterations:int, displayResults:bool=True) -> List[Tuple[Module, float, bool]]:    
    pool = Pool()

    results:List[Tuple[Module, float, bool]] = list(tqdm(pool.imap_unordered(worker, 
                                                                            range(numIterations)),
                                                        total=numIterations,
                                                        unit="Iteration", 
                                                        desc="Model"))

    if (modelParameters.DISCARD_UNSTABLE_RESULTS):
        results = list(filter(lambda x: (x[1]["stable"]), results))
    
        print(f"Number of stable iterations: {len(results)}")
    

    largest = max(results, key=lambda x: x[1]["totalModuleWidth"])
    smallest = min(results, key=lambda x: x[1]["totalModuleWidth"])

    if (displayResults):
        largest[0].displayModule(f"Largest: {largest[1]}mm", False)
        smallest[0].displayModule(f"Smallest {smallest[1]}mm", False)

        showHistogram(results)
    
    return results



if __name__ == "__main__":
    runSimulation(modelParameters.MODEL_NUM_ITERATIONS, True)
    plt.show()