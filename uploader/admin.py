from django.contrib import admin
from .models import Document, ChatHistory, Questionaire

# Register your models here.
admin.site.register(Document)
admin.site.register(ChatHistory)
admin.site.register(Questionaire)