import logging
import os
import re

import pandas as pd

from create_email_text import create_email_text, extract_game_datetimes
from send_email import send_email

_S3BUCKET = os.environ["S3BUCKET"]
_ENVIRONMENT = os.environ["ENVIRONMENT"]


def handler(event, context):
    current_iso_week = pd.Timestamp.today().isocalendar().week

    if (email_type := event.get("email_type")) not in ["monday", "thursday", "friday"]:
        raise Exception("Unknown email type")

    current_game_datetime_w_url, upcoming_five_games_datetimes = extract_game_datetimes(
        current_iso_week, _S3BUCKET
    )
    game_status = ""
    participants = ""

    if email_type == "friday":
        from get_participation_nuudel import get_participation

        try:
            current_game_url = re.search(
                r"\bhttps?://[\w/./]+\b", current_game_datetime_w_url
            ).group()
        except AttributeError as e:
            logging.error("Could parse url")
            raise AttributeError(e)

        game_status, participants = get_participation(current_game_url)
        print(game_status)
        print(participants)

    subject, email_text = create_email_text(
        email_type,
        current_game_datetime_w_url,
        upcoming_five_games_datetimes,
        game_status,
        participants,
    )
    send_email(subject, email_text, _ENVIRONMENT)
