from django.conf.urls import url, include
# from rest_framework import routers

from . import views

# router = routers.DefaultRouter()
# router.register(r'locations', views.LocationViewSet)

urlpatterns = [
    # url(r'^', include(router.urls)),
    url(r'^time/$', views.current_datetime),
    url(r'^user/$', views.user_info),
    url(r'^dish/$', views.dish_list),
    url(r'^dish/(?P<id>[0-9]+)/$', views.dish_detail),
    url(r'^rate/(?P<id>[0-9]+)/$', views.post_rate),
    url(r'^current_location/$', views.current_location),
    url(r'^pickup_locations/$', views.pickup_location_list),
    url(r'^notification/$', views.notification_content),
    url(r'^notification/(?P<timestamp>[0-9]+)/$', views.notification_content_with_timestamp),
    url(r'^order/$', views.order_list),
    url(r'^order/bunch/$', views.create_orders),
    url(r'^order/user/(?P<id>[0-9]+)/$', views.order_user),
    url(r'^order/(?P<id>[0-9]+)/$', views.order_amount),
    url(r'^order/pay/$', views.order_pay),
    url(r'^payment/client_token/$', views.client_token),
    url(r'^payment/checkout/$', views.create_purchase_ios),
    url(r'^payment/checkout/android$', views.create_purchase_android),

    # for debug only, commentted out in production
    # url(r'^location/(?P<id>[0-9]+)/$', views.location_detail),
]
