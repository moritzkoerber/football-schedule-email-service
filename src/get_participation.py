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
        by=By.CLASS_NAME, value="UserList__list-participants-list"
    )

    participation = zip(
        [
            x.get_dom_attribute("name")
            for x in user_list.find_elements(
                by=By.CLASS_NAME, value="UserAvatarWithSubIcon"
            )
        ],
        [
            int(
                x.get_dom_attribute("class")
                .split()[1]
                .replace("Icon--cannot-attend", "0")
                .replace("Icon---check", "1")
            )
            for x in user_list.find_elements(by=By.CSS_SELECTOR, value="svg")
        ],
    )
    game_status = "Abgesagt:"
    participants_str = ""
    if sum(e[1] for e in participation) >= 8:
        game_status = "Wir spielen!"
        participants_str = (
            f"({', '.join(e[0] for e in filter(lambda x: x[1] == 1, participation))})"
        )
    return game_status, participants_str
