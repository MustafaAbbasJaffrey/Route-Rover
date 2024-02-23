from .views import *
from django.urls import include, path
from django_rest_authentication.authentication.django_rest_passwordreset.urls import (
    urlpatterns as password_reset_urls,
)

urlpatterns = [
    path("signup/", GuardianRegisterView.as_view(), name="signup"),
    path("signin/", SignInView.as_view(), name="signin"),
    path('social_auth/', SocialAuthenticationView.as_view(), name = "social_auth"),
    path('create_profile/', CreateProfileView.as_view(), name='create_profile'),
    path('get_schools/', GetSchools.as_view(), name='get_schools'),
    path('get_school_class/', GetSchoolsClass.as_view(), name='get_school_class'),
    path('get_route/', GetRoute.as_view(), name='get_route'),


    path('kids_view/', KidsView.as_view(), name='kids_view'),
    path('kids_view/<int:pk>', KidsViewUpdate.as_view(), name="kids_update_view"),
    path('profile/', ProfileView.as_view(), name="profile"),
    path('changePasswordView/', ChangePasswordView.as_view(), name="change_password"),
    path('driver_profile/', DrivedDetailView.as_view(), name="driver_detail"),
    path('time_in/', TimeInView.as_view(), name="time_in"),
    path('time_out/', TimeOutView.as_view(), name="time_out"),
]


