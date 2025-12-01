# queue_client.py
from multiprocessing.managers import BaseManager
from typing import Iterable, Any

from task import Task


class QueueClient:
    """Client générique qui se connecte au QueueManager."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 50000,
        authkey: bytes = b"upssitech",
    ) -> None:
        # Déclaration d'un Manager client (sans callable)
        class _QueueManager(BaseManager):
            pass

        _QueueManager.register("get_task_queue")
        _QueueManager.register("get_result_queue")

        self._manager = _QueueManager(address=(host, port), authkey=authkey)
        print(f"[Client] connexion à {host}:{port}…")
        self._manager.connect()
        print("[Client] connecté ✅")

        self.task_queue = self._manager.get_task_queue()
        self.result_queue = self._manager.get_result_queue()


class Boss(QueueClient):
    """Envoie des tâches et récupère les résultats."""

    def submit_tasks(self, tasks: Iterable[Task]) -> None:
        for t in tasks:
            print(f"[Boss] envoi de la tâche {t.identifier}")
            self.task_queue.put(t)

    def send_stop(self, n_minions: int) -> None:
        """Envoie des sentinelles None pour arrêter les Minions."""
        for _ in range(n_minions):
            self.task_queue.put(None)

    def collect_results(self, n_tasks: int) -> list[dict[str, Any]]:
        """Récupère n_tasks résultats (dictionnaires renvoyés par Task.work)."""
        results: list[dict[str, Any]] = []
        for _ in range(n_tasks):
            res = self.result_queue.get()
            print(f"[Boss] résultat reçu pour tâche {res['id']}")
            results.append(res)
        return results


class Minion(QueueClient):
    """Boucle de travail : lit des Task, appelle work(), renvoie le résultat."""

    def work_loop(self) -> None:
        while True:
            task = self.task_queue.get()
            if task is None:
                print("[Minion] arrêt demandé, je m'arrête.")
                break

            print(f"[Minion] exécution de la tâche {task.identifier}")
            result = task.work()
            self.result_queue.put(result)
