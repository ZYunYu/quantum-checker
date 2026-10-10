"""Run Django management commands against the project's Neon database."""
import json
import os
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
state = json.loads((root / '.deployment/cloud-state.json').read_text())
env = dict(os.environ, DATABASE_URL=state['database_url'])
if state.get('django_secret_key'):
    env.update(DJANGO_DEBUG='false', DJANGO_SECRET_KEY=state['django_secret_key'])
    env.update(BOOTSTRAP_ADMIN_USERNAME=state['admin_username'], BOOTSTRAP_ADMIN_PASSWORD=state['admin_password'])
raise SystemExit(subprocess.call([sys.executable, str(root / 'qgame/manage.py'), *sys.argv[1:]], env=env))
