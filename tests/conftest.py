# Copyright 2025 Streamlit PDF Component
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest
from typing import Generator, Any, Dict
from playwright.sync_api import Browser, BrowserContext, Page


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """
    Create and yield a Playwright BrowserContext configured for tests.
    
    Parameters:
        browser (Browser): Playwright browser instance used to create the context.
    
    Returns:
        Generator[BrowserContext, None, None]: A generator that yields a BrowserContext with downloads accepted, service workers blocked for Chromium (allowed otherwise), and a default operation timeout of 30000 ms.
    """
    # Browser-specific context options
    context_options: Dict[str, Any] = {
        "accept_downloads": True,
        "service_workers": "block"
        if browser.browser_type.name == "chromium"
        else "allow",
    }

    context = browser.new_context(**context_options)

    # Set default timeout for all operations
    context.set_default_timeout(30000)

    yield context
    context.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """
    Create a new Playwright Page and attach console and page-error listeners for test debugging.
    
    The fixture yields a Page that logs console messages (errors, warnings, and other types, including messages from iframes) and page errors to standard output, and closes the page after the test completes.
    
    Returns:
        page (Page): Playwright Page with console and pageerror listeners attached.
    """
    page = context.new_page()

    # Add console message listener for debugging
    def handle_console(msg):
        # Also log console messages from iframes
        """
        Log a Playwright console message to standard output with a severity-prefixed annotation.
        
        This function prints console messages (including those originating from iframes) to stdout:
        - Error messages are printed with an "[CONSOLE ERROR]" prefix and include the message location when available.
        - Warning messages are printed with an "[CONSOLE WARNING]" prefix.
        - All other message types are printed with their type enclosed in brackets.
        
        Parameters:
            msg: Playwright ConsoleMessage object representing the console entry to log.
        """
        if msg.type == "error":
            print(f"[CONSOLE ERROR] {msg.text}")
            if msg.location:
                print(f"  at {msg.location}")
        elif msg.type == "warning":
            print(f"[CONSOLE WARNING] {msg.text}")
        else:
            print(f"[{msg.type}] {msg.text}")

    page.on("console", handle_console)

    # Add page error listener
    page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))

    yield page
    page.close()


def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "accessibility: marks tests as accessibility tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "edge_case: marks tests as edge case tests"
    )


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Enrich pytest test reports with browser context and print page debugging information on failures.
    
    When a test uses the `page` fixture this hook attaches the browser name to the test report as `rep.browser`. If the test fails during the call phase, prints a failure header that includes the browser and test name, followed by the page title, number of frames, and current page URL. Exceptions encountered while gathering page information are caught and printed.
    
    Parameters:
        item: The pytest test item; if it provides a `page` fixture, that page is used to collect browser and page details.
        call: The pytest call object representing the test phase (setup/call/teardown).
    """
    outcome = yield
    rep = outcome.get_result()

    # Add browser name to test report
    if hasattr(item, "funcargs") and "page" in item.funcargs:
        page = item.funcargs["page"]
        browser_name = page.context.browser.browser_type.name
        rep.browser = browser_name

        # On failure, add more debugging info
        if rep.failed and call.when == "call":
            print(f"\n[FAILED in {browser_name}] Test: {item.name}")
            try:
                # Try to get page title for context
                title = page.title()
                print(f"Page title: {title}")

                # Check if there are any iframes
                frames = page.frames
                print(f"Number of frames: {len(frames)}")

                # Get page URL
                print(f"Page URL: {page.url}")
            except Exception as e:
                print(f"Could not get page info: {e}")


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """
    Extend browser launch arguments to enable Firefox's built-in PDF viewer.
    
    Parameters:
        browser_type_launch_args (dict): Existing browser launch arguments to extend.
    
    Returns:
        dict: A new dictionary combining the provided launch arguments with
        the Firefox user preference `"pdfjs.disabled": False`.
    """
    return {
        **browser_type_launch_args,
        "firefox_user_prefs": {
            "pdfjs.disabled": False,
        }
    }