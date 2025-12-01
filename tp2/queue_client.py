# queue_client.py
from multiprocessing.managers import BaseManager
from typing import Iterable

import queue  # <--- important
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
    S'arrête automatiquement s'il n'a plus de tâches pendant un certain temps.
    """

    def work_loop(self) -> None:
        IDLE_TIMEOUT = 2.0  # secondes max d'attente sur une tâche
        MAX_IDLE_CYCLES = 3  # nombre de timeouts consécutifs avant arrêt

        idle_cycles = 0

        while True:
            try:
                # on attend une tâche au max IDLE_TIMEOUT secondes
                task = self.task_queue.get(timeout=IDLE_TIMEOUT)
            except queue.Empty:
                idle_cycles += 1
                print(
                    f"[Minion] aucune tâche reçue (idle {idle_cycles}/{MAX_IDLE_CYCLES})"
                )
                if idle_cycles >= MAX_IDLE_CYCLES:
                    print("[Minion] plus de tâches depuis un moment, je m'arrête.")
                    break
                continue  # on retente un get()

            # on a bien reçu une tâche : on reset le compteur d'inactivité
            idle_cycles = 0

            print(
                f"[Minion] exécution de la tâche {task.identifier} (size={task.size})"
            )
            task.work()
            self.result_queue.put(task)
