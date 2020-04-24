from django.urls import path

from . import views

urlpatterns = [
    path(r'apis/articles', views.ArticleListView.as_view()),
    path(r'apis/paragraphs', views.ParagraphListView.as_view()),
]
