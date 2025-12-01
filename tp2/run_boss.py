# run_boss.py
from queue_client import Boss
from task import random_task


if __name__ == "__main__":
    boss = Boss()

    # Création de 5 tâches aléatoires
    tasks = [random_task(i) for i in range(5)]
    boss.submit_tasks(tasks)

    results = boss.collect_results(len(tasks))
    boss.send_stop(n_minions=1)  # adapter au nb de Minions lancés

    print("\n=== Résultats ===")
    for r in results:
        print(f"Task {r['id']}: x_final={r['x_final']:.4f}, time={r['time']:.4f}s")
