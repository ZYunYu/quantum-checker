"""Generate printable English guides from the public HTML using Playwright."""
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent.parent
folder = root / 'quantum-checkers-ui/public/guides'
browser_path = os.environ.get('GUIDE_BROWSER_PATH', '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge')
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path=browser_path, headless=True)
    page = browser.new_page(viewport={'width': 1000, 'height': 1000})
    for name in ('admin-guide', 'user-guide'):
        page.goto((folder / f'{name}.html').as_uri(), wait_until='networkidle')
        page.pdf(
            path=str(folder / f'{name}.pdf'), prefer_css_page_size=True,
            print_background=True, display_header_footer=True,
            header_template='<span></span>',
            footer_template='<div style="font:9px Arial;width:100%;text-align:center;color:#53687c">Quantum Checkers · <span class="pageNumber"></span> / <span class="totalPages"></span></div>',
        )
        page.screenshot(path=str(root / f'.deployment/{name}-preview.png'), full_page=True)
        print('Generated:', folder / f'{name}.pdf')
    browser.close()
