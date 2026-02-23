from django.urls import path
from . import views

app_name = "chatbot"

urlpatterns = [
    path("", views.chat_page, name="chat_page"),
    path("api/", views.chat_api, name="chat_api"),
    path("clear/<int:subject_id>/", views.clear_chat, name="clear_chat"),
    path("reading-mode/", views.reading_mode, name="reading_mode"),
    path("reading-mode/upload/", views.upload_scholar_doc, name="scholar_upload"),
    path("reading-mode/chat/", views.scholar_chat_api, name="scholar_chat_api"),
]
