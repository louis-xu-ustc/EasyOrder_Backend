from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

import datetime
from pytz import utc, timezone
from django.utils.dateformat import format

from .models import *
from .serializers import *

import braintree
import os

braintree.Configuration.configure(braintree.Environment.Sandbox,
                                  merchant_id=os.environ['BT_MERCHANT_ID'],
                                  public_key=os.environ['BT_PUBLIC_KEY'],
                                  private_key=os.environ['BT_PRIVATE_KEY'])

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
        if 'twitterID' not in data:
            return JsonResponse({'message': 'Input incorrect'}, status=400)
        if User.objects.filter(twitterID=data['twitterID']).first() is not None:
            return JsonResponse({'message': 'User already exist'}, status=200)
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'message': 'user created'}, status=201)
        return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':
        data = JSONParser().parse(request)
        if 'twitterID' not in data:
            return JsonResponse({'message': 'Input incorrect'}, status=400)
        user = User.objects.filter(twitterID=data['twitterID']).first()
        if user is None:
            return JsonResponse({'message': 'User not found'}, status=404)
        user.delete()
        return JsonResponse({'message': 'User deleted'}, status=204)

    elif request.method == 'GET':
        res = []
        users = User.objects.all()
        for user in users:
            # only return users making orders
            orders = get_effective_orders(user)
            if orders.count() > 0:
                is_paid = True
                for order in orders.all():
                    if not order.paid:
                        is_paid = False
                res.append({'twitterID': user.twitterID, 'name': user.name, 'paid': is_paid})
        return JsonResponse(res, safe=False)

    return JsonResponse({'message':'method not allowed'}, status=405)

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
            return JsonResponse({'message': 'dish created'}, status=201)
        return JsonResponse(serializer.errors, status=400)
    elif request.method == 'DELETE':
        Dish.objects.all().delete()
        return JsonResponse({'message':'clear all dishes'}, status=205)

    return JsonResponse({'message':'method not allowed'}, status=405)

@csrf_exempt
def dish_detail(request, id):
    """
    Retrieve or delete a dish
    """
    index = int(id)
    dish = Dish.objects.filter(id=index).first()

    if dish is None:
        return JsonResponse({'message':'dish not found'}, status=404)

    if request.method == 'GET':
        serializer = DishSerializer(dish)
        return JsonResponse(serializer.data, safe=False)

    # PUT method not supported (to modify a dish, delete and post new one)

    elif request.method == 'DELETE':
        dish.delete()
        return JsonResponse({'message':'dish deleted'}, status=204)

    return JsonResponse({'message':'method not allowed'}, status=405)


@csrf_exempt
def post_rate(request, id):
    """
    Update the rate of a dish
    """

    # Get dish from URI
    index = int(id)
    dish = Dish.objects.filter(id=index).first()
    if dish is None:
        return JsonResponse({'message':'dish not found'}, status=404)

    # Get vote user from JSON content
    data = JSONParser().parse(request)
    if 'user' not in data or 'rate' not in data:
        return JsonResponse({'message':'invalid arguments'}, status=403)
    user = User.objects.filter(twitterID=data['user']).first()
    if user is None:
        return JsonResponse({'message':'user not found'}, status=404)

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
            return JsonResponse({'message':'rate vote cannot be created'}, status=403)

        update_dish_rate(dish)

        return JsonResponse({'message':'vote created'}, status=201)

    elif request.method == 'DELETE':

        if vote is None:
            return JsonResponse({'message': 'Rate vote not found'}, status=404)
        else:
            vote.delete()

        update_dish_rate(dish)

        return JsonResponse({'message':'rate vote deleted'}, status=204)

    return JsonResponse({'message':'method not allowed'}, status=405)

@csrf_exempt
def order_list(request):
    '''
    List all orders, add a new order, or clear the order List
    '''
    if request.method == 'GET':
        dishes = Dish.objects.all()
        data = []

        for dish in dishes:
            amounts = map(lambda order: order.amount, get_effective_orders(dish).all())

            item = {
                'id':dish.id,
                'name':dish.name,
                'price':dish.price,
                'rate':dish.rate,
                'photo':dish.photo.url,
                'num':sum(amounts),
            }
            data.append(item)

        return JsonResponse(data, safe=False)

    if request.method == 'POST':
        data = JSONParser().parse(request)
        if 'twitterID' not in data or 'amount' not in data or 'dish' not in data:
            return JsonResponse({'message':'invalid arguments'}, status=403)

        user = User.objects.filter(twitterID=data['twitterID']).first()
        dish = Dish.objects.filter(id=data['dish']).first()
        if not user or not dish:
            return JsonResponse({'message':'user or dish not found'}, status=404)

        try:
            order = Order.objects.create(user=user, dish=dish, amount=data['amount'], paid=False)
            order.save()
        except Exception:
            return JsonResponse({'message':'create order failed'}, status=403)

        return JsonResponse({'message':'order created'}, status=201)

    return JsonResponse({'message':'method not allowed'}, status=405)

