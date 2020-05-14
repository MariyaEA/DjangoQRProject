from rest_framework import serializers
from QR.models import Laptop, Owner

class OwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Owner
        fields = ['owner_first_name', 'phone_number', 'owner_id', 'image', 'occ', 'dept']

class LaptopSerializer(serializers.ModelSerializer):
    owner = OwnerSerializer()

    class Meta:
        model = Laptop
        fields = ['laptop_name', 'laptop_model', 'serial_number', 'owner']