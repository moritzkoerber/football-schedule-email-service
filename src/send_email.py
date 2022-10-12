import json

import boto3


def _get_secret(boto3_session, environment: str, secret_type: str):
    return json.loads(
        boto3_session.client("secretsmanager").get_secret_value(
            SecretId=f"football-email-service-{environment}-email_adress-{secret_type}"
        )["SecretString"]
    )["email_address"]


def send_email(
    subject: str,
    email_txt: str,
    environment: str,
):
    boto3_session = boto3.Session()

    source_email_address = _get_secret(boto3_session, environment, "source")
    destination_email_address = _get_secret(boto3_session, environment, "destination")
    arn = source_email_address.split("@")[1]

    ses_client = boto3_session.client("ses", region_name="eu-central-1")

    response = ses_client.send_email(
        Source=source_email_address,
        Destination={
            "ToAddresses": [
                destination_email_address,
            ],
        },
        Message={
            "Subject": {"Data": subject, "Charset": "utf-8"},
            "Body": {
                "Text": {"Data": email_txt, "Charset": "utf-8"},
            },
        },
        ReplyToAddresses=[source_email_address],
        ReturnPath=source_email_address,
        SourceArn=f"arn:aws:ses:{boto3_session.region_name}:820381935377:identity/{arn}",
        ReturnPathArn=f"arn:aws:ses:{boto3_session.region_name}:820381935377:identity/{arn}",
    )
    print(response)
