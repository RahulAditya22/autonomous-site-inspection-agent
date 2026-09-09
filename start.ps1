$ErrorActionPreference='Stop'
if(-not (Test-Path '.venv')) { python -m venv .venv }
.\.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
Start-Process powershell -ArgumentList '-NoExit','-Command','python backend\run.py'
Push-Location frontend
if(-not (Test-Path 'node_modules')) { npm install }
npm run dev
Pop-Location
