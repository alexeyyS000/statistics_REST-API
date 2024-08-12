import json

from playwright.sync_api import sync_playwright

from .redis_db.client import get_client


def save_headers(url: str, sub_url_include: str):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        async def log_request(request):
            if sub_url_include in request.url:
                get_client().set("headers", json.dumps(request.headers))

        page.on("request", log_request)
        page.goto(url)
        browser.close()
