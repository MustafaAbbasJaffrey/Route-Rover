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
from rest_framework.generics import CreateAPIView, ListCreateAPIView, RetrieveAPIView,ListAPIView, RetrieveUpdateAPIView
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from datetime import datetime, timedelta




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
        resp = {'status':True,'status_code':status.HTTP_200_OK,'message':'Create Profile List','data':{}}
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


'''
    Kids Route
'''
class KidsView(generics.ListCreateAPIView):
    permission_classes = [IsGuardian] 
    serializer_class = KidsSerializer

    # Create New Kid
    def create(self, request, *args, **kwargs):

        kid_name = request.data['kid_name']
        kid_image = decode_base64_file(request.data['kid_image'])
        cards_media = request.data['kid_id_card']
        id_card_number = request.data['id_card_number']
  
        # Automic Transaction
        with transaction.atomic():
            # Get instances for create Kid Record(s)
            school = School.objects.get(pk=request.data['i_school'])
            rotue = Route.objects.get(pk=request.data['i_route'])
            school_class = SchoolClass.objects.get(pk=request.data['i_class'])
            guardian_detail = GuardianDetails.objects.get(i_profile=request.user.profile.pk)
        
            # Create Guardian Kid Record
            kid = GuardianKids.objects.create(
                                            kid_name=kid_name,
                                            kid_image=kid_image,
                                            i_school=school, 
                                            i_class=school_class, 
                                            i_route=rotue, 
                                            i_guardian_profile=guardian_detail,
                                            id_card_number=id_card_number,
                                            )
            
            # There will be multiple cards for single student
            # so we are using loops here to updated indiviudal card related student
            for card_media in cards_media:
                card = decode_base64_file(card_media)
                KidsIdCard.objects.create(i_kids=kid, 
                                    card_media=card)

        # Response Data
        self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": "Kids has been created", "data":request.data}
        
        return Response(self.resp, status=status.HTTP_201_CREATED)

    # Get all students related to Guardian
    def get(self, request, *args, **kwargs):

        self.resp = {}
        kids = []

        # Creating Dict By using Kids Data
        for kid in GuardianKids.objects.filter(i_guardian_profile__i_profile = request.user.profile.pk):
            
            # Fetch Kid Id Cards
            # There will be multiple cards
            # thats why we are using list comporehensive here
            kid_id_cards = KidsIdCard.objects.filter(i_kids=kid.pk)
            cards = [{"card_id":kid_id_card.pk,"card_media":kid_id_card.get_card_media()} for kid_id_card in kid_id_cards]

            # Data send to client
            data = {
                "id_card_number":kid.id_card_number,
                "kid_id":kid.pk,
                "kid_name" : kid.kid_name,
                "route": kid.i_route.route_name,
                "school":kid.i_school.school_name,
                "class":kid.i_class.class_name,
                "guardian":kid.i_guardian_profile.i_profile.user.first_name,
                "kid_image":kid.get_kid_image(),
                "kid_id_card":cards
            }
            kids.append(data)

        # Response Data
        self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": "Guardian's kids List", "data":kids}

        return Response(self.resp, status=status.HTTP_200_OK)

