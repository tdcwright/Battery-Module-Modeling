from tqdm import tqdm
import time

for i in tqdm(range(10), leave=False):
    time.sleep(1)