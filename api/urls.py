from django.urls import path
from . import views

urlpatterns = [
    path('esgreports/upload/', views.uploadFile, name='uploadFile'),
    path('esgreports/retrieve/', views.getDocs, name='getDocs'),
    path('questionnaire/generatefirstdraft/pdf/', views.uploadQuestionnaire, name='uploadQuestionnaire'),
    path('questionnaire/generatefirstdraft/generateAnswer/', views.getSpecificQuestionResponse, name='getSpecificQuestionResponse'),
    path('firstdraftreport/download/result/<str:reportYear>/', views.getReport, name='getReport'),
    path('questionnaire/generatefirstdraft/pdf/<str:reportYear>/<str:taskId>/status/', views.getReportStatus, name='getReportStatus'),
]