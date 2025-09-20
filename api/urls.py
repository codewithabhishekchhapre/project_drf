from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.signup),
    path('login/',views.login),
    path('send-otp/',views.send_otp),
    path("upload/single/", views.upload_single_image, name="upload_single_image"),
    path("upload/multiple/", views.upload_multiple_images, name="upload_multiple_images"),
     path("users/", views.get_all_users, name="user-list"),
]