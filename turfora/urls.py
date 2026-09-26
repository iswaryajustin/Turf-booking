"""
URL configuration for turfora project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from turforaapp import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.landing,name='landing'),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('home/<int:id>/',views.home,name='home'),
    path('userprofile/<int:id>/',views.userprofile,name='userprofile'),
    path('editprofile/<int:id>/',views.editprofile,name='editprofile'),
    path('logout_user/',views.logout_user,name='logout_user'),
    path('admin_login/',views.admin_login,name='admin_login'),
    path('admin_dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('manageusers/',views.manageusers,name='manageusers'),
    path('block_user/<int:id>/', views.block_user, name='block_user'),
    path('unblock_user/<int:id>/', views.unblock_user, name='unblock_user'),
    path('deleteuser/<int:id>/', views.deleteuser, name='deleteuser'),
    path('viewuser/<int:id>/', views.viewuser, name='viewuser'),
    path('edituser/<int:id>/', views.edituser, name='edituser'),
    path('notifications/', views.notifications, name='notifications'),
    path('manageturfs/', views.manageturfs, name='manageturfs'),
    path('viewturf/<int:id>/', views.viewturf, name='viewturf'),
    path('editturf/<int:id>/', views.editturf, name='editturf'),
    path('delete_turf/<int:id>/',views.delete_turf,name='delete_turf'),
    path('turfdetails/<int:id>/',views.turfdetails,name='turfdetails'),
    path( 'booknow/<int:user_id>/<int:turf_id>/',views.booknow,name='booknow'),
    path( 'confirmbooking/',views.confirmbooking,name='confirmbooking'),
    path('mybookings/<int:id>/',views.mybookings,name='mybookings'),
    path('cancel_booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('booking_history/<int:id>/',views.booking_history,name='booking_history'),
    path('reviews_ratings/', views.reviews_ratings, name='reviews_ratings'),
    path( 'payment/<int:booking_id>/', views.payment, name='payment'),
    path('payment_success/<int:booking_id>/',views.payment_success,name='payment_success'),
    path('activate/<int:turf_id>/', views.activate_turf, name='activate_turf'),
    path('deactivate/<int:turf_id>/', views.deactivate_turf, name='deactivate_turf'),
    path('admin_availability/', views.admin_availability, name='admin_availability'),
    path('turf_availability/<int:turf_id>/',views.turf_availability,name='turf_availability'),
    path('add_slot/<int:turf_id>/',views.add_slot,name='add_slot'),
    path('block_slot/<int:turf_id>/',views.block_slot,name='block_slot'),
    path('update_turf_hours/<int:turf_id>/',views.update_turf_hours,name='update_turf_hours'),
    path('set_holiday/<int:turf_id>/',views.set_holiday,name='set_holiday'),
    path('managebookings/',views.managebookings,name='managebookings'),
    path('update_booking_status/<int:booking_id>/<str:status>/',views.update_booking_status,name='update_booking_status'),
    path( 'admin_booking_detail/<int:booking_id>/', views.admin_booking_detail, name='admin_booking_detail'),
    path('managepayments/',views.managepayments,name='managepayments'),
    path('admin_payment_detail/<int:payment_id>/',views.admin_payment_detail,name='admin_payment_detail'),
    path('admin_reviews_ratings/',views.admin_reviews_ratings,name='admin_reviews_ratings'),
    path('admin_delete_review/<int:review_id>/',views.admin_delete_review,name='admin_delete_review'),
    path('notifications/<int:id>/',views.notifications,name='notifications'),
    path('notifications/mark-all-read/',views.mark_all_notifications_read,name='mark_all_notifications_read'),
    path('notifications/clear-all/',views.clear_all_notifications,name='clear_all_notifications'),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)