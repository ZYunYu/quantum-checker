"""Verify classroom administration and student registration in a real browser."""
import json
import os
import secrets
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parent.parent
credentials = json.loads((root / '.deployment/local-admin.json').read_text())
base = os.environ.get('PREVIEW_URL', 'http://127.0.0.1:8001')
suffix = secrets.token_hex(5)
username = 'browser-student-' + suffix
student_id = '00' + suffix
class_name = 'Browser Test Class ' + suffix
password = secrets.token_urlsafe(24)

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge', headless=True)
    page = browser.new_page(viewport={'width': 1200, 'height': 1000})
    page.goto(base + '/admin/login/')
    page.get_by_label('Username:', exact=True).fill(credentials['username'])
    page.get_by_label('Password:', exact=True).fill(credentials['password'])
    page.get_by_role('button', name='Log in').click()
    page.goto(base + '/admin/game/classroom/add/')
    page.get_by_label('班级名称:').fill(class_name)
    page.get_by_role('button', name='Save', exact=True).click()
    expect(page.locator('.success')).to_be_visible()
    student = browser.new_page()
    student.goto(base + '/signup')
    student.get_by_label('Username', exact=True).fill(username)
    student.get_by_label('Student ID / 学号').fill(student_id)
    student.get_by_label('Classroom / 班级 (optional)').select_option(label=class_name)
    student.get_by_label('Password', exact=True).fill(password)
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
    expect(page.get_by_label('学号:', exact=True)).to_have_value(student_id)
    expect(page.get_by_label('班级:', exact=True)).to_have_value(str(details['classroom']['id']))
    page.get_by_label('学号:', exact=True).fill(student_id + '-updated')
    page.get_by_role('button', name='Save and continue editing').click()
    expect(page.locator('.success')).to_be_visible()
    assert student.request.get(base + '/api/session/').json()['studentId'] == student_id + '-updated'
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
print('Browser checks passed: create classroom, select it during signup, preserve student ID, edit student details.')
