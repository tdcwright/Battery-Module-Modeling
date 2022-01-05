###############
# multiModel.py
# TOM WRIGHT 2021
###############

"""
This file can be run independantly.
Very similar to model.py, however allows for the simulation of multiple variations of module design in a single
run to allow for iterative design. Before running this file, enter the design range of the parameters in the 
function 'varyModelInputs()'. Functions simulate each design input model multiple times. Allows for the
monte-carlo simulation where a new module (with its cell positioning tolerances) is created each iteration.
All results from this program are entered into the file results.txt. This program uses multiprocessing, so
it may slow down your computer and fill up RAM while it is running. I recommend closing most other apps before use.
"""

import numpy as np
import itertools
from typing import Any, Dict

import csv

from multiprocessing import Pool, Lock
from tqdm import tqdm

import modelParameters
from components import Module
from simulation import simulateModule, simulationAnalytics

RESULTS_FILE_NAME = "results.csv"

def worker(modelInputs:Dict[str,Any]) -> bool:
    currParams = modelParameters.ModelParams(**modelInputs)
    newModule = Module(modelParams=currParams)
    stable = simulateModule(newModule,includeProgressBar=False)

    # get resultDict
    analytics = simulationAnalytics(newModule, stable)
    results = list(modelInputs.items())
    results.extend(filter(lambda x: (x[0]!="bandoliers"), analytics.items()))
    for i, bando in enumerate(analytics["bandoliers"]):
        results.extend([(f"Bando{i+1}_{key}", value) for key,value in bando.items() ])
    
    results=dict(results)
    fieldNames = list(results.keys())
    
    with Lock():
        with open(RESULTS_FILE_NAME, 'a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldNames)

            writer.writerow(results)

    # print("Stable result\r" if stable else "Unstable result")

    return stable

def product_dict(**kwargs):
    keys = kwargs.keys()
    vals = kwargs.values()
    for instance in itertools.product(*vals):
        yield dict(zip(keys, instance))

# Range of values
def r(lowerBound:float,upperBound:float, numIntervals:int):
    return np.unique(np.linspace(lowerBound, upperBound, numIntervals))

# See modelParameters.py file for variable desctiptions
# Uses np.linspace(x,y,z) where x is the lower bound, y is the upper bound, and z is the number of steps between
# Eg: np.linspace(0,1,11) = [ 0. ,  0.1,  0.2,  0.3,  0.4,  0.5,  0.6,  0.7,  0.8,  0.9,  1. ]
def varyModelInputs():
    BANDO_CELL_X:float = r(modelParameters.BANDO_CELL_X, modelParameters.BANDO_CELL_X+0, 1) 
    BANDO_CELL_Y1:float = r(modelParameters.BANDO_CELL_Y1, modelParameters.BANDO_CELL_Y1+0, 1) 
    BANDO_CELL_Y2:float = r(modelParameters.BANDO_CELL_Y2, modelParameters.BANDO_CELL_Y2+0, 1) 
    BANDO_X_MU:float = r(modelParameters.BANDO_X_MU, modelParameters.BANDO_X_MU+0, 1) 
    BANDO_X_SIGMA:float = r(modelParameters.BANDO_X_SIGMA, modelParameters.BANDO_X_SIGMA+0, 1) 
    BANDO_Y_MU:float = r(modelParameters.BANDO_Y_MU, modelParameters.BANDO_Y_MU+0, 1) 
    BANDO_Y_SIGMA:float = r(modelParameters.BANDO_Y_SIGMA, modelParameters.BANDO_Y_SIGMA+0, 1) 
    CELL_DIAMETER_CURRENT:float = r(modelParameters.CELL_DIAMETER_CURRENT, modelParameters.CELL_DIAMETER_CURRENT+0, 1) 
    CELL_DIAMETER_MU:float = r(modelParameters.CELL_DIAMETER_MU, modelParameters.CELL_DIAMETER_MU+0, 1) 
    CELL_DIAMETER_SIGMA:float = r(modelParameters.CELL_DIAMETER_SIGMA, modelParameters.CELL_DIAMETER_SIGMA+0, 1) 
    BANDO_DESIRED_SPACING:float = r(modelParameters.BANDO_DESIRED_SPACING, modelParameters.BANDO_DESIRED_SPACING+0, 1) 
    INCLUDE_END_CONSTRAINTS:bool = [True] # [True, False]
    END_CONSTRAINT_LOWER_X:float = r(modelParameters.END_CONSTRAINT_LOWER_X, modelParameters.END_CONSTRAINT_LOWER_X+0, 1) 
    END_CONSTRAINT_UPPER_X:float = r(modelParameters.END_CONSTRAINT_UPPER_X, modelParameters.END_CONSTRAINT_UPPER_X+0, 1) 
    END_CONSTRAINT_LOWER_Y:float = r(modelParameters.END_CONSTRAINT_LOWER_Y, modelParameters.END_CONSTRAINT_LOWER_Y+0, 1) 
    END_CONSTRAINT_UPPER_Y:float = r(modelParameters.END_CONSTRAINT_UPPER_Y, modelParameters.END_CONSTRAINT_UPPER_Y+0, 1)


    return list(product_dict(BANDO_CELL_X = BANDO_CELL_X,
                            BANDO_CELL_Y1 = BANDO_CELL_Y1,
                            BANDO_CELL_Y2 = BANDO_CELL_Y2,
                            BANDO_X_MU = BANDO_X_MU,
                            BANDO_X_SIGMA = BANDO_X_SIGMA,
                            BANDO_Y_MU = BANDO_Y_MU,
                            BANDO_Y_SIGMA = BANDO_Y_SIGMA,
                            CELL_DIAMETER_CURRENT = CELL_DIAMETER_CURRENT,
                            CELL_DIAMETER_MU = CELL_DIAMETER_MU,
                            CELL_DIAMETER_SIGMA = CELL_DIAMETER_SIGMA,
                            BANDO_DESIRED_SPACING = BANDO_DESIRED_SPACING,
                            INCLUDE_END_CONSTRAINTS = INCLUDE_END_CONSTRAINTS,
                            END_CONSTRAINT_LOWER_X = END_CONSTRAINT_LOWER_X,
                            END_CONSTRAINT_UPPER_X = END_CONSTRAINT_UPPER_X,
                            END_CONSTRAINT_LOWER_Y = END_CONSTRAINT_LOWER_Y,
                            END_CONSTRAINT_UPPER_Y = END_CONSTRAINT_UPPER_Y))

def runMultiModel(numIterations:int, displayResults:bool=True):
    pool = Pool()

    inputList = varyModelInputs()

    fieldNames = list(inputList[0].keys())
    fieldNames.extend(["stable", "totalModuleWidth"])
    [fieldNames.append(f"Bando{i+1}_{key}") for i in range(modelParameters.MODULE_BANDO_COUNT) for key in ["upperDistanceX", "upperDistanceY", "lowerDistanceX", "lowerDistanceY"]]
    with Lock():
        with open(RESULTS_FILE_NAME, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldNames)
            writer.writeheader()

    results = list(tqdm(pool.imap_unordered(worker, 
                                        [modelInput for modelInput in inputList for _ in range(numIterations)]),
                    total=len(inputList)*numIterations,
                    unit="Iteration", 
                    desc="MultiModel",
                    disable=False))
        
    numStable = results.count(True)
    
    print(f"Number of stable iterations: {numStable}")
            

if __name__ == "__main__":
    runMultiModel(modelParameters.MODEL_NUM_ITERATIONS)

