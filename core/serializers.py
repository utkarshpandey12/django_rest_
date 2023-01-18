import random
import re
from datetime import datetime, timezone

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import Otp
from .send_otp_sns import SnsWrapper


class OtpSerializer(ModelSerializer):
    class Meta:
        model = Otp
        fields = ["country_code", "phone_number"]
        extra_kwargs = {
            "phone_number": {"write_only": True},
            "country_code": {"write_only": True},
        }

    def create(self, validated_data):
        message_sender = SnsWrapper()
        code = random.randint(1, 899999) + 100000
        try:
            phone_number_record = Otp.objects.get(
                phone_number=validated_data["phone_number"]
            )

            if (
                round(
                    (
                        datetime.now(timezone.utc) - phone_number_record.updated_at
                    ).total_seconds()
                )
                < 900
                and phone_number_record.count > 5
            ):
                raise serializers.ValidationError({"error": "Please try after 15 mins"})

            else:
                if (
                    round(
                        (
                            datetime.now(timezone.utc) - phone_number_record.updated_at
                        ).total_seconds()
                    )
                    > 900
                    and phone_number_record.count > 5
                ):
                    phone_number_record.count = 1
                else:
                    phone_number_record.count = phone_number_record.count + 1

                if not message_sender.publish_text_message(
                    validated_data["country_code"] + validated_data["phone_number"],
                    str(code),
                ):
                    raise serializers.ValidationError({"error": "Unable to send otp"})

                phone_number_record.code = code
                phone_number_record.save()
                return {"message": "success"}

        except Otp.DoesNotExist:
            if not message_sender.publish_text_message(
                validated_data["country_code"] + validated_data["phone_number"],
                str(code),
            ):
                raise serializers.ValidationError({"error": "Unable to send otp"})
            validated_data["code"] = code
            validated_data["count"] = 1
            Otp.objects.create(**validated_data)
            return {"message": "success"}

    def validate(self, validate_data):
        country_code = validate_data.get("country_code", "+91")
        phone_number = validate_data.get("phone_number")

        if len(phone_number) < 10:
            raise serializers.ValidationError(
                {"error": "Enter a valid 10 digit number"}
            )

        if (
            re.fullmatch(
                "[6-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]", phone_number
            )
            is None
        ):
            raise serializers.ValidationError({"error": "Invalid phone number"})

        return {"country_code": country_code, "phone_number": phone_number}
