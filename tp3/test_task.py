from task import Task


def test_roundtrip_json() -> None:
    """Vérifie que to_json puis from_json redonnent une tâche égale."""
    t1 = Task(identifier=42)
    json_text = t1.to_json()
    t2 = Task.from_json(json_text)

    assert t1 == t2, "La tâche reconstruite devrait être égale à l'originale"


def test_tasks_with_different_id_are_not_equal() -> None:
    """Deux tâches avec des identifiants différents ne doivent pas être égales."""
    t1 = Task(identifier=1)
    json_text = t1.to_json()
    t2 = Task.from_json(json_text)

    # On change l'identifiant de la deuxième tâche
    t2.identifier = 2

    assert t1 != t2, (
        "Deux tâches avec des identifiants différents ne doivent pas être égales"
    )


if __name__ == "__main__":
    # Exécution manuelle des tests si on lance le fichier directement
    test_roundtrip_json()
    test_tasks_with_different_id_are_not_equal()
    print("Tous les tests de Task ont réussi ✅")
