from rest_framework import serializers
from backend.models import *
from drf_extra_fields.fields import Base64ImageField

class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ('latitude', 'longitude')

    def create(self, validated_data):
        return Location.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.latitude = validated_data.get('lantitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.save()
        return instance

class DishSerializer(serializers.ModelSerializer):

    photo = Base64ImageField()

    class Meta:
        model = Dish
        fields = ('name', 'price', 'rate', 'rateNum', 'photo')

    def create(self, validated_data):
        return Dish.objects.create(**validated_data)
