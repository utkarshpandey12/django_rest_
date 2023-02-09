'''
import boto3
import botocore

from config.settings.base import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_SESSION_TOKEN,
)


class SnsWrapper:
    """Encapsulates Amazon SNS topic and subscription functions."""

    def __init__(self):
        """
        :param sns_resource: A Boto3 Amazon SNS resource.
        """
        self.sns_resource = boto3.client(
            "sns",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            aws_session_token=AWS_SESSION_TOKEN,
            region_name="ap-south-1",
        )

    def publish_text_message(self, phone_number, message):
        """
        Publishes a text message directly to a phone number without need for a
        subscription.

        :param phone_number: The phone number that receives the message. This must be
                             in E.164 format. For example, a United States phone
                             number might be +12065550101.
        :param message: The message to send.
        :return: The ID of the message.
        """
        try:
            response = self.sns_resource.publish(
                PhoneNumber=phone_number, Message=message
            )
            message_id = response["MessageId"]
        except botocore.exceptions.ClientError:
            return None
        else:
            return message_id
'''

from twilio.rest import Client

from config.settings.base import (
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_HEX_CODE,
    TWILIO_M_SERVICE_SID,
)


def sendSms(mobileNumber, otp):
    account_sid = TWILIO_ACCOUNT_SID
    auth_token = TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    try:
        client.messages.create(
            messaging_service_sid=TWILIO_M_SERVICE_SID,
            body="#"
            + otp
            + " is your Moneyboxx verification OTP."
            + "\n"
            + TWILIO_HEX_CODE,
            to=mobileNumber,
        )
        return True
    except Exception:
        return False
