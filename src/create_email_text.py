import re

import boto3
import numpy as np
import pandas as pd

s3_client = boto3.client("s3")


def extract_game_datetimes(current_iso_week: int, s3_bucket: str):
    txt = pd.Series(
        s3_client.get_object(Bucket=s3_bucket, Key="football_dates.txt")["Body"]
        .read()
        .decode("utf-8")
        .splitlines()
    )

    regex_dates = re.compile(
        r"\b(\d{1,2}\.\d{1,2}\.\d{4})(?:, \d{2}:\d{2} Uhr – \d{2}:\d{2} Uhr)\b"
    )

    dates = [regex_dates.search(e).group(1) for e in txt]
    dates_iso_weeks = (
        pd.to_datetime(pd.Series(dates), format="%d.%m.%Y")
        .dt.isocalendar()["week"]
        .astype("int32")
    )

    mask = np.select(
        condlist=[
            dates_iso_weeks == current_iso_week,
            dates_iso_weeks < current_iso_week,
            dates_iso_weeks > current_iso_week,
        ],
        choicelist=["current", "past", "upcoming"],
        default="",
    )

    current_game_datetime_w_url = txt[mask == "current"].iloc[0]
    upcoming_five_games_datetimes = "\n".join(txt[mask == "upcoming"][:5])

    return current_game_datetime_w_url, upcoming_five_games_datetimes


def create_email_text(
    email_type: str,
    current_game_datetime_w_url: str,
    upcoming_five_games_datetimes: str,
    game_status: str,
    participants_str: str,
):
    current_game_datetime = re.search(
        r"(.* Uhr)(?:: )", current_game_datetime_w_url
    ).group(1)

    prefix = {
        "monday": "Bitte eintragen:",
        "thursday": "PUSH:",
        "friday": game_status,
    }[email_type]

    email_txt = f"""Liebe Fußball-Freunde,

Bitte beachtet folgende Regeln und tragt euch in folgende doodle ein:
    - Wenn ihr Leute mitbringt, tragt bitte ihre Namen ein und nicht +1 bei euch o. Ä.
    - Verbindliche Zu- oder Absage bis Donnerstag! Wer Freitagmorgen zugesagt hat, zahlt bei spontanem Nicht-Erscheinen anteilig die Reservierungsgebühr oder kümmert sich eigenständig um Ersatz.
    - Es entfallen alle Zugangsregeln zur SoccArena!


{prefix} {current_game_datetime_w_url.strip()} {participants_str}

Weitere Termine:
{upcoming_five_games_datetimes}

Die Google-Gruppe darf jederzeit an weitere Interessenten weitergeleitet und geteilt werden.

Viele Grüße
Jonas+Moritz
    """
    return f"{prefix} {current_game_datetime}", email_txt


def create_cancel_socca5_email_text():
    pass
