from pathlib import Path
for p in ['data/demo','data/knowledge','backend/uploads','backend/logs']: Path(p).mkdir(parents=True,exist_ok=True)
print('AegisFleet directories ready.')
