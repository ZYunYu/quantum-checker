"""Install GitHub's official CLI in the ignored project-local tools directory."""
import hashlib
import io
import json
import platform
import urllib.request
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parent.parent
tools = root / '.deployment' / 'bin'
tools.mkdir(parents=True, exist_ok=True)
request = urllib.request.Request(
    'https://api.github.com/repos/cli/cli/releases/latest',
    headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'quantum-checker-setup'},
)
release = json.load(urllib.request.urlopen(request, timeout=30))
arch = 'arm64' if platform.machine() in ('arm64', 'aarch64') else 'amd64'
asset = next(item for item in release['assets'] if 'macos' in item['name'].lower() and arch in item['name'].lower() and item['name'].endswith('.zip'))
payload = urllib.request.urlopen(asset['browser_download_url'], timeout=60).read()
digest = asset.get('digest')
if digest and digest.startswith('sha256:'):
    assert hashlib.sha256(payload).hexdigest() == digest.removeprefix('sha256:'), 'Checksum mismatch.'
with zipfile.ZipFile(io.BytesIO(payload)) as archive:
    name = next(name for name in archive.namelist() if name.endswith('/bin/gh'))
    (tools / 'gh').write_bytes(archive.read(name))
(tools / 'gh').chmod(0o755)
print('Installed official GitHub CLI', release['tag_name'])
