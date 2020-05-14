from django.urls import path
from .views import search

app_name = 'api'


urlpatterns = [
    path('search/<laptop_id>/', search, name='search'),
  
]
# No not here the other urls.py file inside form