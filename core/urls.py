from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.dashboard_view, name='dashboard'), 
    path('take-quiz/', views.take_quiz_view, name='take_quiz'),
    path('submit-quiz/', views.submit_quiz_view, name='submit_quiz'),
    path('results/', views.quiz_results_view, name='quiz_results'),
    path('history/', views.past_history_view, name='past_history'),
]