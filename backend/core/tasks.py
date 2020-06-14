import re

import jieba.posseg
from celery import shared_task
from django.db import transaction

from . import models, elasticsearch


@shared_task
def parse_article(article_id: int):
    task = (
        # 將文章拆成段落並存進資料庫
            split_article_to_paragraphs_and_save.s(article_id=article_id) |
            # 將段落丟進 ES 以供查詢
            save_paragraphs_to_es.s()
    )()


def parse_article_directly(article_id: int):
    # 將文章拆成段落並存進資料庫
    paragraph_ids = split_article_to_paragraphs_and_save(article_id=article_id)
    # 將段落丟進 ES 以供查詢
    save_paragraphs_to_es(paragraph_ids)


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
def save_paragraphs_to_es(paragraph_ids: [int]):
    for paragraph in models.Paragraph.objects.filter(id__in=paragraph_ids):
        elasticsearch.es_client.create(
            index='paragraphs',
            id=paragraph.id,
            body={
                'id': paragraph.id,
                'articleTitle': paragraph.article.title,
                'content': paragraph.content,
            }
        )
