# task.py
from dataclasses import dataclass, field
import math
import time
import random


@dataclass
class Task:
    """Représente un travail à effectuer par un Minion."""

    identifier: int  # identifiant de la tâche
    size: int  # "taille" du travail (nb d'itérations)
    a: float  # paramètre a
    b: float  # paramètre b
    x: float = 0.0  # valeur initiale de x
    time: float = field(default=0.0, init=False)  # temps d'exécution

    def work(self):
        """
        Travail simulé : on applique plusieurs fois une fonction non triviale
        pour prendre un peu de temps (sin/cos).
        """
        start = time.perf_counter()

        x = self.x
        a = self.a
        b = self.b

        for _ in range(self.size):
            x = math.sin(a * x + b) + math.cos(b * x + a)

        end = time.perf_counter()
        self.time = end - start
        self.x = x  # on mémorise le résultat final

        # On retourne quelque chose d'exploitable par le Boss
        return {
            "id": self.identifier,
            "x_final": self.x,
            "time": self.time,
        }


def random_task(identifier: int, size_min=50_000, size_max=200_000) -> Task:
    """Petit helper pour générer une tâche aléatoire."""
    size = random.randint(size_min, size_max)
    a = random.uniform(-2.0, 2.0)
    b = random.uniform(-2.0, 2.0)
    x0 = random.uniform(-1.0, 1.0)
    return Task(identifier=identifier, size=size, a=a, b=b, x=x0)
