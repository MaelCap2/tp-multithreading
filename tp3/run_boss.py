# run_boss.py
from queue_client import Boss
from task import Task


def main() -> None:
    boss = Boss()

    n_tasks = 5
    tasks = [Task(identifier=i) for i in range(n_tasks)]

    boss.submit_tasks(tasks)
    results = boss.collect_results(n_tasks)

    print("\n=== Résumé des résultats ===")
    for t in results:
        print(f"Tâche {t.identifier} : size={t.size}, temps={t.time:.6f}s")


if __name__ == "__main__":
    main()
