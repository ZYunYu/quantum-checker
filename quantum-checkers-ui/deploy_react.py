"""Build the React app and collect static assets for Django."""
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
subprocess.run(['npm', 'run', 'build'], cwd=root / 'quantum-checkers-ui', check=True)
subprocess.run([sys.executable, str(root / 'qgame' / 'manage.py'), 'collectstatic', '--noinput'], check=True)
