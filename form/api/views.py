from rest_framework import status
from django.shortcuts import render
from .serializers import LaptopSerializer
from rest_framework.response import Response

from rest_framework.decorators import api_view
from QR.models import Laptop

# Create your views here.
@api_view(['GET'])
def search(request, laptop_id):
    try:
        laptop = Laptop.objects.get(id=laptop_id)
        laptop_serializer = LaptopSerializer(laptop)
        return Response(laptop_serializer.data, status=200)

    except Laptop.DoesNotExist:
        return Response('Laptop does not exist.', status=status.HTTP_404_NOT_FOUND)