# Retrive Delete are working Correctly 
# Update is remaining to test
class KidsViewUpdate(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsGuardian] 
    serializer_class = KidsUpdateSerializer
    queryset = GuardianKids.objects.all()

    # Get Individaul Kid
    def get(self, request, *args, **kwargs):

        # Select Those kids which are associated by its Guardian else return 404 
        kid = get_object_or_404(GuardianKids, pk=kwargs['pk'],
                                 i_guardian_profile__i_profile = request.user.profile.pk)
        
        # Fetch All kid id cards
        kid_id_cards = KidsIdCard.objects.filter(i_kids=kid.pk)
        cards = [{"card_id":kid_id_card.pk,"card_media":kid_id_card.get_card_media()} for kid_id_card in kid_id_cards]
        
        data = {
            "id":kid.id,
            "kid_name":kid.kid_name,
            "kid_image":kid.get_kid_image(),
            "class":kid.i_class.class_name,
            "school":kid.i_school.school_name,
            "route":kid.i_route.route_name,
            "id_card_number":kid.id_card_number,
            "kid_id_card":cards
        }

        # Response Data
        self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": "Kid data", "data":data}

        return Response(self.resp, status=status.HTTP_200_OK)
    
    # Update Individual Kid
    def update(self, request, *args, **kwargs):

        instance = self.get_object()

        # Select kid which are associated by its Guardian else return 404 Error
        kid_data = get_object_or_404(GuardianKids, pk=instance.pk,
                                                    i_guardian_profile__i_profile = request.user.profile.pk)
        
        school_isntance = School.objects.get(pk=request.data['school_id'])
        class_instance = SchoolClass.objects.get(pk=request.data['class_id'])
        route_isntance = Route.objects.get(pk=request.data['route_id'])

        # get previous image name for deleting purpose
        previous_image_path = kid_data.kid_image.name
        
        with transaction.atomic(): 

            kid_data.kid_name = request.data['kid_name']
            kid_data.id_card_number = request.data['id_card_number']
            kid_data.kid_image = decode_base64_file(request.data['kid_image'])
            kid_data.i_school = school_isntance
            kid_data.i_class = class_instance
            kid_data.i_route = route_isntance
            kid_data.i_guardian_profile = GuardianDetails.objects.get(i_profile=request.user.profile.pk)
            kid_data.save()
            
            # Update Kid ID Card
            for id_card in request.data['kid_id_card']:
                card = decode_base64_file(id_card)
                KidsIdCard.objects.create(i_kids=kid_data, 
                                    card_media=card)
            
            # Delete Id card From the database
            for card_id in request.data['deleted_card']:
                card = KidsIdCard.objects.get(pk=card_id)
                filepath = os.path.join(settings.MEDIA_ROOT, card.card_media.name)
                os.remove(filepath)
                card.delete()
                
            # Delete Previous image from os
            os.remove(os.path.join(settings.MEDIA_ROOT,previous_image_path))
            
        # Response Data
        self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": "Kids data has been updated", "data":request.data}

        return Response(self.resp, status=status.HTTP_200_OK)


