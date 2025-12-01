# queue_client.py
from multiprocessing.managers import BaseManager
from typing import Iterable

from task import Task


class QueueClient:
    """Client générique qui se connecte au QueueManager."""

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 50000,
        authkey: bytes = b"upssitech",
    ) -> None:
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
            print(f"[Boss] envoi de la tâche {t.identifier} (size={t.size})")
            self.task_queue.put(t)

    def collect_results(self, n_tasks: int) -> list[Task]:
        """Récupère n_tasks Task complétées."""
        results: list[Task] = []
        for _ in range(n_tasks):
            task: Task = self.result_queue.get()
            print(
                f"[Boss] résultat reçu pour tâche {task.identifier} "
                f"(size={task.size}, time={task.time:.6f}s)"
            )
            results.append(task)
        return results


class Minion(QueueClient):
    """Boucle de travail : lit des Task, appelle work(), renvoie la Task.
    - Attente bloquante pour la première tâche
    - Puis arrêt si la queue reste vide un certain temps.
    """

    def work_loop(self) -> None:
        import queue as _queue  # pour l'exception Empty locale

        IDLE_TIMEOUT = 1.0  # secondes max d'attente après la première tâche

        # --- Phase 1 : on attend la première tâche (bloquant) ---
        print("[Minion] en attente de la première tâche...")
        first_task = self.task_queue.get()  # attente infinie
        print(
            f"[Minion] première tâche reçue : {first_task.identifier} "
            f"(size={first_task.size})"
        )
        first_task.work()
        self.result_queue.put(first_task)

        # --- Phase 2 : on continue tant qu'il y a du travail ---
        while True:
            try:
                task = self.task_queue.get(timeout=IDLE_TIMEOUT)
            except _queue.Empty:
                # plus de nouvelle tâche pendant IDLE_TIMEOUT
                print("[Minion] queue vide, je m'arrête.")
                break

            print(
                f"[Minion] exécution de la tâche {task.identifier} (size={task.size})"
            )
            task.work()
            self.result_queue.put(task)
