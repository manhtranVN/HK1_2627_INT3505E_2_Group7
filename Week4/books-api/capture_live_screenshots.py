import os
import sys
import time

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from playwright.sync_api import sync_playwright

def run():
    screenshots_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
    os.makedirs(screenshots_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1400, "height": 1100})
        page = context.new_page()

        print("Navigating to http://127.0.0.1:5000/docs...")
        page.goto("http://127.0.0.1:5000/docs", wait_until="networkidle")
        page.wait_for_selector(".swagger-ui", timeout=10000)
        time.sleep(2)

        # 1. Overview
        p1 = os.path.join(screenshots_dir, "01_swagger_ui_overview.png")
        page.screenshot(path=p1)
        print("Saved:", p1)

        # 2. Open GET /books
        get_op = page.locator("#operations-books-listBooks")
        get_op.locator(".opblock-summary").click()
        time.sleep(1)

        # Try it out
        try_btn = get_op.locator("button.try-out__btn")
        if "Try it out" in try_btn.inner_text():
            try_btn.click()
            time.sleep(1)

        p2 = os.path.join(screenshots_dir, "02_swagger_ui_try_it_out_get_ready.png")
        page.screenshot(path=p2)
        print("Saved:", p2)

        # Click Execute
        exec_btn = get_op.locator("button.execute")
        exec_btn.scroll_into_view_if_needed()
        time.sleep(0.5)
        exec_btn.click()

        # Wait for response 200
        get_op.locator(".response-col_status:has-text('200')").first.wait_for(timeout=10000)
        time.sleep(1)

        # Scroll so response is visible
        get_op.locator(".responses-inner").first.scroll_into_view_if_needed()
        time.sleep(1)

        p3 = os.path.join(screenshots_dir, "03_swagger_ui_try_it_out_get_200_ok.png")
        page.screenshot(path=p3)
        print("Saved:", p3)

        # Collapse GET /books
        get_op.locator(".opblock-summary").click()
        time.sleep(0.5)

        # 3. POST /books
        post_op = page.locator("#operations-books-createBook")
        post_op.locator(".opblock-summary").scroll_into_view_if_needed()
        time.sleep(0.5)
        post_op.locator(".opblock-summary").click()
        time.sleep(1)

        post_try = post_op.locator("button.try-out__btn")
        if "Try it out" in post_try.inner_text():
            post_try.click()
            time.sleep(1)

        post_exec = post_op.locator("button.execute")
        post_exec.scroll_into_view_if_needed()
        time.sleep(0.5)
        post_exec.click()

        post_op.locator(".response-col_status:has-text('201')").first.wait_for(timeout=10000)
        time.sleep(1)
        post_op.locator(".responses-inner").first.scroll_into_view_if_needed()
        time.sleep(1)

        p4 = os.path.join(screenshots_dir, "04_swagger_ui_try_it_out_post_201_created.png")
        page.screenshot(path=p4)
        print("Saved:", p4)

        # Collapse POST
        post_op.locator(".opblock-summary").click()
        time.sleep(0.5)

        # 4. GET /books/{bookId} with 404 test
        get_id_op = page.locator("#operations-books-getBookById")
        get_id_op.locator(".opblock-summary").scroll_into_view_if_needed()
        time.sleep(0.5)
        get_id_op.locator(".opblock-summary").click()
        time.sleep(1)

        get_id_try = get_id_op.locator("button.try-out__btn")
        if "Try it out" in get_id_try.inner_text():
            get_id_try.click()
            time.sleep(1)

        # Fill non-existent UUID
        param_input = get_id_op.locator("input[placeholder='bookId']").first
        if param_input.count() > 0:
            param_input.fill("00000000-0000-0000-0000-000000000000")
        
        get_id_exec = get_id_op.locator("button.execute")
        get_id_exec.scroll_into_view_if_needed()
        time.sleep(0.5)
        get_id_exec.click()

        get_id_op.locator(".response-col_status:has-text('404')").first.wait_for(timeout=10000)
        time.sleep(1)
        get_id_op.locator(".responses-inner").first.scroll_into_view_if_needed()
        time.sleep(1)

        p5 = os.path.join(screenshots_dir, "05_swagger_ui_try_it_out_404_rfc7807.png")
        page.screenshot(path=p5)
        print("Saved:", p5)

        browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    run()
