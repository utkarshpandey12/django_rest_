import random
import re
import string
from datetime import datetime, timezone

from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import MbxUser, Otp
from .token import create_temp_token


class OtpSerializer(ModelSerializer):
    class Meta:
        model = Otp
        fields = ["country_code", "phone_number"]
        extra_kwargs = {
            "phone_number": {"write_only": True},
            "country_code": {"write_only": True},
        }

    def create(self, validated_data):
        # message_sender = SnsWrapper()
        # code = random.randint(1, 899999) + 100000
        code = 654321
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

                phone_number_record.code = code
                phone_number_record.save()
                return {"message": "success"}

        except Otp.DoesNotExist:
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


class OtpVerifySerializer(ModelSerializer):
    class Meta:
        model = Otp
        fields = ["code", "country_code", "phone_number"]
        extra_kwargs = {
            "phone_number": {"write_only": True},
            "country_code": {"write_only": True},
            "code": {"write_only": True},
        }

    def validate(self, validate_data):
        country_code = validate_data.get("country_code", "+91")
        phone_number = validate_data.get("phone_number")
        code = validate_data.get("code")

        if len(phone_number) < 10:
            raise serializers.ValidationError(
                {"error": "Enter a valid 10 digit number"}
            )

        if len(str(code)) != 6:
            raise serializers.ValidationError(
                {"error": "Enter a valid 6 digit one time password"}
            )

        if (
            re.fullmatch(
                "[6-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]", phone_number
            )
            is None
        ):
            raise serializers.ValidationError({"error": "Invalid phone number"})

        return {
            "country_code": country_code,
            "phone_number": phone_number,
            "code": code,
        }

    def create(self, validated_data):
        otp_verification_result = Otp.objects.get(
            phone_number=validated_data["phone_number"]
        )
        if not (otp_verification_result.code == validated_data["code"]):
            raise serializers.ValidationError({"error": "Invalid one time password"})

        otp_verification_result.count = 0
        otp_verification_result.save()

        try:
            user, is_created = MbxUser.objects.get_or_create(
                country_code=validated_data["country_code"],
                phone_number=validated_data["phone_number"],
            )
        except (MbxUser.DoesNotExist, IntegrityError) as error:
            print(error)
            raise serializers.ValidationError({"error": "user not found/created!"})

        if is_created:
            integrity_error = True
            while integrity_error:
                user.referral_code = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=8)
                )
                try:
                    user.save()
                    integrity_error = False
                except IntegrityError:
                    integrity_error = True

        temp_token = create_temp_token(user.id, user.is_mpin_set)

        return {
            "message": "success",
            "data": {"temp_token": temp_token, "is_new_user": is_created},
        }


class MpinSerializer(ModelSerializer):
    class Meta:
        model = MbxUser
        fields = ["mpin"]
        extra_kwargs = {
            "mpin": {"write_only": True},
        }

    def validate(self, validate_data):
        mpin = validate_data.get("mpin")

        if len(str(mpin)) < 4 or len(str(mpin)) > 4:
            raise serializers.ValidationError(
                {"error": "Enter a valid 4 digit number as mpin"}
            )

        try:
            int(mpin)
        except Exception:
            raise serializers.ValidationError({"error": "only numbers allowed"})

        return {
            "mpin": mpin,
        }


class ReferralVerifySerializer(serializers.Serializer):

    referral_code = serializers.CharField(max_length=8)

    def validate_referral_code(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Referral code should be of 8 digits!")
        return value


class MbxUserProfessionUpdateSerializer(ModelSerializer):
    class Meta:
        model = MbxUser
        fields = ["profession"]

    def validate(self, validate_data):
        if not validate_data:
            raise serializers.ValidationError({"error": "invalid json data"})
        return validate_data
