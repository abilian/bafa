import shutil
from pathlib import Path
from time import sleep

import whisper

from .server_metrics import get_metrics
from .whisper_util import dump

DB_DIR = "data"


def collect_metrics():
    if Path(DB_DIR).exists():
        shutil.rmtree(DB_DIR)
    Path(DB_DIR).mkdir()

    metrics = get_metrics()

    for k in metrics.keys():
        db_name = Path(DB_DIR) / f"{k}.wsp"

        args = {
            "aggregationMethod": "average",
            "archiveList": [(10, 1440)],
            "path": db_name,
            "sparse": False,
            "useFallocate": False,
            "xFilesFactor": 0.5,
        }
        whisper.create(**args)

    counter = 0
    while True:
        metrics = get_metrics()

        for k, v in metrics.items():
            db_name = Path(DB_DIR) / f"{k}.wsp"

            whisper.update(db_name, v)

        sleep(10)
        counter += 1

        if counter > 6:
            for k in metrics.keys():
                db_name = Path(DB_DIR) / f"{k}.wsp"
                print(f"Dumping {db_name}...")
                dump(db_name)
                print()
            counter = 0


if __name__ == "__main__":
    collect_metrics()
