from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import permissions
from .models import UserProfile
from .serializers import UserProfileSerializer
from accounts.serializers import UserModelSerializer
from utils.responses import *


class GetUserProfileView(APIView):
    def get(self, request, format=None):
        try:
            user = self.request.user
            user_profile = UserProfile.objects.filter(user=user)
            user_profile = UserProfileSerializer(user_profile)
            return success_response({'profile': user_profile.data})
        except Exception as error:
            return server_error({'error': f'{error}'})


class UdateUserProfile(APIView):
    def put(self, request, format=None):
        try:
            user = self.request.user
            data = self.request.data

            user = data.get("user")
            full_name = data.get("full_name")
            address_line_1 = data.get("address_line_1")
            address_line_1 = data.get("address_line_1")
            city = data.get("city")
            state_or_province = data.get("state_or_province")
            zip_code = data.get("zip_code")
            telephone = data.get("telephone")
            additional_phone = data.get("additional_phone")
            profile_pic = data.get("profile_pic")

            UserProfile.objects.filter(user=user).update(
                user=user,
                full_name=full_name,
                address_line_1=address_line_1,
                address_line_1=address_line_1,
                city=city,
                state_or_province=state_or_province,
                zip_code=zip_code,
                telephone=telephone,
                additional_phone=additional_phone,
                profile_pic=profile_pic
            )

            user_profile = UserProfile.objects.filter(user=user)
            user_profile = UserProfileSerializer(user_profile)

            return success_response({'profile': user_profile.data})
        except Exception as error:
            return server_error({'error': f'{error}'})
