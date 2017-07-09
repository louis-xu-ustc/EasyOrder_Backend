from rest_framework import serializers
from backend.models import Location

class LocationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Location
        fields = ('latitude', 'longitude')

    def create(self, validated_data):
        return Location.objects.create(**validated_data)

    def update(self, instance, valiadated_data):
        instance.latitude = validated_data.get('lantitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.save()
        return instance
