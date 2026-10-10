"""Run Render CLI with credentials stored inside the ignored project directory."""
import os
import subprocess
import sys
from pathlib import Path
root = Path(__file__).resolve().parent.parent
env = dict(os.environ, RENDER_CLI_CONFIG_DIR=str(root / '.deployment' / 'render-config'))
raise SystemExit(subprocess.call([str(root / '.deployment' / 'bin' / 'render'), *sys.argv[1:]], env=env))
