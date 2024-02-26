from django.forms import model_to_dict
from django_rest_authentication.authentication.serializers import MainRegisterSerializer, SocialTokenObtainPairSerializer
from django_rest_authentication.authentication.serializers import (MyTokenObtainPairSerializer,RefreshToken,
                                                                   api_settings,update_last_login)
from rest_framework import serializers
from rest_framework import status
import magic
from .utils import decode_base64_file, get_model_objects, get_profiles
from user_management.countries import COUNTRY_CHOICES
from .models import GuardianKids

from .utils import get_user_roles, validate_phone_number
from django.db import transaction
# from django_firestore_messaging.utils import create_firebase_profile_signup,signin_firebase,get_firestore_id
from .models import *
from django.core.files import File
import re

class UserSerialier(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"


class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerialier()
    class Meta:
        model=Profile
        fields="__all__"
    
class CreateProfileSerializer(MainRegisterSerializer):
    status = serializers.BooleanField(read_only=True)
    data = serializers.DictField(read_only=True, default = {})
    message = serializers.CharField(read_only=True)

    # status_code = serializers.IntegerField(read_only=True,default = status.HTTP)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # This is for response!
        self.resp = {'status' : False, 'data':None, 'message':None, 'status_code':status.HTTP_400_BAD_REQUEST}
        
        
        # ----------- This is due to inheritance -------------
        self.fields['full_name'] = self.fields.pop('first_name')

        # ---------- Cutomer serializer --------------- #
        self.fields['role'] = serializers.ChoiceField(choices=get_user_roles(),write_only=True, required=True)
        self.fields['phone_number'] = serializers.CharField(write_only=True, required=True)
        self.fields['main_image'] = serializers.FileField(write_only=True, required=False)

        # self.fields['country_short_form'] = serializers.CharField(write_only=True, required=True)
        # self.fields['full_name'] = self.fields.pop('first_name')
        # self.fields['country_short_form'] = serializers.CharField(write_only=True, required=True)
        

    def validate(self, attrs):
        # ------ This validate method from parent class -------
        parent_attr = super().validate(attrs)

        if parent_attr['valid']:
            errors = None
            
            attrs['valid'] = True
            role = attrs.get('role',None)

             
            # number_validation = validate_phone_number(attrs['phone_number'],
            #                             attrs['country_short_form'].upper())
            
            # if attrs['valid'] and not number_validation['success']:
            #     errors = number_validation['message']
            #     attrs['valid'] = False
            
            # for key, value in COUNTRY_CHOICES:
            #     if attrs['valid'] and attrs['country_short_form'].upper() == key:
            #         attrs['country'] = value
            
            if attrs['valid'] == False:
                attrs['message'] = errors
            else:
                attrs['valid'] = True
        else:
            attrs['message'] = parent_attr['error']
            attrs['valid'] = parent_attr['valid']
 
        return attrs
    
    def create(self, validated_data):
        # ------ This create method from parent class -------
        parent_create = super().create(validated_data)

        if validated_data['valid'] == True:
            with transaction.atomic():
                print(parent_create,"+++ create")
                role = Role.objects.get(name = validated_data['role'])
                profile = Profile.objects.create(
                    user = User.objects.get(pk=parent_create['data']['pk']),
                    role = role,
                    phone_number = validated_data['phone_number'],
                    # country = validated_data['country']
                )
                # firestore_token = create_firebase_profile_signup(profile)
                # firestore_id = get_firestore_id(profile)
                parent_create['data']['phone_number'] = validated_data['phone_number']
                parent_create['data']['role'] = validated_data['role']
                parent_create['data']['main_image'] = profile.get_main_image()
                # parent_create['data']['firestore_id'] = firestore_id
                # parent_create['data']['firestore_token'] = firestore_token

                # ---------- This try catch will be added by me because usename is not diefine
                try:
                    del parent_create['data']['username']
                    del parent_create['data']['first_name']
                    del parent_create['data']['pk']
                except:
                    pass
                

                self.resp = {
                    'data':parent_create['data'],
                    'message':parent_create['message'],
                    'status':parent_create['status'],
                    'status_code':parent_create['status_code']
                }
        else:
            self.resp['message'] = validated_data['message']
        return self.resp



class UserCustomTokenObtainPairSerializer(MyTokenObtainPairSerializer):
    token_class = RefreshToken

    status = serializers.BooleanField(read_only=True)
    data = serializers.DictField(read_only=True,default = {})
    message = serializers.CharField(read_only=True)

    # status_code = serializers.IntegerField(read_only=True,default = status.HTTP)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.response = {'status' : False, 'data':None, 'message':None, 'status_code':status.HTTP_400_BAD_REQUEST}
        self.fields['role'] = serializers.ChoiceField(choices=get_user_roles(),write_only=True, required=False)
        
    def validate(self, attrs):
        #response = {"status" : False,"status_code"  : None, "message" : None, "data" : None}
        data = super().validate(attrs)
        if attrs.get('role',None) is None:
            self.response["status"] = False
            self.response["message"] = "Role is Required"
            self.response["status_code"] = status.HTTP_400_BAD_REQUEST   
        elif 'message' not in data.keys():
            # qs = ProDetails.objects.filter(professional_profile=self.user.profile)
            print(self.user.profile.role,"2222")
            if self.user.profile.role.name != attrs['role']:
                self.response["status"] = False
                self.response["message"] = f'You are already registered as a {self.user.profile.role.display_name}'
                self.response["status_code"] = status.HTTP_400_BAD_REQUEST
            
            else:
                # if self.user.profile.role.name == "nutritionist":
                    # if not qs.latest("created_on").is_validated:
                        # self.response["status"] = False
                        # self.response["message"] = f'Account is under verification'
                        # self.response["status_code"] = status.HTTP_400_BAD_REQUEST
                        # return self.response
                        
                refresh = self.get_token(self.user)
                self.response["status"] = True
                self.response["status_code"] = status.HTTP_200_OK
                self.response["message"] = "Login Successfully"
                self.response["data"] = data
                self.response['data']["refresh"] = str(refresh)
                self.response['data']["access"] = str(refresh.access_token)
                self.response['data']["role"] = str(self.user.profile.role)
                self.response['data']["main_image"] = self.user.profile.get_main_image()
                # firestore_id = get_firestore_id(self.user.profile)
                # firestore_id = None
                # firestore_token = signin_firebase(self.user.profile)
                # firebase_token = firestore_token if firestore_token else None
                # self.response['data']["firebase_token"] = firebase_token
                # firestore_id = get_firestore_id(self.user.profile)

                # self.response['data']["firebase_id"] = firestore_id
                if api_settings.UPDATE_LAST_LOGIN:
                    update_last_login(None, self.user)
                log_msg = f"{self.user.username} Login Successfully"
        else:
            self.response["status"] = False
            self.response["message"] = data["message"]
            self.response["status_code"] = status.HTTP_400_BAD_REQUEST
            # save_system_logs(log_msg, self.user)

        return self.response
    


class SocialAuthSerializer(SocialTokenObtainPairSerializer):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields["role"] = serializers.CharField(required = False,write_only=True,default=None)
        
    def validate(self, attrs):
        validate_data = super().validate(attrs).copy()
        print("validated_data",validate_data)
        attrs['valid'] = False
        errors = None
        if validate_data['valid'] == True:
            try:
                role = Role.objects.get(name=attrs['role'])
                attrs['role'] = role
            except Role.DoesNotExist:
                errors = 'Invalid role passed'
        
            if validate_data['login']==False:
                attrs['profile_creation'] = True
            else:
                attrs['profile_creation'] = False
                
            if errors:
                attrs['message'] = errors
            else:
                attrs['valid'] = True   
                         
        
        return attrs

    def create(self, validated_data):
        print("====>",validated_data,"----")
        create_data = super().create(validated_data)
        # validated_data
        errors = ['Full name is required', 'Email is required']
        print(create_data)
        if validated_data['valid'] and not create_data['message'] in errors:
            if validated_data['profile_creation'] :
                with transaction.atomic():
                    profile = Profile.objects.create(
                        user = User.objects.get(pk=create_data['data']['pk']),
                        phone_number = None,
                        main_image = None,
                        # profile_photo = None,
                        role = validated_data['role'],
                    )
            
            # create_data['data']['phone_number'] = None
            # create_data['data']['main_image'] = None
            create_data['data']['role'] = validated_data['role'].name
            create_data['data']['social'] = True
            create_data['data']['is_new_user'] = validated_data['login']
            unwanted_keys = ['password', 'last_login', 'is_superuser', 'is_staff', 'date_joined']
            return_data = {key: value for key, value in create_data.items() if key not in unwanted_keys}
            # del create_data['data']['password']
            self.resp = {
                'data':return_data['data'],
                'message':create_data['message'],
                'status':create_data['status'],
                'status_code':create_data['status_code']
            }
        else:
            
            self.resp = {
                "data":{},
                "message":create_data['message'] if 'message' in create_data else validated_data['message'],
                "status":False,
                "status_code":status.HTTP_400_BAD_REQUEST
            }

        return self.resp
    

class CreateProfileViewSerializer(serializers.Serializer):
    status_code = serializers.IntegerField(read_only=True,default=status.HTTP_201_CREATED)
    status = serializers.BooleanField(read_only=True)
    message = serializers.CharField(read_only=True,default=None)
    data = serializers.DictField(read_only=True,default={})
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resp = {'status' : False}
        request = self.context["request"]
        self.user = request.user
        self.fields["kids"] = serializers.ListField(child=serializers.DictField(), required=True,write_only=True)
        self.fields['main_image'] = serializers.CharField(write_only=True, required=False)
        self.fields['phone_number'] = serializers.CharField(write_only=True, required=True)
        self.fields['full_name'] = serializers.CharField(write_only=True, required=True)
        self.fields['home_address'] = serializers.CharField(write_only=True, required=True)
    
    def validate(self, attrs):
        '''{"main_image" : File, "full_name" : "Dev Test", "phone_number" "+12128528852", "home_address" : "Texas, US", 
                kids": [
        { "kid_image" : "base64","school_id": "1","kid_name":"Kelvin","class_id": "1","id_card_no": "AB1234", "route_id" : 1, "kid_id_card" : [
        card_image = "base64"]}
        ]},
       '''
        
        attrs['valid'] = False
        today = datetime.today()
        # number_validation = validate_phone_number(attrs['phone_number'],
        #                                 attrs['country_short_form'].upper())
            
        # if attrs['valid'] and not number_validation['success']:
        #     errors = number_validation['message']
        #     attrs['valid'] = False
            
        # for key, value in COUNTRY_CHOICES:
        #     if attrs['valid'] and attrs['country_short_form'].upper() == key:
        #         attrs['country'] = value
            
        # if attrs['valid'] == False:
        #     attrs['message'] = errors
        # else:
        attrs['valid'] = True
        # for idx, kid in enumerate(attrs.get('kids', [])):
        #     # idx += 1

        #     kids_image = decode_base64_file(kid['kid_image'])
        #     print(kids_image,"---21")
        #     if kids_image == False:
        #         self.resp["error"] = "Invalid file type. Please upload a different file."
        #         break

        #     if 'kid_image' not in kid.keys():
        #         self.resp["error"] = "Please upload the required kid image."
        #         break
        #     # elif not isinstance(experience['file'], File):
        #     elif not isinstance(file, File):
        #         self.resp["error"] = "license file should be a Type file "
        #         break

        #     if 'license_name' not in license.keys():
        #         self.resp["error"] = "Please enter the license name."
        #         break
        #     elif not isinstance(license['license_name'], str):
        #         self.resp["error"] = "The license name should be a text."
        #         break
        #     if 'license_id' not in license.keys():
        #         self.resp["error"] = "Please enter the license id"
        #         break
        #     elif not isinstance(license['license_id'], str):
        #         self.resp["error"] = "license id should be a text."
        #         break
        #     if 'start_date' not in license.keys():
        #         self.resp["error"] = "Please enter the start date."
        #         break
        #     elif not isinstance(license['start_date'], str):
        #         self.resp["error"] = "Start date should be a string"
        #         break
        #     if 'expiry_date' not in license.keys():
        #         self.resp["error"] = "Please enter the expiry date."
        #         break
        #     elif not isinstance(license['expiry_date'], str):
        #         self.resp["error"] = "Expiry date should be a string."
        #         break
        #     start_date = license.get('start_date')
        #     expiry_date = license.get('expiry_date')
        #     try:
        #         start_date_obj = datetime.strptime(start_date, "%d/%m/%Y")
        #     except ValueError:
        #         self.resp["error"] = "The start date should be in the format 'DD/MM/YYYY'."
        #         break
        #     try:
        #         expiry_date_obj = datetime.strptime(expiry_date, "%d/%m/%Y")
        #     except ValueError:
        #         self.resp["error"] = "The expiry date should be in the format 'DD/MM/YYYY'."
        #         break
        #     if start_date_obj >= expiry_date_obj:
        #         self.resp["error"] = "The expiry date must be after the start date."
        #         break
        #     elif expiry_date_obj > today:
        #         self.resp["error"] = "The expiry date cannot be in the future"
        #         break
        #     license['license_file'] = file
        # if not "error" in self.resp:
        print('attrs ', attrs)
        return attrs
    

    def create(self, validated_data):
        if validated_data['valid'] == True:
            kids = validated_data.get('kids', [])
            main_image = decode_base64_file(validated_data['main_image'])
            # Atomic Transaction
            # If one is fail all are fails 
            # not a even transaction occur
            with transaction.atomic():
                
                # New Guardian Detail Creation
                guardian_profile = GuardianDetails.objects.create(i_profile = self.user.profile,
                                                                    home_address = validated_data['home_address'])
                
                # Update User Profile
                profile_obj = Profile.objects.get(user = self.user)
                profile_obj.main_image = main_image
                profile_obj.phone_number = validated_data['phone_number']
                profile_obj.save()
                profile_obj.user.first_name = validated_data['full_name']
                profile_obj.user.save()

                # This loop is for multipule kids insertion
                for kid in kids:
                    school_obj = School.objects.get(pk = kid['school_id'])
                    class_obj = SchoolClass.objects.get(pk = kid['class_id'])   
                    route_obj = Route.objects.get(pk = kid['route_id'])
                    kids_image = decode_base64_file(kid['kid_image'])
                    

                    # Guardian kids insertions
                    g=GuardianKids.objects.create(
                        i_guardian_profile = guardian_profile,
                        i_school = school_obj,
                        i_class = class_obj,
                        i_route = route_obj,
                        kid_image = kids_image,
                        kid_name = kid['kid_name'],
                        id_card_number = kid['id_card_no']
                    )

                    # Id Card Insertion
                    # At this time we are assuming this is for multiple Id_card (one or many) related to one student
                    # But we can change it in future
                    id_card = kid['kid_id_card']
                    for card in id_card:
                        card_image = decode_base64_file(card)
                        KidsIdCard.objects.create(i_kids = g,card_media = card_image)


            # Remove Valid From validate_Data        
            validated_data.pop("valid")

            # Resposne if data is valid
            self.resp["status"] = True
            self.resp["message"] = "Profile Created"
            self.resp['status_code'] = status.HTTP_201_CREATED
            self.resp["data"] = validated_data
        else:
            # Response When data is not valid
            self.resp["message"] = self.resp.pop("error")   
            self.resp["status_code"] = status.HTTP_400_BAD_REQUEST
            self.resp["status"] = False
            self.resp["data"] = {}
        return self.resp
    

class KidsSerializer(serializers.ModelSerializer):
    class Meta:
        model=GuardianKids
        fields = "__all__"



'''
    We need to display three models data into one
    That's why we use nested serilizer approch
    School, Class and Route Data is shown along with Guardian kid data
'''

class SchoolSerializer(serializers.ModelSerializer):
    class Meta:
        model=School
        fields=['school_name']

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model=SchoolClass
        fields=['class_name']

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model=Route
        fields=['route_name']

class KidsUpdateSerializer(serializers.ModelSerializer):
    i_school = SchoolSerializer()
    i_class = ClassSerializer()
    i_route = RouteSerializer()

    class Meta:
        model=GuardianKids
        fields = "__all__"


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirmation = serializers.CharField(required=True)

    def validate(self, data):

        user = self.context['request'].user
        if not user.check_password(data['old_password']):
            raise serializers.ValidationError({'old_password': 'Wrong password.'})

        if data['new_password'] != data['new_password_confirmation']:
            raise serializers.ValidationError({'new_password_confirmation': 'Passwords do not match.'})

        return data

    def update(self, instance, validated_data):

        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance
    

class DriveProfileSerializer(serializers.ModelSerializer):
    i_profile = ProfileSerializer()

    class Meta:
        model = DriverDetails
        fields="__all__"


class DriverAttendenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DriverAttendance
        fields="__all__"

class GetDriverAttendenceSerialization(serializers.ModelSerializer):
    class Meta:
        model = DriverAttendance
        fields="__all__" 