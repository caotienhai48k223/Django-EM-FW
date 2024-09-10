from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.user_register, name='register'),
    path('login/', views.user_login_df, name='login-default'),
    path('face-id/', views.user_login_fi, name='login-faceid'),
    path('logout/', views.user_logout, name='logout'),
    path('account/', views.user_account, name='account'),
    path('profile/<str:str>/', views.user_profile, name='profile'),
    path('create-faceid/', views.create_faceid, name='create-faceid'),
    path('classify/', views.find_user_view, name='classify'),
    path('check-in/', views.check_in, name='check-in'),
    path('check-out/', views.check_out, name='check-out'),
    path('time-sheet/', views.time_sheet, name='time-sheet'),
    path('time-sheet/user_id=<str:str>', views.time_sheet_emp, name='time-sheet')
]