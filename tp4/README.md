# Lancer les composants (ordre obligatoire)

Ouvrir 4 terminaux dans le dossier tp4/.

## Terminal 1 — Manager
```bash
python manager.py
```

## Terminal 2 — Proxy HTTP
```bash
python proxy.py
```

## Terminal 3 — Boss (envoi des tâches)
```bash
python run_boss.py
```

## Terminal 4 — Client C++
Compilation (une seule fois)
```bash
cmake -B build -S .
cmake --build build
```

Exécution
```bash
./build/low_level --n 5
```

# Arrêt

run_boss.py et low_level se terminent automatiquement

arrêter manager.py et proxy.py avec Ctrl+C