'''
    ProfileView is responsible to update and fetch User Profile data from
    User, Profile and guardian_details models  
'''
# Note: This view use request.FILES not Base
class ProfileView(generics.ListCreateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    # This is get method which is responsible to fetch 
    # full_name, main_image, phone_number and home_address
    def get(self, request, *args, **kwargs):
        profile = Profile.objects.get(user=request.user)
        guardian_detail = GuardianDetails.objects.get(i_profile=profile)

        data = {}
        data['full_name'] = profile.get_full_name()
        data["main_image"] = profile.get_main_image()
        data['phone_number'] = str(profile.phone_number)
        data['home_address'] = guardian_detail.home_address

        # Response Data
        self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": "Profile Data", "data":data}

        return Response(self.resp, status=status.HTTP_200_OK)
    
    # This is Update method not create function
    # This is because we dont need to pass query params 
    # We know using using request object which user is login.
    def create(self, request, *args, **kwargs):
        user = User.objects.get(pk=request.user.pk)
        profile = Profile.objects.get(user=request.user)
        guardian_detail = GuardianDetails.objects.get(i_profile=profile)

        # Automic Transaction
        with transaction.atomic():
            # Update Full name of user profile
            user.first_name = request.data['full_name']
            user.save()

            # Update main_image and phone number on prfile
            previous_image_path = profile.main_image.name
            profile.main_image = request.FILES.get('main_image')
            profile.phone_number = request.data['phone_number']
            profile.save()

            # Remove previous image from os 
            os.remove(os.path.join(settings.MEDIA_ROOT,previous_image_path))
            
            # update home_address in guardian details
            guardian_detail.home_address = request.data['home_address']
            guardian_detail.save()

        image = request.data.pop('main_image')
        data = request.data
        data['main_image'] = profile.get_main_image()
        # Response Data
        self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": "Profile Data", "data":request.data}
        
        return Response(self.resp, status=status.HTTP_200_OK)
    


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        print(request.data)

        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        serializer.update(request.user, serializer.validated_data)

        # Generate a new refresh token
        refresh = RefreshToken.for_user(request.user)

        
        
        resp = Response({ 'status': True,
                          'status_code':status.HTTP_200_OK,
                          "message": "Password changed successfully",
                          'refresh': str(refresh)},
                             status=status.HTTP_200_OK)

        return resp
    

class DrivedDetailView(CreateAPIView):
    # Its Allow Any for All for just testing purpose
    # But its allow only for Admin
    permission_classes = [AllowAny]
    serializer_class = DriveProfileSerializer
    queryset = DriverDetails.objects.all()

    def create(self, request, *args, **kwargs):
        
        # Its create three models data
        # 1. User
        # 2. Profile
        # 3. Drvier Detail
        with transaction.atomic():
            user = ""
            try:
                user_data = {}
                user_data['first_name'] = request.data['full_name']
                user_data['username'] = request.data['email_address']
                user_data['email'] = request.data['email_address']
                user = User(**user_data)
                user.set_password(request.data['password'])
                request.data.pop('password')
                user.save()
            except Exception as e:
                print(e)
                return Response({"status": False, "status_code":status.HTTP_403_FORBIDDEN, "message": "Email address already Registered", "data":""})

            profile_data = {}
            profile_data['user'] = user
            profile_data['role'] = Role.objects.get(pk=1)
            profile_data['join_date'] = request.data['date_of_employement']
            profile_data['phone_number'] = request.data['phone_number']
            profile_data['main_image'] = decode_base64_file(request.data['main_image'])
            profile = Profile.objects.create(**profile_data)

            driver_data = {}
            driver_data['i_profile'] = profile
            driver_data['license_number'] = request.data['license_number']
            driver_data['license_validity'] = request.data['license_validity']
            driver_data['vehicle_make'] = request.data['vehicle_make']
            driver_data['vehicle_model'] = request.data['vehicle_model']
            driver_data['vehicle_registration'] = request.data['vehicle_registration']
            driver_data['home_address'] = request.data['home_address']
            driver_data['authorized_schools'] = School.objects.get(pk=request.data['authorized_schools'])
            driver_data['assign_route'] = Route.objects.get(pk=request.data['assign_route'])

            DriverDetails.objects.create(**driver_data)

            request.data['main_image'] = profile.get_main_image()

        self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": "Driver has been created", "data":request.data}

        return Response(self.resp, status=status.HTTP_201_CREATED)

'''
    Time In View
    This View is Responsible for Driver Time In
    If driver want to time in 2 time in a single day
    This view won't allow it.
'''
class TimeInView(CreateAPIView):
    permission_classes = [IsDriver]
    serializer_class = DriveProfileSerializer
    queryset = DriverAttendance.objects.all()

    def create(self, request, *args, **kwargs):

        # Fetch last Record of Driver Attendance Detail
        driver = DriverDetails.objects.get(i_profile=request.user.profile)
        last_date = DriverAttendance.objects.filter(driver=driver).last()

        time_in = request.data['time_in']
        date_only = datetime.strptime(time_in, "%Y-%m-%d %H:%M:%S").date()

        # Check either its first time for client to insert time_in or driver want to insert old date time_in
        if last_date == None or compare_dates(str(date_only), str(last_date.current_date)) == -1:
            DriverAttendance.objects.create(driver=driver, time_in=time_in, current_date=date_only)
        else:
            # Thi condition is because we have to pass two different response to the client
            if compare_dates(str(date_only), str(last_date.current_date)) == 1:
                self.resp = {"status": False, "status_code":status.HTTP_405_METHOD_NOT_ALLOWED, "message": f"Driver is already time in", "data":""}
            else:
                self.resp = {"status": False, "status_code":status.HTTP_405_METHOD_NOT_ALLOWED, "message": f"Date has been passed", "data":""}
            return Response(self.resp, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        # Successfully time_in
        self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": f"Time in at {time_in} on {date_only}", "data":""}
        return Response(self.resp, status=status.HTTP_200_OK)

'''
    Time Out View
    This view is responsible for driver time out
    If driver want to insert time out when they are not time in
    This view wont allow it
'''
class TimeOutView(CreateAPIView):
    permission_classes = [IsDriver]
    serializer_class = DriveProfileSerializer
    queryset = DriverAttendance.objects.all()

    def create(self, request, *args, **kwargs):
        driver = DriverDetails.objects.get(i_profile=request.user.profile)

        time_out = request.data['time_out']
        date_only = datetime.strptime(time_out, "%Y-%m-%d %H:%M:%S").date()

        # Check if driver has time_in ot not
        if DriverAttendance.objects.filter(Q(driver=driver), Q(current_date=date_only)).exists():
            today_attendance = DriverAttendance.objects.filter(driver=driver, current_date=date_only)
            today_attendance.update(time_out=time_out)
        else:
            self.resp = {"status": False, "status_code":status.HTTP_405_METHOD_NOT_ALLOWED, "message": f"You have to Time In First", "data":""}
            return Response(self.resp, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": f"Time out at {time_out} on {date_only}", "data":""}
        return Response(self.resp, status=status.HTTP_200_OK)

'''
    Get Attendance View
    This View is responsible for multiple work  
    If no query parameter pass it return current Year Record
    If month query parameter pass it return selected month and current year record
    if year query parameter pass it will return selected year record
    if month and year both pased as a query parameter it will return selectd month and seleted year record
'''
class GetDriverAttendence(ListAPIView):
    permission_classes = [IsDriver]
    serializer_class = GetDriverAttendenceSerialization
    queryset = DriverAttendance.objects.all()

    def get(self, request, *args, **kwargs):
        
        # If there is some query parameter is available in url or not
        if ('month' in request.query_params and 'year' in request.query_params) or 'month' in request.query_params:

            # Get query Parameter from request object if its not available then its send None
            selected_month = int(request.query_params.get('month'))
            selected_year = int(request.query_params.get('year')) if request.query_params.get('year') != None else None

            # Fetch Month and year record
            data = self.attendance_for_month(month=selected_month, year=selected_year)

            self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": f"Driver Attendance", "data":data}
            return Response(self.resp, status=status.HTTP_200_OK)
        elif 'last' in request.query_params:
            data = self.attendance_limit(int(request.query_params.get('last')))

            self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": f"Last {request.query_params.get('last')} Driver Attendance", "data":data}
            return Response(self.resp, status=status.HTTP_200_OK)

        present = 0
        absent = 0

        data = {}
        data['calenader'] = {}
        
        # Check there is any query parameter pass from client or not if not its send current year
        selected_year = int(request.query_params.get('year')) if request.query_params.get('year') != None else datetime.now().year
        start_date = datetime(selected_year, 1, 1)
        end_date = datetime(selected_year, 12, 31)

        # This while loop is responsible to genereate whole record (month and year)
        current_date = start_date
        while current_date <= end_date:
            formatted_date = current_date.strftime("%Y-%m-%d")

            # date is greather than current date -> status will be empty
            if current_date > datetime.today():
                data['calenader'][formatted_date] = {"time_in": None, "time_out": None, "status": ""}
            else:
                # If there is saturday or sunday status will be holiday
                if current_date.weekday() == 5 or current_date.weekday() == 6:
                    data['calenader'][formatted_date] = {"time_in": None, "time_out": None, "status": "Holiday"}
                else:
                    # if date is previous date -> status will be absent
                    data['calenader'][formatted_date] = {"time_in": None, "time_out": None, "status": "Absent"}
                    absent += 1
            
            current_date += timedelta(days=1)

        # Get attendance record from database
        driver = DriverDetails.objects.get(i_profile=request.user.profile)
        attendance = DriverAttendance.objects.filter(driver=driver)

        # attach DB record in current table which is genereated above
        for i in list(attendance):
            if str(i.current_date) in data['calenader']:
                time_in = get_time(i.time_in)
                time_out = get_time(i.time_out)
                data['calenader'][str(i.current_date)] = {"time_in":time_in, "time_out":time_out, "status":"Present"}
                present += 1

        # calcualte Present and absent Record
        data['Attendance']= {
                "Present":present,
                "Absent":absent         
            }

        self.resp = {"status": True, "status_code":status.HTTP_200_OK, "message": f"Driver Attendance", "data":data}
        return Response(self.resp, status=status.HTTP_200_OK)
    

    '''
        This method is responsible to generate custom calendar to the client
        By passing month and year as a parameter in this method
        This method wont be called if month is not in query parameters
    '''
    def attendance_for_month(self, month=None, year=None):
        absent = 0
        present = 0

        # If one of the query parameter is not passed in to this method it will because current month and current year
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        # it will calculate how many days in particular time which is give by client
        num_days_in_month = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day

        data = {}
        data['calenader'] = {}
        for day in range(1, num_days_in_month + 1):
            date = datetime(year, month, day)
            formatted_date = date.strftime("%Y-%m-%d")

            # date is greather than current date -> status will be empty
            if date.date() > datetime.today().date():
                data['calenader'][formatted_date] = {"time_in": None, "time_out": None, "status": ""}
            else:
                # If there is saturday or sunday status will be holiday
                if date.weekday() == 5 or date.weekday() == 6:
                    data['calenader'][formatted_date] = {"time_in": None, "time_out": None, "status": "Holiday"}
                else:
                    # if date is previous date -> status will be absent
                    data['calenader'][formatted_date] = {"time_in": None, "time_out": None, "status": "Absent"}
                    absent += 1

        # Get attendance record from database
        driver = DriverDetails.objects.get(i_profile=self.request.user.profile)
        attendance = DriverAttendance.objects.filter(driver=driver)

        # attach DB record in current table which is genereated above
        for i in list(attendance):
            if str(i.current_date) in data['calenader']:
                time_in = get_time(i.time_in)
                time_out = get_time(i.time_out)
                data['calenader'][str(i.current_date)] = {"time_in":time_in, "time_out":time_out, "status":"Present"}
                present += 1

        # calcualte Present and absent Record
        data['Attendance']= {
                "Present":present,
                "Absent":absent         
            }

        return data
    

    '''
        This method in responsible send last (given by client as a query parameter) Attendance record
    '''
    def attendance_limit(self, limit):
        data = {}
        data['calenader'] = {}

        present = 0
        absent = 0

        current_date = datetime.today()
        while len(data["calenader"]) < int(limit):
            formatted_date = current_date.strftime("%Y-%m-%d")

            if current_date > datetime.today():
                data['calenader'][formatted_date] = {"time_in": None, "time_out": None, "status": ""}
            else:
                # If there is saturday or sunday it will not include in the record
                if current_date.weekday() == 5 or current_date.weekday() == 6:
                    pass
                else:
                    # if date is previous date -> status will be absent
                    data['calenader'][formatted_date] = {"time_in": None, "time_out": None, "status": "Absent"}
                    absent += 1
            current_date+=timedelta(days=-1)
        
        # Get attendance record from database
        driver = DriverDetails.objects.get(i_profile=self.request.user.profile)
        attendance = DriverAttendance.objects.filter(driver=driver)

        # attach DB record in current table which is genereated above
        for i in list(attendance):
            if str(i.current_date) in data['calenader']:
                time_in = get_time(i.time_in)
                time_out = get_time(i.time_out)

                data['calenader'][str(i.current_date)] = {"time_in":time_in, "time_out":time_out, "status":"Present"}
                present += 1

        data['Attendance']= {
            "Present":present,
            "Absent":absent         
        }
        return data
        
