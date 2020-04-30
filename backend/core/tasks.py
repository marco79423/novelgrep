import re

import celery
import jieba.posseg
from celery import shared_task
from django.db import transaction

from . import models


@shared_task
def parse_article(article_id: int):
    # 將文章拆成段落
    paragraph_ids = split_article_to_paragraphs_and_save(article_id=article_id)
    # 將段落拆成詞
    task = celery.group(split_paragraph_to_tokens_and_save.s(paragraph_id=paragraph_id) for paragraph_id in paragraph_ids)
    task.apply_async()


def parse_article_directly(article_id: int):
    # 將文章拆成段落
    paragraph_ids = split_article_to_paragraphs_and_save(article_id=article_id)
    # 將段落拆成詞
    for paragraph_id in paragraph_ids:
        split_paragraph_to_tokens_and_save(paragraph_id=paragraph_id)


@shared_task
def split_article_to_paragraphs_and_save(article_id: int):
    article = models.Article.objects.get(id=article_id)

    content = article.content
    content = content.replace('\r\n', '\n')
    content = content.replace('\r', '\n')

    with transaction.atomic():
        paragraph_ids = []
        for paragraph_text in re.split(r'(\n\n|[ \t]+)', content):
            paragraph_text = paragraph_text.strip().replace('\n', '')

            skip = True
            for _, part_of_speech in jieba.posseg.cut(paragraph_text):
                if part_of_speech not in ['x', 'eng']:
                    skip = False
                    break
            if skip:
                continue

            paragraph = article.paragraph_set.create(
                content=paragraph_text
            )

            paragraph_ids.append(paragraph.id)

    return paragraph_ids


@shared_task
def split_paragraph_to_tokens_and_save(paragraph_id: int):
    paragraph = models.Paragraph.objects.get(id=paragraph_id)

    with transaction.atomic():
        for word, part_of_speech in jieba.posseg.cut(paragraph.content):
            if part_of_speech in ['x', 'eng']:
                continue

            token, _ = models.Token.objects.get_or_create(word=word, part_of_speech=part_of_speech)
            paragraph.token_set.add(token)
