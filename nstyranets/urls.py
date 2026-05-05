from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve as static_serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Static is served by Django only in dev; in prod WhiteNoise handles static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    # WhiteNoise serves STATIC; add an explicit view for MEDIA
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
    ]