"""Verify classroom administration and student registration in a real browser."""
import json
import os
import secrets
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parent.parent
credentials_file = Path(os.environ.get('ADMIN_CREDENTIALS_FILE', str(root / '.deployment/local-admin.json')))
credentials = json.loads(credentials_file.read_text())
base = os.environ.get('PREVIEW_URL', 'http://127.0.0.1:8001')
suffix = secrets.token_hex(5)
username = 'browser-student-' + suffix
student_id = 'D00' + str(secrets.randbelow(10**12))
class_name = 'Browser Test Class ' + suffix
password = secrets.token_urlsafe(24)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', headless=True)
    page = browser.new_page(viewport={'width': 1200, 'height': 1000})
    page.goto(base + '/admin/login/')
    page.get_by_label('Username:', exact=True).fill(credentials['username'])
    page.get_by_label('Password:', exact=True).fill(credentials['password'])
    page.get_by_role('button', name='Log in').click()
    expect(page.get_by_role('link', name='Classrooms', exact=True).first).to_be_visible()
    expect(page.get_by_role('link', name='Student profiles', exact=True).first).to_be_visible()
    expect(page.get_by_role('link', name='Read the administrator guide')).to_be_visible()
    for name in ('admin-guide', 'user-guide'):
        guide = page.request.get(base + '/guides/' + name + '.html')
        assert guide.status == 200 and '<html lang="en">' in guide.text()
        pdf = page.request.get(base + '/guides/' + name + '.pdf')
        assert pdf.status == 200 and pdf.body().startswith(b'%PDF-')
    page.goto(base + '/admin/game/classroom/add/')
    page.get_by_label('Classroom name:').fill(class_name)
    page.get_by_role('button', name='Save', exact=True).click()
    expect(page.locator('.success')).to_be_visible()
    student = browser.new_page()
    student.goto(base + '/signup')
    student.get_by_label('Username', exact=True).fill(username)
    student.get_by_label('Student ID', exact=True).fill(student_id)
    student.get_by_label('Classroom (optional)').select_option(label=class_name)
    student.get_by_label('Password', exact=True).fill(password)
    student.get_by_label('Student ID', exact=True).fill('d12345')
    student.get_by_role('button', name='Sign up', exact=True).click()
    expect(student.get_by_role('heading', name='Create an account')).to_be_visible()
    assert not student.get_by_label('Student ID', exact=True).evaluate('(element) => element.validity.valid')
    student.get_by_label('Student ID', exact=True).fill(student_id)
    assert student.get_by_label('Student ID', exact=True).evaluate('(element) => element.validity.valid')
    student.screenshot(path=str(root / '.deployment/preview-signup.png'), full_page=True)
    student.get_by_role('button', name='Sign up', exact=True).click()
    expect(student.get_by_role('heading', name='Log in')).to_be_visible()
    student.get_by_label('Username', exact=True).fill(username)
    student.get_by_label('Password', exact=True).fill(password)
    student.get_by_role('button', name='Log in', exact=True).click()
    expect(student.get_by_role('button', name='Log out')).to_be_visible()
    details = student.request.get(base + '/api/session/').json()
    assert details['studentId'] == student_id
    assert details['classroom']['name'] == class_name
    page.goto(base + '/admin/game/userprofile/?q=' + student_id)
    page.get_by_role('link', name=username, exact=True).click()
    expect(page.get_by_label('Student ID:', exact=True)).to_have_value(student_id)
    expect(page.get_by_label('Classroom:', exact=True)).to_have_value(str(details['classroom']['id']))
    page.get_by_label('Student ID:', exact=True).fill(student_id + '1')
    page.get_by_role('button', name='Save and continue editing').click()
    expect(page.locator('.success')).to_be_visible()
    assert student.request.get(base + '/api/session/').json()['studentId'] == student_id + '1'
    page.screenshot(path=str(root / '.deployment/preview-student-admin.png'), full_page=True)
    browser.close()

# Remove only the synthetic records created by this run.
import sys
sys.path.insert(0, str(root / 'qgame'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qgame.settings')
import django
django.setup()
from django.contrib.auth.models import User
from game.models import Classroom
User.objects.filter(username=username).delete()
Classroom.objects.filter(name=class_name).delete()
print('Browser checks passed: English classroom/profile forms, invalid ID rejected, class selected during signup, D-prefixed ID preserved, student details edited.')
