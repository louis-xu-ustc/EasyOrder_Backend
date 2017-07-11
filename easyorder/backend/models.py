from django.db import models

# Persistent Data Models

class User(models.Model):
    '''
    TwitterID:     Each user (customer/retailer) use his twitterID as unique primary key (posted to DB after user logged in)
    TwitterToken:  not useful? because this can be save locally and used by app to post twitter
    Name:          Initially set to user twitter screenname, and user can edit in profile tab?
    '''
    twitterID = models.CharField(max_length=100)
    # twitterToken = models.CharField(max_length=100)
    name = models.CharField(max_length=100)

class Dish(models.Model):
    '''
    Name:          name of the dish
    Price:         price of each serve
    Photo:         Imagefield is a File object, where we usually save actual image in media/ directory. Encode/Decode image to Base64 format when doing REST API call
    Rate:          score of this dish, from 0.0-5.0
    RateNum:       number of rate votes, used to calculate further rate score
    '''
    name = models.CharField(max_length=100)
    price = models.IntegerField()
    photo = models.ImageField(upload_to='dishes')
    rate = models.FloatField()
    rateNum = models.IntegerField()

class Order(models.Model):
    '''
    User:          point to the user object made this order
    Dish:          point to the dish object of this order
    Amount:        specify how many serves ordered
    Paid:          whether this order has been paid
    '''
    user = models.ForeignKey(User, related_name='order')
    dish = models.ForeignKey(Dish, related_name='order')
    amount = models.IntegerField()
    paid = models.BooleanField()

class Location(models.Model):
    '''
    Location data is used to share retailer's location with customers
    We can also use this model to save the target pickup locations set by retailer
    The location at index 0 is the current location of the retailer.
    Any locations with index larger than 0 is the pickup locaiton configured
    by the retailers.
    '''
    name = models.CharField(max_length=100, default="Anonymous")
    latitude = models.FloatField()
    longitude = models.FloatField()

# Temporary Notification Model
class Notification(models.Model):
    '''
    We can create notification object when retailer want to push notification, and delete that one related
    to user when customer application retrieves the notification using long poll
    '''
    content = models.CharField(max_length=500)
    modified_at = models.DateTimeField(auto_now=True)
