from django.urls import path
from . import views

urlpatterns = [
    path('', views.homeView, name='homeView'),
    path('upload/', views.uploadView, name='uploadView'),
    path('delete-all/', views.deleteView, name='deleteView'),
    path('upload-questionaire/', views.uploadQuestionaireView, name='uploadQuestionaireView'),
    path ('report/<str:pk>/', views.reportView, name='reportView'),
    path ('chat/<str:pk>/', views.chatView, name='chatView'),
]