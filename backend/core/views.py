from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from . import errors, models, tasks, elasticsearch
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

        title = form.cleaned_data['title']
        content = form.cleaned_data['file'].read().decode('utf-8')

        article, created = models.Article.objects.get_or_create(title=title, content=content)
        if not created:
            return JsonResponse({
                'error': errors.TargetExistedError.serialize(),
            }, status=400)

        mode = request.GET.get('mode', '')
        if mode == 'direct':
            tasks.parse_article_directly(article.id)
            return JsonResponse({
                'data': {
                    'id': article.id,
                    'title': title,
                    'process_id': None,
                },
            }, status=201)
        else:
            async_task = tasks.parse_article.delay(article.id)
            return JsonResponse({
                'data': {
                    'id': article.id,
                    'title': title,
                    'process_id': async_task.id,
                },
            }, status=201)


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

        res = elasticsearch.es_client.search(
            index='paragraphs',
            body={
                'from': offset,
                'size': number,
                'query': {
                    'match': {
                        'content': query,
                    }
                },
                'highlight': {
                    'fields': {
                        'content': {}
                    }
                }
            }
        )

        return JsonResponse({
            'data': [
                {
                    'id': hit['_source']['id'],
                    'articleTitle': hit['_source']['articleTitle'],
                    'content': hit['_source']['content'],
                } for hit in res['hits']['hits']
            ]
        })
