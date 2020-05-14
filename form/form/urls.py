from django.urls import path, include, re_path
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static 

from .views import index



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', index),
    path('qr/', include('QR.urls')),
    path('api/', include('api.urls')),
    re_path(r'^accounts/', include('allauth.urls')),
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
