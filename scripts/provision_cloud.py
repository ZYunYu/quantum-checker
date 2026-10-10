"""Provision only Free Neon/Render resources; keep secrets in .deployment.

Usage: python scripts/provision_cloud.py database|service|status
"""
import json
import os
import secrets
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
folder = root / '.deployment'
folder.mkdir(exist_ok=True)
state_file = folder / 'cloud-state.json'
state = json.loads(state_file.read_text()) if state_file.exists() else {}
env = dict(os.environ, RENDER_CLI_CONFIG_DIR=str(folder / 'render-config'))
neon = [str(folder / 'tools/node_modules/.bin/neon'), '--config-dir', str(folder / 'neon-config'), '--no-analytics', '-o', 'json']
render = [str(folder / 'bin/render')]


def save():
    state_file.write_text(json.dumps(state, indent=2))
    state_file.chmod(0o600)


def run(command):
    result = subprocess.run(command, capture_output=True, text=True, env=env, timeout=120)
    if result.returncode:
        message = result.stderr.strip() or 'Cloud command failed.'
        for value in state.values():
            if isinstance(value, str) and len(value) > 16:
                message = message.replace(value, '[redacted]')
        raise RuntimeError(message)
    return result.stdout.strip()


def database():
    orgs = json.loads(run(neon + ['orgs', 'list']))
    free_orgs = [org for org in orgs if org['plan'] == 'free']
    if len(free_orgs) != 1:
        raise RuntimeError('Choose a single Free Neon organization before provisioning.')
    org_id = free_orgs[0]['id']
    if not state.get('neon_project_id'):
        projects = json.loads(run(neon + ['projects', 'list', '--org-id', org_id]))
        existing = [project for project in projects if project['name'] == 'quantum-checker']
        if existing:
            project = existing[0]
        else:
            response = json.loads(run(neon + [
                'projects', 'create', '--name', 'quantum-checker', '--org-id', org_id,
                '--region-id', 'aws-eu-central-1', '--pg-version', '17', '--cu', '0.25', '--no-secrets',
            ]))
            project = response['project']
        state['neon_project_id'] = project['id']
        save()
    if not state.get('database_url'):
        state['database_url'] = run(neon + ['connection-string', '--project-id', state['neon_project_id'], '--pooled'])
        assert state['database_url'].startswith('postgresql://')
        save()
    print('Neon Free database ready:', state['neon_project_id'])
    print('Database credentials saved locally; not printed or committed.')


def service():
    if not state.get('database_url'):
        raise RuntimeError('Run the database step first.')
    if not state.get('admin_password'):
        state.update(admin_username='admin', admin_password=secrets.token_urlsafe(30), django_secret_key=secrets.token_urlsafe(64))
        save()
        account_file = folder / 'production-admin.json'
        account_file.write_text(json.dumps({'username': state['admin_username'], 'password': state['admin_password']}, indent=2))
        account_file.chmod(0o600)
    if not state.get('render_service_id'):
        variables = {
            'DJANGO_DEBUG': 'false', 'DJANGO_SECRET_KEY': state['django_secret_key'],
            'DATABASE_URL': state['database_url'], 'BOOTSTRAP_ADMIN_USERNAME': state['admin_username'],
            'BOOTSTRAP_ADMIN_PASSWORD': state['admin_password'],
        }
        command = render + [
            'services', 'create', '--name', 'quantum-checker', '--type', 'web_service',
            '--repo', 'https://github.com/ZYunYu/quantum-checker', '--branch', 'master',
            '--runtime', 'docker', '--region', 'frankfurt', '--plan', 'free',
            '--num-instances', '1', '--health-check-path', '/healthz/', '-o', 'json', '--confirm',
        ]
        for key, value in variables.items():
            command.extend(['--env-var', f'{key}={value}'])
        response = json.loads(run(command))
        item = response.get('service', response)
        state['render_service_id'] = item['id']
        state['render_url'] = item.get('serviceDetails', {}).get('url', '')
        save()
    print('Render Free service created:', state['render_service_id'])
    if state.get('render_url'):
        print('Website:', state['render_url'])
    print('Initial admin credentials saved in .deployment/production-admin.json')


def status():
    if not state.get('render_service_id'):
        raise RuntimeError('The web service has not been created yet.')
    deployments = json.loads(run(render + ['deploys', 'list', state['render_service_id'], '-o', 'json']))
    if isinstance(deployments, list):
        for entry in deployments[:3]:
            deploy = entry.get('deploy', entry)
            print('Deployment:', deploy.get('id'), 'Status:', deploy.get('status'))
    else:
        print('Deployment metadata keys:', ', '.join(deployments))


if __name__ == '__main__':
    action = {'database': database, 'service': service, 'status': status}.get(sys.argv[1] if len(sys.argv) > 1 else '')
    if not action:
        raise SystemExit('Usage: provision_cloud.py database|service|status')
    try:
        action()
    except Exception as exc:
        raise SystemExit(str(exc))
