from rest_framework import serializers
from .models import Photos


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photos
        fields = ('photo',)
