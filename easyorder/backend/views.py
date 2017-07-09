from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

import datetime

from .models import Location
from .serializers import LocationSerializer

# Create your views here.
def current_datetime(request):
    """
    Get current server time
    """
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

@csrf_exempt
def location_list(request):
    """
    List all location coordinate, or create a new location.
    """
    if request.method == 'GET':
        locations = Location.objects.all()
        serializer = LocationSerializer(locations, many=True)
        return JsonResponse(serializer.data, safe=False)
    
    elif request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = LocationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        return JsonResponse(serializer.errors, status=400)

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
