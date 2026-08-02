"""Black-box browser smoke test for the no-login customer workflow.

Run through the repository's webapp-testing helper:
  python /Users/amlfarhad/.agents/skills/webapp-testing/scripts/with_server.py \
    --server "python3 -m content_ai_solution_lab.web --port 8765" --port 8765 \
    -- python tests/browser_journey.py
"""

from pathlib import Path
import sys

try:
    from playwright.sync_api import expect, sync_playwright
except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional browser tooling
    raise SystemExit("Playwright is optional; install it with `pip install -e .[test]` before running this journey.") from exc


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8765"
ARTIFACT_DIR = ROOT / "artifacts"


def main() -> None:
    ARTIFACT_DIR.mkdir(exist_ok=True)
    console_errors = []
    failed_requests = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.on("console", lambda message: console_errors.append(message.text) if message.type == "error" else None)
        page.on("requestfailed", lambda request: failed_requests.append(request.url))
        page.goto(BASE_URL, wait_until="networkidle")

        expect(page.get_by_role("heading", name="From messy content to a governed decision.")).to_be_visible()
        expect(page.get_by_text("Northstar Manufacturing")).to_be_visible()
        expect(page.get_by_text("Urgent Contractor Access Exception")).to_be_visible()

        page.get_by_role("button", name="Run policy workflow").click()
        expect(page.get_by_text("Proceed automatically")).to_be_visible()
        expect(page.get_by_text("Needs human review")).to_be_visible()
        expect(page.get_by_text("Blocked / policy conflict")).to_be_visible()
        expect(page.get_by_text("Unsafe requests are blocked")).to_be_visible()
        expect(page.get_by_text("blocked_pending_review")).to_be_visible()

        page.get_by_role("button", name="Simulate issue").click()
        expect(page.get_by_text("Provider degraded")).to_be_visible()
        page.get_by_role("button", name="Run policy workflow").click()
        expect(page.get_by_text("Restore the mock provider before running a workflow.")).to_be_visible()

        page.get_by_role("button", name="Restore provider").click()
        page.get_by_role("button", name="Clear").click()
        page.get_by_role("button", name="Run policy workflow").click()
        expect(page.get_by_text("Select at least one content item before running the policy workflow.")).to_be_visible()

        page.get_by_role("button", name="Use sample engagement").click()
        page.screenshot(path=str(ARTIFACT_DIR / "browser_journey.png"), full_page=True)
        browser.close()

    if console_errors:
        raise AssertionError(f"Browser console errors: {console_errors}")
    if failed_requests:
        raise AssertionError(f"Failed browser requests: {failed_requests}")
    print(f"Browser journey passed; screenshot: {ARTIFACT_DIR / 'browser_journey.png'}")


if __name__ == "__main__":
    sys.exit(main())
