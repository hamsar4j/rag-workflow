import requests
from bs4 import BeautifulSoup
import logging
from app.utils.progress import progress_bar

logger = logging.getLogger(__name__)


def load_web_docs(urls: list[str]) -> list[tuple[str, str]]:
    """Load content from a list of URLs."""

    if not urls:
        logger.warning("No URLs provided for scraping.")
        return []

    docs = []

    with progress_bar("Scraping URLs...") as progress:
        task = progress.add_task("Scraping URLs...", total=len(urls))

        for url in urls:
            logger.info(f"Scraping URL: {url}")
            content = scrape_url(url)
            docs.append((content, url))
            progress.update(task, advance=1)

    return docs


def scrape_url(url: str) -> str:
    """Scrape content from a single URL."""

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # content = soup.find("font")
        content = soup

        if content:
            text = content.get_text()
            text = " ".join(text.split())
            return text
        else:
            return "Could not find the main content."

    except requests.RequestException as e:
        error_msg = f"Error fetching the webpage: {e}"
        logger.error(error_msg)
        return error_msg
    except Exception as e:
        error_msg = f"Unexpected error while scraping {url}: {e}"
        logger.error(error_msg)
        return error_msg
