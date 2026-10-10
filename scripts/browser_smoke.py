"""Verify login, puzzle play, refresh, and the admin form in a real browser."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

root = Path(__file__).resolve().parent.parent
credentials = json.loads((root / '.deployment' / 'local-admin.json').read_text())
artifacts = root / '.deployment'
with sync_playwright() as p:
    browser = p.chromium.launch(
        executable_path='/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
        headless=True,
    )
    page = browser.new_page(viewport={'width': 1280, 'height': 950})
    errors = []
    page.on('pageerror', lambda error: errors.append(str(error)))
    page.goto('http://127.0.0.1:8000/login')
    page.get_by_label('Username', exact=True).fill(credentials['username'])
    page.get_by_label('Password', exact=True).fill(credentials['password'])
    page.get_by_role('button', name='Log in', exact=True).click()
    expect(page.get_by_role('link', name='Edit levels').first).to_be_visible()
    page.get_by_role('link', name='Start Game', exact=True).click()
    expect(page.get_by_role('link', name='Level 1:', exact=False)).to_be_visible()
    page.get_by_role('link', name='Level 1:', exact=False).click()
    page.get_by_role('button', name='Apply X gate').click()
    expect(page.get_by_text('Puzzle solved!', exact=False)).to_be_visible()
    page.reload()
    expect(page.get_by_text('Puzzle solved!', exact=False)).to_be_visible()
    page.screenshot(path=str(artifacts / 'preview-game.png'), full_page=True)
    page.get_by_role('button', name='Reset puzzle').click()
    expect(page.get_by_text('Puzzle solved!', exact=False)).not_to_be_visible()
    page.goto('http://127.0.0.1:8000/admin/game/gamelevel/1/change/')
    expect(page.get_by_label('初始状态:', exact=True)).to_be_visible()
    title = page.locator('#id_title')
    original = title.input_value()
    title.fill('Browser-verified level')
    page.get_by_role('button', name='Save and continue editing').click()
    expect(page.locator('.success')).to_be_visible()
    page.screenshot(path=str(artifacts / 'preview-admin.png'), full_page=True)
    title.fill(original)
    page.get_by_role('button', name='Save and continue editing').click()
    expect(page.locator('.success')).to_be_visible()
    for level, gate in ((2, 'H'), (3, 'Z'), (4, 'CZ')):
        page.goto(f'http://127.0.0.1:8000/game/{level}')
        page.get_by_role('button', name='Reset puzzle').click()
        page.get_by_role('button', name=f'Apply {gate} gate').click()
        expect(page.get_by_text('Puzzle solved!', exact=False)).to_be_visible()
    page.set_viewport_size({'width': 390, 'height': 844})
    page.goto('http://127.0.0.1:8000/game/4')
    expect(page.get_by_role('button', name='Apply CZ gate')).to_be_visible()
    page.screenshot(path=str(artifacts / 'preview-mobile.png'), full_page=True)
    assert not page.evaluate('document.documentElement.scrollWidth > window.innerWidth'), 'Mobile layout overflows.'
    assert not errors, errors
    browser.close()
print('Browser checks passed: login, four puzzles, persisted progress, reset, admin editing, mobile layout.')
