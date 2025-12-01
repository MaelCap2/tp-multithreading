# run_minion.py
from queue_client import Minion


if __name__ == "__main__":
    m = Minion()
    m.work_loop()
