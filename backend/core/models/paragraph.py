from django.db import models

from core.models.article import Article


class Paragraph(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField(null=False)
