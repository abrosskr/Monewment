import time
import random
import base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth

class BaeminScraper:
    def __init__(self, remote_url="http://localhost:4444/wd/hub"):
        # If running inside docker, use 'http://chrome:4444/wd/hub'
        # But for default init we can assume localhost for testing if outside docker
        # Docker internal: http://chrome:4444/wd/hub
        self.remote_url = remote_url

    def get_driver(self):
        options = Options()
        options.add_argument("start-maximized")
        # options.add_argument("--headless") # Remote server is usually headless or Xvfb
        
        # Anti-detection flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Remote(
            command_executor=self.remote_url,
            options=options
        )
        
        # Apply Stealth
        # Note: selenium-stealth communicates via CDP. Remote WebDriver supports this if properly configured.
        # If it fails on Remote, we rely on the flags above.
        try:
            stealth(driver,
                languages=["ko-KR", "ko", "en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
            )
        except Exception as e:
            print(f"Stealth init warning: {e}")

        return driver

    def scrape_menu(self, url: str):
        """
        Visits the URL and returns a screenshot (base64) and page title.
        """
        driver = self.get_driver()
        try:
            driver.get(url)
            
            # Human-like delay
            time.sleep(random.uniform(2, 5))
            
            # Scroll down to load lazy images (simple scroll)
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(1, 2))
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))

            title = driver.title
            # Capture full page screenshot usually requires trickery, but simple screenshot is fine for Vision AI
            # Vision AI often handles standard Screenshots well if layout is responsive.
            screenshot_b64 = driver.get_screenshot_as_base64()
            
            return {
                "title": title,
                "screenshot": screenshot_b64
            }
        finally:
            driver.quit()

# Factory for dependency injection if needed
def get_scraper():
    # Detect if running in Docker (simplified check or env var)
    # For now, let's use the docker service name if we assume this runs in backend container
    # But wait, backend runs on host currently via `uvicorn` in existing setup?
    # No, user is running `start_vendors.ps1` which runs `uvicorn` locally on Host.
    # The `chrome` service runs in Docker.
    # So `localhost:4444` is correct for Host->Docker communication because we exposed ports 4444:4444.
    return BaeminScraper(remote_url="http://localhost:4444/wd/hub")
