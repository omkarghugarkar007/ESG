from django.db import models

# Create your models here.
class APIDocument(models.Model):
    api_document = models.FileField(upload_to='api_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.api_document) 