import boto3
import botocore

from config.settings.local import AWS_ACCESS_KEY, AWS_SECRET_KEY


class SnsWrapper:
    """Encapsulates Amazon SNS topic and subscription functions."""

    def __init__(self):
        """
        :param sns_resource: A Boto3 Amazon SNS resource.
        """
        self.sns_resource = boto3.client(
            "sns",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
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
