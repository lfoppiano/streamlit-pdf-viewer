from pathlib import Path

ROOT_DIRECTORY = Path(__file__).parent.parent.absolute()

import time

def wait_for_canvases(locator, timeout=10000, poll_interval=0.2, stable_checks=3):
    start = time.time()
    last_count = 0
    stable = 0
    while (time.time() - start) * 1000 < timeout:
        canvases = locator.all()
        count = len(canvases)
        if count == last_count:
            stable += 1
            if stable >= stable_checks:
                return canvases
        else:
            stable = 0
            last_count = count
        time.sleep(poll_interval)
    raise TimeoutError("Canvases did not finish loading in time")