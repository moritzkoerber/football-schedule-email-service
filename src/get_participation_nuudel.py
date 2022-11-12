import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.remote.webelement import WebElement


def _create_participation_list(user_list: WebElement) -> list:
    return list(
        zip(
            [
                x.get_attribute("innerText")
                for x in user_list.find_elements(by=By.CSS_SELECTOR, value="th.bg-info")
            ],
            [
                1 if x.get_attribute("innerText") == "Yes" else 0
                for x in user_list.find_elements(by=By.CLASS_NAME, value="sr-only")
            ],
        )
    )


LOGGER.setLevel(logging.DEBUG)
logging.getLogger().setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

service = Service(log_path="/tmp/geckodriver.log")

options = FirefoxOptions()
options.add_argument("--headless")

logging.info("Starting Firefox")
try:
    driver = webdriver.Firefox(options=options, service=service)
except Exception as e:
    logging.error("Error starting Firefox")
    logging.error(e)
    logging.error("geckodriver.log:")
    with open("/tmp/geckodriver.log") as f:
        print(f.read())
    raise Exception


def get_participation(url):
    logging.info("Getting url")
    driver.get(url)

    logging.info("Grabbing user_list")
    user_list = driver.find_element(by=By.CSS_SELECTOR, value="tbody")

    logging.info("Get participation")
    participation = _create_participation_list(user_list)

    logging.info(f"Got participants: {', '.join(str(x) for x in participation)}")

    game_status = "Abgesagt:"
    participants_str = "Leider zu wenig Spieler!"

    if (num_players := sum(e[1] for e in participation)) >= 8:
        game_status = "Wir spielen:"
        participants_str = f"({num_players} Spieler: {', '.join(e[0] for e in filter(lambda x: x[1] == 1, participation))})"
    return game_status, participants_str
