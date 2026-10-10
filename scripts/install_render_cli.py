"""Install the official Render CLI in the ignored project-local tools directory."""
import hashlib
import io
import json
import platform
import tarfile
import zipfile
import urllib.request
from pathlib import Path

root = Path(__file__).resolve().parent.parent
tools = root / '.deployment' / 'bin'
tools.mkdir(parents=True, exist_ok=True)
request = urllib.request.Request(
    'https://api.github.com/repos/render-oss/cli/releases/latest',
    headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'quantum-checker-setup'},
)
release = json.load(urllib.request.urlopen(request, timeout=30))
systems = ('darwin', 'macos') if platform.system() == 'Darwin' else ('linux',)
arch = 'arm64' if platform.machine() in ('arm64', 'aarch64') else 'amd64'
matches = [item for item in release['assets'] if any(system in item['name'].lower() for system in systems) and arch in item['name'].lower()]
if not matches:
    raise RuntimeError('No matching release asset: ' + ', '.join(item['name'] for item in release['assets']))
asset = matches[0]
payload = urllib.request.urlopen(asset['browser_download_url'], timeout=60).read()
digest = asset.get('digest')
if digest and digest.startswith('sha256:'):
    assert hashlib.sha256(payload).hexdigest() == digest.removeprefix('sha256:'), 'Checksum mismatch.'
if asset['name'].endswith('.zip'):
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        binaries = [archive.read(name) for name in archive.namelist() if not name.endswith('/')]
        payload = next(data for data in binaries if data[:4] in (b'\x7fELF', b'\xcf\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xca\xfe\xba\xbe'))
elif asset['name'].endswith('.tar.gz'):
    with tarfile.open(fileobj=io.BytesIO(payload)) as archive:
        member = next(item for item in archive.getmembers() if Path(item.name).name == 'render' and item.isfile())
        payload = archive.extractfile(member).read()
(tools / 'render').write_bytes(payload)
(tools / 'render').chmod(0o755)
print('Installed official Render CLI', release['tag_name'])
