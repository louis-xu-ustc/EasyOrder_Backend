from rest_framework import serializers
from backend.models import *
from drf_extra_fields.fields import Base64ImageField

import time

class TimestampField(serializers.Field):
    def to_representation(self, value):
        return int(time.mktime(value.timetuple()))

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

    modified_at = TimestampField(required=False)

    class Meta:
        model = Notification
        fields = ('content', 'modified_at')

    def create(self, validated_data):
        return Notification.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.save()
        return instance

class OrderSerializer(serializers.ModelSerializer):

    created_at = TimestampField(required=False)

    class Meta:
        model = Order
        fields = ('id', 'user', 'dish', 'amount', 'paid', 'created_at')

    def create(self, validated_data):
        order = Order.objects.create(**validated_data)
        order.paid = False
        return order

    def update(self, instance, validated_data):
        instance.paid = validated_data.get('paid', instance.paid)
        instance.save()
        return instance
