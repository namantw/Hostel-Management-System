from django.contrib import admin
from django.urls import path
from selection import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='register'),
    path('reg_form/', views.register, name='reg_form'),
    path('login/', views.user_login, name='login'),
    path('warden_login/', views.warden_login, name='warden_login'),
    path('warden_dues/', views.warden_dues, name='warden_dues'),
    path('warden_add_due/', views.warden_add_due, name='warden_add_due'),
    path('warden_remove_due/', views.warden_remove_due, name='warden_remove_due'),
    path('warden_student_list/', views.warden_student_list, name='warden_student_list'),
    path('warden_student_list/change_student_details/<slug:enrollment_no>', views.change_student_details, name='change_student_details'),
    path('hostels/<slug:hostel_name>/', views.hostel_detail_view, name='hostel'),
    path('login/edit/', views.edit, name='edit'),
    path('login/select/', views.select, name='select'),
    path('logout/', views.logout_view, name='logout'),
    path('reg_form/login/edit/', views.edit, name='update'),
]
