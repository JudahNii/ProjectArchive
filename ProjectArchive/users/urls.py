from django.urls import path

from .views import (
        homeview, landing_page, logoutview, login_view, upload_excel, 
        load_departments, load_programmes, load_supervisors,
        StudentCreateView, StudentUpdateView, StudentListView, InitStudentUpdateView,
        search_bar,
        # hod_landing_page, 
    )

urlpatterns = [
    path('login/', login_view, name='login'),
    path('home/', homeview, name='home'),
    path('logout/', logoutview, name='logout'),
    path('create_student/', StudentCreateView.as_view(), name='create_student'),
    path('update_student/<str:username>/', StudentUpdateView.as_view(), name='update_student'),
    path('init_update_student/<str:username>/', InitStudentUpdateView.as_view(), name='init_update_student'),
    path('upload_excel/', upload_excel, name='upload_excel'),
    path('students/', StudentListView.as_view(), name='student_list'),
    path('load_departments/', load_departments, name='load_departments'),
    path('load_programmes/', load_programmes, name='load_programmes'),
    path('load_supervisors/', load_supervisors, name='load_supervisors'),
    path('search', search_bar, name='search'),
]

