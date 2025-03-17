import requests
from bs4 import BeautifulSoup

urls = [
    "https://www.sutd.edu.sg/",
    "https://www.sutd.edu.sg/education",
    "https://www.sutd.edu.sg/education/undergraduate",
    "https://www.sutd.edu.sg/education/graduate/masters",
    "https://www.sutd.edu.sg/admissions/academy/",
    "https://www.sutd.edu.sg/education/accreditation",
    "https://www.sutd.edu.sg/education/undergraduate/courses",
    "https://www.sutd.edu.sg/asd",
    "https://www.sutd.edu.sg/asd/education/undergraduate/courses",
    "https://www.sutd.edu.sg/dai",
    "https://www.sutd.edu.sg/dai/education/undergraduate/specialisation-tracks/",
    "https://www.sutd.edu.sg/epd",
    "https://www.sutd.edu.sg/epd/education/undergraduate/specialisation-tracks/beyond-industry-4-0",
    "https://www.sutd.edu.sg/esd",
    "https://www.sutd.edu.sg/esd/education/undergraduate/specialisation-tracks/overview/",
    "https://www.sutd.edu.sg/hass",
    "https://www.sutd.edu.sg/hass/education/undergraduate/minors/digital-humanities-minor/",
    "https://www.sutd.edu.sg/istd",
    "https://www.sutd.edu.sg/istd/education/undergraduate/specialisation-tracks/overview/",
    "https://www.sutd.edu.sg/smt",
    "https://www.sutd.edu.sg/smt/education/undergraduate/minors/",
    "https://www.sutd.edu.sg/research",
    "https://www.sutd.edu.sg/innovation",
    "https://www.sutd.edu.sg/enterprise",
    "https://www.sutd.edu.sg/admissions",
    "https://www.sutd.edu.sg/admissions/undergraduate",
    "https://www.sutd.edu.sg/admissions/graduate/masters/",
    "https://www.sutd.edu.sg/admissions/academy",
    "https://www.sutd.edu.sg/campus-life",
    "https://www.sutd.edu.sg/campus-life/undergraduate-opportunities-programme/",
    "https://www.sutd.edu.sg/campus-life/student-life",
    "https://www.sutd.edu.sg/campus-life/global-experience-and-exchange/",
    "https://www.sutd.edu.sg/campus-life/career-development/",
    "https://www.sutd.edu.sg/campus-life/wellbeing-services/overview/",
    "https://www.sutd.edu.sg/campus-life/academic-facilities/",
    "https://www.sutd.edu.sg/campus-life/housing/",
    "https://www.sutd.edu.sg/campus-life/sports-and-recreation-centre/",
    "https://www.sutd.edu.sg/campus-life/fnb-and-services/dining",
    "https://www.sutd.edu.sg/about",
    "https://www.sutd.edu.sg/about/design-ai/",
    "https://www.sutd.edu.sg/about/at-a-glance",
    "https://www.sutd.edu.sg/about/diversity-inclusion/building-gender-diversity/",
    "https://www.sutd.edu.sg/about/sustainability",
    "https://www.sutd.edu.sg/about/people/leadership",
    "https://www.sutd.edu.sg/about/people/board-of-trustees/",
    "https://www.sutd.edu.sg/about/people/president-emeritus",
    "https://www.sutd.edu.sg/about/people/professorships/",
    "https://www.sutd.edu.sg/about/people/faculty",
    "https://www.sutd.edu.sg/about/happenings",
    "https://www.sutd.edu.sg/about/careers",
    "https://www.sutd.edu.sg/about/partnering-with-sutd",
]


def load_web_docs(urls):
    docs = []
    for url in urls:
        docs.append(scrape_url(url))
    return docs


def scrape_url(url):

    try:
        response = requests.get(url)
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
        return f"Error fetching the webpage: {e}"