@csrf_exempt
def create_orders(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        if 'twitterID' not in data or 'order' not in data:
            return JsonResponse({'message':'invalid arguments'}, status=403)

        user = User.objects.filter(twitterID=data['twitterID']).first()
        if not user:
            return JsonResponse({'message':'user not found'}, status=404)

        for order in data['order']:
            if 'dish' not in order or 'amount' not in order:
                return JsonResponse({'message':'invalid arguments'}, status=403)

            dish = Dish.objects.filter(id=order['dish']).first()
            if not dish:
                return JsonResponse({'message':'dish not found'}, status=404)

            try:
                order = Order.objects.create(user=user, dish=dish, amount=order['amount'], paid=False)
                order.save()
            except Exception:
                return JsonResponse({'message':'create order failed'}, status=403)

        return JsonResponse({'message':'order created'}, status=201)

    return JsonResponse({'message':'method not allowed'}, status=405)


@csrf_exempt
def order_amount(request, id):
    '''
    Get the number of order based on dish id
    '''
    id = int(id)
    if request.method == 'GET':
        try:
            dish = Dish.objects.get(id=id)
        except ObjectDoesNotExist:
            return JsonResponse({'message':'invalid dish id'}, status=403)

        count = get_effective_orders(dish).count()
        return JsonResponse({'dish':id,'num':count})

    return JsonResponse({'message':'method not allowed'}, status=405)

@csrf_exempt
def order_user(request, id):
    if request.method == 'GET':
        user = User.objects.filter(twitterID=id).first()
        if user is None:
            return JsonResponse({'Message':'Invalid user id'}, status=403)

        orders = get_effective_orders(user).all()
        res = []
        for order in orders:
            if order.paid == False:
                dish = order.dish
                res.append({"dish":dish.name, "price":dish.price, "amount":order.amount})
        return JsonResponse(res, safe=False)

    return JsonResponse({'message':'method not allowed'}, status=405)

@csrf_exempt
def history_order_user(request, id):
    if request.method == 'GET':
        user = User.objects.filter(twitterID=id).first()
        if user is None:
            return JsonResponse({'Message':'Invalid user id'}, status=403)

        orders = user.order.all().order_by('-created_at')
        res = []
        count = 0
        for order in orders:
            dish = order.dish
            res.append({"dish":dish.name, "price":dish.price, "amount":order.amount, "photo":dish.photo.url})
            count += 1
            if count >= 5:
                break
        return JsonResponse(res, safe=False)

    return JsonResponse({'message':'method not allowed'}, status=405)


# Tab2 Methods

@csrf_exempt
def notification_content_with_timestamp(request, timestamp):
    '''
    Get the notification if there is a new one
    '''
    notif = Notification.objects.all().first()
    if notif is None:
        return JsonResponse({'notification':False})

    if request.method == 'GET':
        last = int(notif.modified_at.strftime('%s'))
        cur = int(timestamp)

        if cur < last:
            data = NotificationSerializer(notif).data
            data['notification'] = True
            return JsonResponse(data)
        else:
            return JsonResponse({'notification':False})

    return JsonResponse({'message':'method not allowed'}, status=405)

@csrf_exempt
def notification_content(request):
    '''
    Update/Get the notification
    '''
    if request.method == 'GET':
        notif = Notification.objects.all().first()
        if notif is None:
            return JsonResponse({'notification':False})

        # check if notification too old (5 min)
        curtime = datetime.datetime.utcnow()
        curtime = curtime.replace(tzinfo=utc)
        if (curtime - notif.modified_at).total_seconds() > 300:
            notif.delete()
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

    return JsonResponse({'message':'method not allowed'}, status=405)

@csrf_exempt
def current_location(request):
    '''
    Get/Update the cureent retailer location
    '''
    if request.method == 'GET':
        location = Location.objects.all().first()
        if location is None:
            return JsonResponse({'emssage':'server errors'}, status=500)

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

    return JsonResponse({'message':'method not allowed'}, status=405)

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
        return JsonResponse({'message':'reset all pickup locations'}, status=205)

    return JsonResponse({'message':'method not allowed'}, status=405)

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
        return JsonResponse({'message':'location not found'}, status=404)

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
        return JsonResponse({'message':'location deleted'}, status=204)

    return JsonResponse({'message':'method not allowed'}, status=405)

# Tab 3 Methods

def client_token(request):
    """
    Get the client token needed to complete the payment
    """
    if request.method == 'GET':
        # check the identity first (nice to have feature)
        return HttpResponse(braintree.ClientToken.generate())

    return HttpResponse(status=405)

@csrf_exempt
def create_purchase_android(request):
    """
    Place the order
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        if 'payment_method_nonce' in data and 'user_id' in data:

            user = User.objects.filter(twitterID=data['user_id']).first()
            if user is None:
                return JsonResponse({'message':'user id invalid'}, status=404)

            orders = get_effective_orders(user).all()
            total = 0.0;
            for order in orders:
                if order.paid == False:
                    total = total + (order.amount * order.dish.price)

            if total > 0:
                # use payment method,
                result = braintree.Transaction.sale({
                    "amount": str(total),  # modify the amount here to reflect the real case
                    "payment_method_nonce": data['payment_method_nonce'],
                    "options": {
                        "submit_for_settlement": True
                    }
                })

                if result.is_success:
                    order_pay(user)
                    return JsonResponse({'message':'payment is successful'}, status=200)
                else:
                    return JsonResponse({'message':'payment failed'}, status=501)
            else:
                return JsonResponse({'message':'payment has already been completed'})

        return JsonResponse({'message':'invalid input arguments'}, status=403)

    return JsonResponse({'message':'method not allowed'}, status=405)

@csrf_exempt
def create_purchase_ios(request):
    """
    Place the order
    """
    if request.method == 'POST':
        if 'payment_method_nonce' in request.POST and 'user_id' in request.POST:

            user = User.objects.filter(twitterID=request.POST['user_id']).first()
            if user is None:
                return JsonResponse({'message':'user id invalid'}, status=404)

            orders = get_effective_orders(user)
            total = 0.0;
            for order in orders:
                if order.paid == False:
                    total = total + (order.amount * order.dish.price)

            if total > 0:
                # use payment method,
                result = braintree.Transaction.sale({
                    "amount": str(total),  # modify the amount here to reflect the real case
                    "payment_method_nonce": request.POST['payment_method_nonce'],
                    "options": {
                        "submit_for_settlement": True
                    }
                })

                if result.is_success:
                    order_pay(user)
                    return JsonResponse({'message':'payment is successful'}, status=200)
                else:
                    return JsonResponse({'message':'payment failed'}, status=501)
            else:
                return JsonResponse({'message':'payment has already been completed'})

        return JsonResponse({'message':'invalid input arguments'}, status=403)

    return JsonResponse({'message':'method not allowed'}, status=405)



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

# Helper Function: get orders within this interval
def get_effective_orders(relate_item):

    cur_date = datetime.datetime.now()
    delta = datetime.datetime.utcnow() - cur_date
    hour = cur_date.hour

    # 10AM - 2PM(noon) only return orders later than 6AM
    # 3PM - 7PM only return orders later than 12PM

    # if hour < 10 or hour >= 19:
    #     return Order.objects.none()
    # elif hour >= 10 and hour < 14:
    #     thresh_date = datetime.datetime(cur_date.year, cur_date.month, cur_date.day, 10, 0)
    # elif hour >= 15 and hour < 19:
    #     thresh_date = datetime.datetime(cur_date.year, cur_date.month, cur_date.day, 15, 0)

    # For Testing Purpose
    thresh_date = cur_date - datetime.timedelta(hours=3)
    thresh_date += delta
    thresh_date = thresh_date.replace(tzinfo=utc)

    if relate_item is None:
        return Order.objects.filter(created_at__gte=thresh_date)
    else:
        return relate_item.order.filter(created_at__gte=thresh_date)

# Helper Function: update user payment information
def order_pay(user):
    orders = get_effective_orders(user).all()
    for order in orders:
        if order.paid == False:
            order.paid = True
            order.save()
