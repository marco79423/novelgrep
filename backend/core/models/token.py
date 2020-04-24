from django.db import models

from core.models import Paragraph


class Token(models.Model):
    word = models.CharField(max_length=16)
    part_of_speech = models.CharField(max_length=4)
    paragraphs = models.ManyToManyField(Paragraph)
