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

# Tab 1 Methods

@csrf_exempt
def user_info(request):
    '''
    Create/Delete users, or get user list information
    '''

    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'Message': 'User Created'}, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        data = JSONParser().parse(request)
        if 'twitterID' not in data:
            return HttpResponse(status=404)
        user = User.objects.filter(twitterID=data['twitterID']).first()
        if user is None:
            return HttpResponse(status=404)
        user.delete()
        return HttpResponse(status=204)

    elif request.method == 'GET':
        res = []
        users = User.objects.all()
        for user in users:
            # only return users making orders
            if user.order.count() > 0:
                paid = user.order.first().paid
                res.append({'twitterID': user.twitterID, 'name': user.name, 'paid': paid})
        return JsonResponse(res, safe=False)

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

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

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

@csrf_exempt
def dish_detail(request, id):
    """
    Retrieve or delete a dish
    """
    index = int(id)
    dish = Dish.objects.filter(id=index).first()

    if dish is None:
        return JsonResponse({'Message':'Dish not found'}, status=404)

    if request.method == 'GET':
        serializer = DishSerializer(dish)
        return JsonResponse(serializer.data, safe=False)

    # PUT method not supported (to modify a dish, delete and post new one)

    elif request.method == 'DELETE':
        dish.delete()
        return JsonResponse({'Message':'Dish deleted'}, status=204)

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)


@csrf_exempt
def post_rate(request, id):
    """
    Update the rate of a dish
    """

    # Get dish from URI
    index = int(id)
    dish = Dish.objects.filter(id=index).first()
    if dish is None:
        return JsonResponse({'Message':'Dish not found'}, status=404)

    # Get vote user from JSON content
    data = JSONParser().parse(request)
    if 'user' not in data or 'rate' not in data:
        return JsonResponse({'Message':'Invalid Arguments'}, status=403)
    user = User.objects.filter(twitterID=data['user']).first()
    if user is None:
        return JsonResponse({'Message':'User not found'}, status=404)

    # Identify the vote object in DB
    vote = Vote.objects.filter(user=user, dish=dish).first()

    if request.method == 'PUT':
        try:
            # create vote if user not voted before
            if vote is None:
                vote = Vote.objects.create(user=user, dish=dish, rate=data['rate'])
                vote.save()

            # modify vote score if user has voted before towards the dish
            else:
                vote.rate = data['rate']
                vote.save()

        except Exception:
            return JsonResponse({'Message':'Rate vote cannot be created'}, status=403)

        update_dish_rate(dish)

        return JsonResponse({'Message':'Vote Created'}, status=201)

    elif request.method == 'DELETE':

        if vote is None:
            return HttpResponse(status=404)
        else:
            vote.delete()

        update_dish_rate(dish)

        return JsonResponse({'Message':'Rate vote deleted'}, status=204)

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

@csrf_exempt
def order_list(request):
    '''
    List all orders, add a new order, or clear the order List
    '''
    if request.method == 'GET':
        dishes = Dish.objects.all()
        data = []

        for dish in dishes:
            item = {
                'dish':dish.id,
                'num':dish.order.count(),
            }
            data.append(item)

        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        data = JSONParser().parse(request)
        if 'twitterID' not in data or 'amount' not in data or 'dish' not in data:
            return JsonResponse({'Message':'Invalid Arguments'}, status=403)

        user = User.objects.filter(twitterID=data['twitterID']).first()
        dish = Dish.objects.filter(id=data['dish']).first()
        if not user or not dish:
            return JsonResponse({'Message':'User or dish not found'}, status=404)

        try:
            order = Order.objects.create(user=user, dish=dish, amount=data['amount'], paid=False)
            order.save()
        except Exception:
            return JsonResponse({'Message':'Create order failed'}, status=403)

        return JsonResponse({'Message':'Order created'}, status=201)

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

def order_amount(request, id):
    '''
    Get the number of order based on dish id
    '''
    if request.method == 'GET':
        try:
            dish = Dish.objects.get(id=id)
        except ObjectDoesNotExist:
            return JsonResponse({'Message':'Invalid dish id'}, status=403)

        count = dish.order.count()
        return JsonResponse({'dish':id,'num':count})

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

# Tab2 Methods

@csrf_exempt
def notification_content_with_timestamp(request, timestamp):
    '''
    Get the notification if there is a new one
    '''
    notif = Notification.objects.all().first()
    if notif is None:
        return JsonResponse({'Message':'Server errors'}, status=500)

    if request.method == 'GET':
        last = datetime.datetime.fromtimestamp(int(timestamp))
        timezone = notif.modified_at.tzinfo
        last = last.replace(tzinfo=timezone)

        if last < notif.modified_at:
            data = NotificationSerializer(notif).data
            data['notification'] = True
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
    if request.method == 'GET':
        location = Location.objects.all().first()
        if location is None:
            return JsonResponse({'Message':'Server errors'}, status=500)

        serializer = LocationSerializer(location)
        return JsonResponse(serializer.data)

    elif request.method == 'PUT':
        location = Location.objects.all().first()
        if location is None:
            location = Location(latitude=0, longitude=0)

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
        return JsonResponse({'Message':'Reset all pickup locations'}, status=205)

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
        return JsonResponse({'Message':'Location not found'}, status=404)

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
        return JsonResponse({'Message':'Location deleted'}, status=204)

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

# Tab 3 Methods

@csrf_exempt
def order_pay(request):
    '''
    pay the order, one has to specify the user twitterID to complete the payment
    '''
    if request.method == 'PUT':

        data = JSONParser().parse(request)
        if 'twitterID' not in data:
            return JsonResponse({'Message':'User id not specified'}, status=403)
        user = User.objects.filter(twitterID=data['twitterID']).first()
        if user is None:
            return JsonResponse({'Message':'User id invalid'}, status=404)

        orders = user.order.all()
        pay = False
        for order in orders:
            if order.paid == False:
                pay = True
                order.paid = True
                order.save()

        if pay == False:
            return JsonResponse({'Message':'Payment has already been completed'})
        else:
            return JsonResponse({'Message':'Payment accepted'})

    return JsonResponse({'Message':'Method Not Allowed'}, status=405)

# Helper Function
def update_dish_rate(dish):
    """
    After user voted or canceled voting, the score of a dish should be updated
    """
    votes = list(dish.vote.all())
    if len(votes) != 0:
        new_score = float(sum(map(lambda x:x.rate, votes))) / len(votes)
        dish.rate = new_score
        dish.save()
