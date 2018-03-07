from django.urls import path

from django.conf import settings
from django.conf.urls import url, include
from rest_framework import response, schemas
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import CoreJSONRenderer
from rest_framework_swagger.renderers import OpenAPIRenderer
from rest_framework_swagger.renderers import SwaggerUIRenderer

from biz.api import urls as api_urls

grouped_url_patterns = {
#    'base_patterns': [
#        url(r'^status/', include('health.urls')),
#    ],
    'biz_patterns': [
        url(r'^biz/', include(api_urls.urls)),
    ],
}

@api_view()
@renderer_classes([SwaggerUIRenderer, OpenAPIRenderer, CoreJSONRenderer])
def biz_schema_view(request):
    generator = schemas.SchemaGenerator(
        title='BedrijfsInvesteringsZones',
        patterns=grouped_url_patterns['biz_patterns']
    )
    return response.Response(generator.get_schema(request=request))


urlpatterns = [url('^biz/docs/api-docs/biz/$',
                   biz_schema_view),
               ] + [url for pattern_list in grouped_url_patterns.values()
                    for url in pattern_list]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns.extend([
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ])