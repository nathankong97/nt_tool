import time
from typing import List, Dict, Optional
import pandas as pd


def timing(f):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = f(*args, **kwargs)
        end = time.time()
        print(f"{f.__name__} takes {end - start:.4f} seconds to run.")
        return result
    return wrapper


def export_to_csv(result: List[Dict], file_name: Optional[str] = "output.csv") -> None:
    df = pd.DataFrame(result)
    df.to_csv(file_name, index=False)
