#!/usr/bin/env python3
"""Browser test of Marin Software's search and filter column with a made-up feed.

Never sends requests to the live public service. Needs Playwright for Python and Chromium.
Run: python3 tests/browser_software.py
"""
from __future__ import annotations

import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
FEED = [
    {"system_name": "Permit Tracker", "system_vendor": "Acme Civic", "system_purpose": "Track building permits", "custodian_department": "Community Development Agency"},
    {"system_name": "Ledger Pro", "system_vendor": "Books Inc", "system_purpose": "General ledger", "custodian_department": "Department of Finance"},
    {"system_name": "Payroll Plus", "system_vendor": "Books Inc", "system_purpose": "Payroll", "custodian_department": "Department of Finance"},
    {"system_name": "Case Notes", "system_vendor": "Helpful Co", "system_purpose": "Client case notes", "custodian_department": "Health and Human Services"},
    {"system_name": "=Danger() <script>x</script>", "system_vendor": "Evil Corp", "system_purpose": "Hostile text", "custodian_department": ""},
]
PANEL = "#software-filter-panel"


class Handler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def titles(page):
    return page.locator("#software-results > li:visible .software-card__name").all_inner_texts()


def run(browser, base):
    import json

    context = browser.new_context(bypass_csp=True, viewport={"width": 1200, "height": 900})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.route("https://data.marincounty.gov/**", lambda r: r.fulfill(status=200, content_type="application/json", body=json.dumps(FEED)))
    page.goto(base)
    page.wait_for_function('document.getElementById("software-results-count").textContent === "5 of 5 software systems"')

    # The column comes from filters.json: the words are the file's, and nothing is hand-written in the page.
    require(page.inner_text(f"{PANEL}-title") == "Filter" and page.inner_text(f"{PANEL} .search-input-field label") == "Search", "Title and search label")
    require(page.evaluate(f"document.querySelectorAll('{PANEL} [placeholder]').length") == 0, "No placeholders")
    require(page.inner_text("#department-facet legend") == "Departments" and page.inner_text("#department-summary") == "All departments", "Group name and All text")
    options = page.eval_on_selector_all("#department-options li", "els => els.map(e => e.textContent.trim())")
    require([o.split("(")[0].strip() for o in options] == ["Community Development Agency", "Department of Finance", "Health and Human Services"], f"Departments are counted from the feed: {options}")
    require(page.locator("#software-results script").count() == 0, "Untrusted text stays text")

    # Search, address, and Reset.
    page.fill("#software-search-input", "ledger")
    page.wait_for_function('document.getElementById("software-results-count").textContent === "1 of 5 software systems"')
    require(titles(page) == ["Ledger Pro"] and "q=ledger" in page.url, "Search filters and reaches the address")
    page.click(f"{PANEL} .action-button")
    require(len(titles(page)) == 5 and "q=" not in page.url, "Reset restores the list and clears the address")

    # A department choice.
    page.click("#department-summary")
    page.check("#department-options input[value='Department of Finance']")
    page.wait_for_function('document.getElementById("software-results-count").textContent === "2 of 5 software systems"')
    require(titles(page) == ["Ledger Pro", "Payroll Plus"] and page.inner_text("#department-summary") == "1 selected", "A department filters, and the summary counts it")

    # Nothing matches: it says so and offers Reset.
    page.fill("#software-search-input", "zzzz")
    page.wait_for_function('document.getElementById("software-results-count").textContent.startsWith("No results.")')
    require(page.locator("#software-results-count button", has_text="Reset filters").count() == 1, "Zero results offers Reset filters")
    page.click("#software-results-count button")
    page.wait_for_function('document.getElementById("software-results-count").textContent.includes("5 of 5 software systems")')

    # A link restores search and choice; Copy link points at one system.
    page.goto(base + "?q=payroll&department=Department+of+Finance")
    page.wait_for_function('document.getElementById("software-results-count").textContent === "1 of 5 software systems"')
    require(titles(page) == ["Payroll Plus"] and page.input_value("#software-search-input") == "payroll", "The address restores the search")
    require(page.locator("#department-options input[value='Department of Finance']").is_checked(), "The address restores the department")

    # Narrow screens: the column starts closed and nothing scrolls sideways.
    page.set_viewport_size({"width": 360, "height": 800})
    page.goto(base)
    page.wait_for_function('document.getElementById("software-results-count").textContent === "5 of 5 software systems"')
    require(page.get_attribute(f"{PANEL}-toggle", "aria-expanded") == "false", "Narrow screens start closed")
    require(not page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth"), "No sideways scrolling at 360 px")

    # A feed that fails shows the app's own message.
    page.set_viewport_size({"width": 1200, "height": 900})
    page.evaluate("localStorage.clear()")
    page.unroute("https://data.marincounty.gov/**")
    page.route("https://data.marincounty.gov/**", lambda r: r.fulfill(status=500, body="no"))
    page.goto(base)
    page.wait_for_function('document.getElementById("software-results-count").textContent.startsWith("Could not load")')
    require(not errors, f"No JavaScript errors: {errors}")
    context.close()


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(Handler, directory=str(ROOT)))
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            run(browser, f"http://127.0.0.1:{server.server_port}/")
            browser.close()
    finally:
        server.shutdown()
    print("Marin Software browser test (mock feed): PASS")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        sys.exit(1)
