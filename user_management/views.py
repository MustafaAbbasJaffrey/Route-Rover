from django.shortcuts import render
from rest_framework.views import APIView
# from user_management.admin import PrivacyAndPolicyAdmin
from django_rest_authentication.dj_rest_auth.views import PasswordChangeView
from user_management import permissions
from rest_framework.permissions import IsAuthenticated
from django_rest_authentication.authentication.views import TokenObtainPairView
# from .serializers import UserCustomTokenObtainPairSerializer
from user_management.models import *
from rest_framework import status
from rest_framework.response import Response
from django.forms.models import model_to_dict
from rest_framework import generics
from user_management.permissions import IsDriver, IsGuardian, IsAdmin
from user_management.serializers import *
from rest_framework.permissions import AllowAny
from user_management.utils import *
from django_rest_authentication.authentication.views import UserRegisterView
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveAPIView,ListAPIView

class GuardianRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CreateProfileSerializer



class SignInView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = UserCustomTokenObtainPairSerializer

class SocialAuthenticationView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = SocialAuthSerializer


class CreateProfileView(generics.ListCreateAPIView):
    permission_classes = [IsGuardian]
    serializer_class = CreateProfileViewSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print('serializer ', serializer)
        
        # Check if the data is valid
        if serializer.is_valid():
            # Save the object and return a success response
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Print serializer errors
            print(serializer.errors)
            
            # Return a response with error details
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        # Customize how the object is saved if needed
        serializer.save()

    def get(self, request, *args, **kwargs):
        resp = {'status':True,'status_code':status.HTTP_200_OK,'message':'Nutritionist license List','data':{}}
        lst = []
        profile = Profile.objects.get(user = request.user)

        if profile:
            data = {
                    'id': profile.pk,
                    'full_name':profile.get_full_name(),
                    'phone_number':str(profile.phone_number),
                }
            resp['data'] = data
        return Response(resp)
    
class GetSchools(APIView):
    permission_classes = [IsGuardian]
    
    def get(self, request):
        resp = {}
        school_lst = []
        school_qs = School.objects.filter(is_active = True)
        for school in school_qs:
            data = {
                "id" : school.pk,
                "name" : school.school_name
            }
            school_lst.append(data)

        resp['status']  = True
        resp['status_code'] = status.HTTP_200_OK
        resp['message'] = "Schools Data"
        resp['data'] = {"data_lst"  : school_lst}

        return Response(resp, status=status.HTTP_200_OK)
    
class GetSchoolsClass(APIView):
    permission_classes = [IsGuardian]
    
    def get(self, request):
        resp = {}
        class_lst = []
        class_qs = SchoolClass.objects.filter(is_active = True)
        for school_class in class_qs:
            data = {
                "id" : school_class.pk,
                "name" : school_class.class_name
            }
            class_lst.append(data)

        resp['status']  = True
        resp['status_code'] = status.HTTP_200_OK
        resp['message'] = "Class Data"
        resp['data'] = {"data_lst"  : class_lst}

        return Response(resp, status=status.HTTP_200_OK)


class GetRoute(APIView):
    permission_classes = [IsGuardian]
    
    def get(self, request):
        resp = {}
        route_lst = []
        route_qs = Route.objects.filter(is_active = True)
        for route in route_qs:
            data = {
                "id" : route.pk,
                "name" : route.route_name
            }
            route_lst.append(data)

        resp['status']  = True
        resp['status_code'] = status.HTTP_200_OK
        resp['message'] = "Route Data"
        resp['data'] = {"data_lst"  : route_lst}

        return Response(resp, status=status.HTTP_200_OK)

