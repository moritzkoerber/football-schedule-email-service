import contextlib
import logging
import time

from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
)
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.remote.remote_connection import LOGGER
from selenium.webdriver.remote.webelement import WebElement


def _create_participation_list(user_list: WebElement) -> list:
    return list(
        zip(
            [
                name
                for x in user_list.find_elements(by=By.CLASS_NAME, value="chakra-text")
                if (name := x.get_attribute("innerText")) != "Organizer"
            ],
            [
                int(
                    x.get_dom_attribute("aria-label")
                    .replace("Cross", "0")
                    .replace("BracketsCheck", "0")
                    .replace("Checkmark", "1")
                )
                for x in user_list.find_elements(by=By.CSS_SELECTOR, value="svg")
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
    logging.info("get url")
    driver.get(url)

    with contextlib.suppress(NoSuchElementException, ElementNotInteractableException):
        time.sleep(10)
        logging.info("Trying to accept cookies")
        obj = driver.find_element(
            by=By.XPATH, value='//*[@id="onetrust-accept-btn-handler"]'
        )
        actions = ActionChains(driver)
        actions.move_to_element(obj)
        actions.click(obj)
        actions.perform()

    logging.info("Grabbing user_list")
    user_list = driver.find_element(
        by=By.CLASS_NAME,
        value="votes-participants-module_votes-participants__list__xyqSV",
    )

    logging.info("Get participation")
    participation = _create_participation_list(user_list)

    logging.info("Scrolling once to last element:")
    with contextlib.suppress(TypeError):
        user_list.find_elements(by=By.CLASS_NAME, value="chakra-text")[
            -1
        ].location_once_scrolled_into_view()

    logging.info("Get participation once more")
    participation += _create_participation_list(user_list)

    # deduplicate
    participation = list(set(participation))

    logging.info(f"Got participants: {', '.join(str(x) for x in participation)}")
    game_status = "Abgesagt:"
    participants_str = "Leider zu wenig Spieler!"
    if sum(e[1] for e in participation) >= 8:
        game_status = "Wir spielen:"
        participants_str = (
            f"({', '.join(e[0] for e in filter(lambda x: x[1] == 1, participation))})"
        )
    return game_status, participants_str
