# manager.py
from multiprocessing.managers import BaseManager
import queue

_task_queue: "queue.Queue" = queue.Queue()
_result_queue: "queue.Queue" = queue.Queue()


class QueueManager(BaseManager):
    pass


QueueManager.register("get_task_queue", callable=lambda: _task_queue)
QueueManager.register("get_result_queue", callable=lambda: _result_queue)


def main(
    host: str = "127.0.0.1",
    port: int = 50000,
    authkey: bytes = b"upssitech",
) -> None:
    manager = QueueManager(address=(host, port), authkey=authkey)
    server = manager.get_server()
    print(f"[Manager] écoute sur {host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
