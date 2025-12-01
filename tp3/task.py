import time
import json

import numpy as np


class Task:
    def __init__(self, identifier: int = 0, size: int | None = None):
        self.identifier = identifier
        # choosee the size of the problem
        self.size = size or np.random.randint(300, 3_000)
        # Generate the input of the problem
        self.a = np.random.rand(self.size, self.size)
        self.b = np.random.rand(self.size)
        # prepare room for the results
        self.x = np.zeros((self.size))
        self.time = 0.0

    def work(self) -> None:
        start = time.perf_counter()
        self.x = np.linalg.solve(self.a, self.b)
        self.time = time.perf_counter() - start

    # ===========================
    #   Sérialisation JSON
    # ===========================
    def to_json(self) -> str:
        """Sérialise la tâche en chaîne JSON (types natifs Python seulement)."""
        data = {
            "identifier": self.identifier,
            "size": self.size,
            "a": self.a.tolist(),  # numpy -> liste de listes
            "b": self.b.tolist(),
            "x": self.x.tolist(),
            "time": self.time,
        }
        return json.dumps(data)

    @staticmethod
    def from_json(text: str) -> "Task":
        """Reconstruit une Task à partir d'une chaîne JSON produite par to_json."""
        data = json.loads(text)

        # On crée une Task "normale"
        t = Task(identifier=data["identifier"], size=data["size"])

        # Puis on remplace les champs aléatoires par ceux du JSON
        t.a = np.array(data["a"], dtype=float)
        t.b = np.array(data["b"], dtype=float)
        t.x = np.array(data["x"], dtype=float)
        t.time = float(data["time"])

        return t

    # ===========================
    #   Égalité entre tâches
    # ===========================
    def __eq__(self, other: object) -> bool:
        """Deux tâches sont égales si tous leurs attributs sont égaux."""
        if not isinstance(other, Task):
            return NotImplemented

        same_id = self.identifier == other.identifier
        same_size = self.size == other.size
        same_time = np.isclose(self.time, other.time)

        same_a = np.array_equal(self.a, other.a)
        same_b = np.array_equal(self.b, other.b)
        same_x = np.array_equal(self.x, other.x)

        return same_id and same_size and same_time and same_a and same_b and same_x
