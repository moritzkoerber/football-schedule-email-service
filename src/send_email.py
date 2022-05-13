import json

import boto3


def send_email(
    subject: str,
    email_txt: str,
    environment: str,
):
    def _get_secret(secret_type: str):
        return json.loads(
            boto3.client("secretsmanager").get_secret_value(
                SecretId=f"football-email-service-{environment}-email_adress-{secret_type}"
            )["SecretString"]
        )["email_address"]

    source_email_address = _get_secret("source")
    destination_email_address = _get_secret("destination")
    arn = destination_email_address.split("@")[1]

    ses_client = boto3.client("ses", region_name="eu-central-1")

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
        SourceArn=f"arn:aws:ses:eu-central-1:820381935377:identity/{arn}",
        ReturnPathArn=f"arn:aws:ses:eu-central-1:820381935377:identity/{arn}",
    )
    print(response)
