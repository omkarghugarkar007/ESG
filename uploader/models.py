from django.db import models
from django.http import response

# Create your models here.
class Document(models.Model):
    document = models.FileField(upload_to='docs/')
    reportYear = models.CharField(max_length=5, default='2020')

    def __str__(self):
        return str(self.document)

class Questionaire(models.Model):
    questionaire = models.FileField(upload_to='questionaires/')
    reportYear = models.CharField(max_length=5, default='2020')
    response = models.TextField()

    def __str__(self):
        return str(self.questionaire)

class ChatHistory(models.Model):
    name = models.CharField(max_length=200, default='Chat')
    response = models.TextField()

    def __str__(self):
        return str('Chat ' + str(self.pk))