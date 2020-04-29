import re

import jieba.posseg
from django.db import transaction, DatabaseError
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from . import errors, models
from .form import UploadFileForm


class APIView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ArticleListView(APIView):

    @staticmethod
    def post(request):
        form = UploadFileForm(request.POST, request.FILES)
        if not form.is_valid():
            return JsonResponse({
                'error': errors.InvalidFormatError.serialize(),
            }, status=400)

        try:
            with transaction.atomic():
                title = form.cleaned_data['title']
                content = form.cleaned_data['file'].read().decode('utf-8')

                article, created = models.Article.objects.get_or_create(title=title)
                if not created:
                    return JsonResponse({
                        'error': errors.TargetExistedError.serialize(),
                    }, status=400)

                content = content.replace('\r\n', '\n')
                content = content.replace('\r', '\n')

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

                    for word, part_of_speech in jieba.posseg.cut(paragraph_text):
                        if part_of_speech in ['x', 'eng']:
                            continue

                        token, _ = models.Token.objects.get_or_create(word=word, part_of_speech=part_of_speech)
                        paragraph.token_set.add(token)

                return JsonResponse({
                    'data': {
                        'title': title,
                    },
                }, status=201)
        except DatabaseError:
            return JsonResponse({
                'error': errors.DatabaseError.serialize(),
            }, status=500)


class ParagraphListView(APIView):

    @staticmethod
    def get(request):

        query = request.GET.get('query', '')

        try:
            offset = int(request.GET.get('offset', '0'))
        except ValueError:
            return JsonResponse({
                'error': errors.InvalidFormatError.serialize(),
            }, status=400)

        try:
            number = int(request.GET.get('number', '20'))
        except ValueError:
            return JsonResponse({
                'error': errors.InvalidFormatError.serialize(),
            }, status=400)

        return JsonResponse({
            'data': [
                {
                    'id': paragraph.id,
                    'articleTitle': paragraph.article.title,
                    'content': paragraph.content,
                } for paragraph in models.Paragraph.objects.filter(token__word=query)[offset: offset + number]
            ]
        })
