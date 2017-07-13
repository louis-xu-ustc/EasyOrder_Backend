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
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.save()
        return instance

class DishSerializer(serializers.ModelSerializer):

    photo = Base64ImageField()

    class Meta:
        model = Dish
        fields = ('name', 'price', 'rate', 'photo', 'id')

    def create(self, validated_data):
        dish = Dish.objects.create(**validated_data)

        # must initialize new dish rate to 0.0 (prevent retailer fake score)
        dish.rate = 0.0

        return dish

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('twitterID', 'name')

class NotificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Notification
        fields = ('content',)

    def create(self, validated_data):
        return Notification.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance

