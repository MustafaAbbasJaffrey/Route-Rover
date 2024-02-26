from datetime import datetime
from django.urls import reverse
import magic
import phonenumbers
import re
import base64

from .models import Role
from django.apps import apps
from django.core.files.base import ContentFile
from .models import Profile
from django.db.models import Q
from rest_framework import status
from django.db.models import Sum
from datetime import datetime



def get_profiles(many = False, query = None, **kwargs):
    profile_qs = None
    if many == True:
       profile_qs = Profile.objects.filter(**kwargs)
        
    if many == False:
        profile_qs = Profile.objects.filter(**kwargs).first()
    
    if query is not None and many == True:
        profile_qs=Profile.objects.filter(query)
       
    return profile_qs

    
def get_roles(role):
    if role:
        user_role = Role.objects.filter(id = role).first()
        return user_role
    else:
        return Role.objects.all()
    
def get_user_roles():
    return list(Role.objects.values_list('name','display_name'))


def get_model_objects(app_label, model_name, list_ids):
    if list_ids == []:
        return None
    else:
        data = apps.get_model(app_label=app_label, model_name=model_name).objects.filter(id__in=list_ids)
    return data if data else None


def decode_base64_file(base64_file):

    # Remove the base64 prefix
    if base64_file.startswith('data:'):
        data = base64_file.split(';base64,', 1)[1]
    else:
        data = base64_file

    try:
        # Decode the Base64 data
        decoded_file = base64.b64decode(data)
    except UnicodeDecodeError:
        return None

    # Validate the file format based on the signature
    mime_type = magic.from_buffer(decoded_file, mime=True)
    file_extension = mime_type.split('/')[-1]
    if file_extension not in ['jpeg', 'jpg', 'png', 'pdf']:
        return None

    # Create a ContentFile from the decoded file
    file = ContentFile(decoded_file, name='file.' + file_extension)
    return file



def validate_phone_number(value, country_short_form):
    phone_number = re.sub(r'\D', '', value)
    try:
        parsed_number = phonenumbers.parse(phone_number, country_short_form)
        if not phonenumbers.is_valid_number(parsed_number):
            return {'success':False, 'message':'Invalid phone number.'}
        else:
            return {'success':True, 'message':'Correct number.'}
    except phonenumbers.NumberParseException:
        return {'success':False, 'message':'Invalid phone number format or country Code.'}
    


def compare_dates(date1, date2):
    format = '%Y-%m-%d'
    
    try:
        datetime1 = datetime.strptime(date1, format)
        datetime2 = datetime.strptime(date2, format)
    except ValueError:
        return -1

    if datetime1 == datetime2:
        return 1
    elif datetime1 > datetime2:
        return -1
    else:
        return 0
    

def get_time(date_time):
    formated_date_time = datetime.fromisoformat(str(date_time))            
    time = formated_date_time.strftime('%I:%M %p') 
    return time
