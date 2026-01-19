"""Web crawler for fetching and extracting receipt data using Selenium."""

__all__ = ("Crawler",)

import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


class Crawler:
    """Web crawler for automated receipt data extraction using Selenium WebDriver.

    This crawler uses headless Chrome to navigate receipt pages, handle dynamic
    content loading, and extract the full HTML source after expanding collapsed
    sections.

    Attributes:
        url: The target URL to crawl

    """

    def __init__(self, url: str) -> None:
        """Initialize Crawler with target URL.

        Args:
            url: The receipt page URL to crawl

        """
        self.url = url

    @property
    def chrome_options(self) -> Options:
        """Configure Chrome options for headless browser operation.

        Sets up Chrome to run in headless mode with necessary arguments for
        stability in containerized or restricted environments.

        Returns:
            Configured Chrome Options object with:
            - Headless mode enabled (new headless implementation)
            - Sandbox disabled for container compatibility
            - Shared memory usage disabled for stability

        """
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        return chrome_options

    @property
    def driver(self) -> webdriver.Chrome:
        """Create and configure a Chrome WebDriver instance.

        Automatically downloads and installs the appropriate ChromeDriver version
        using webdriver_manager, then initializes it with the configured options.

        Returns:
            Configured Chrome WebDriver instance ready for use

        """
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.chrome_options)

    def run(self) -> str:
        """Execute the crawling process and extract page HTML.

        This method:
        1. Initializes a Chrome WebDriver instance
        2. Navigates to the target URL
        3. Waits for page load (1 second)
        4. Finds and clicks the collapsed element to expand hidden content
        5. Waits for content expansion (1 second)
        6. Extracts the complete page source HTML
        7. Closes the browser and cleans up resources

        Returns:
            Complete HTML source of the page after expanding collapsed sections

        Raises:
            selenium.common.exceptions.NoSuchElementException: If the collapsed
                element is not found on the page
            selenium.common.exceptions.WebDriverException: If there are issues
                with the WebDriver or browser

        Example:
            >>> crawler = Crawler("https://receipt.example.com/12345")
            >>> html = crawler.run()
            >>> len(html) > 0
            True

        """
        driver = self.driver
        driver.get(self.url)
        time.sleep(1)

        link_element = driver.find_element(By.CLASS_NAME, "collapsed")
        driver.execute_script("arguments[0].click();", link_element)
        time.sleep(1)

        html = driver.page_source
        driver.quit()
        return html
