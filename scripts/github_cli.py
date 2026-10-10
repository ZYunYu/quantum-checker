"""Run GitHub CLI with project-local settings; --push-main pushes via its credential helper."""
import os
import shlex
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
env = dict(os.environ, GH_CONFIG_DIR=str(root / '.deployment' / 'github-config'))
binary = root / '.deployment' / 'bin' / 'gh'
if sys.argv[1:] == ['--push-main']:
    command = ['git', '-c', 'credential.helper=', '-c',
               f'credential.helper=!{shlex.quote(str(binary))} auth git-credential',
               'push', 'origin', 'master']
else:
    command = [str(binary), *sys.argv[1:]]
raise SystemExit(subprocess.call(command, env=env))
