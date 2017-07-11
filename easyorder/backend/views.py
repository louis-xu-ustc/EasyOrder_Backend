from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

import datetime
from django.utils.dateformat import format

from .models import *
from .serializers import *

# Create your views here.
def current_datetime(request):
    """
    Get current server time
    """
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

@csrf_exempt
def dish_list(request):
    '''
    List all dish in menu, or create a new dish
    '''
    if request.method == 'GET':
        dishes = Dish.objects.all()
        serializer = DishSerializer(dishes, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = DishSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'Message': 'Dish Created'}, status=201)
        return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def notification_content_with_timestamp(request, timestamp):
    '''
    Get the notification if there is a new one
    '''
    try:
        notif = Notification.objects.all().first()
    except IndexError:
        return JsonResponse({'Message':'Server errors'}, status=500)

    if request.method == 'GET':
        last = datetime.datetime.fromtimestamp(int(timestamp))
        timezone = notif.modified_at.tzinfo
        last = last.replace(tzinfo=timezone)

        if last < notif.modified_at:
            data = NotificationSerializer(notif).data
            data['notification'] = True
            data['modified_at'] = format(notif.modified_at, 'U')
            return JsonResponse(data)
        else:
            return JsonResponse({'notification':False})

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

@csrf_exempt
def notification_content(request):
    '''
    Update/Get the notification
    '''
    if request.method == 'GET':

        notif = Notification.objects.all().first()
        if notif is None:
            return JsonResponse({'notification':False})

        data = NotificationSerializer(notif).data
        data['notification'] = True
        data['modified_at'] = format(notif.modified_at, 'U')
        return JsonResponse(data)
    elif request.method == 'PUT':
        notif = Notification.objects.all().first()
        if notif is None:
            notif = Notification(content='dummy content')

        data = JSONParser().parse(request)
        serializer = NotificationSerializer(notif, data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

@csrf_exempt
def current_location(request):
    '''
    Get/Update the cureent retailer location
    '''
    try:
        location = Location.objects.all().first()
    except IndexError:
        return JsonResponse({'Message':'Server errors'}, status=500)

    if request.method == 'GET':
        serializer = LocationSerializer(location)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = LocationSerializer(location, data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

@csrf_exempt
def pickup_location_list(request):
    """
    List all pickup location coordinates, or insert a new location.
    """
    if request.method == 'GET':
        locations = Location.objects.all()[1:]
        serializer = LocationSerializer(locations, many=True)
        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = LocationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        first = Location.objects.all().first()
        Location.objects.exclude(id=first.id).delete()
        return HttpResponse(status=204)

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

@csrf_exempt
def location_detail(request, id):
    """
    Retrieve, update or delete a location coordinate.
    """
    index = int(id)
    count = Location.objects.count()
    if index < count:
        location = Location.objects.all()[index]
    else:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = LocationSerializer(location)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)
        serializer = LocationSerializer(location, data=data)

        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        location.delete()
        return HttpResponse(status=204)

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)
