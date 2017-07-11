from django.conf.urls import url, include
# from rest_framework import routers

from . import views

# router = routers.DefaultRouter()
# router.register(r'locations', views.LocationViewSet)

urlpatterns = [
    # url(r'^', include(router.urls)),
    url(r'^time/$', views.current_datetime),
    url(r'^current_location/$', views.current_location),
    url(r'^pickup_locations/$', views.pickup_location_list),
    url(r'^dish/$', views.dish_list),
    url(r'^notification/$', views.notification_content),
    url(r'^notification/(?P<timestamp>[0-9]+)/$', views.notification_content_with_timestamp),
    # url(r'^dish/(?P<id>[0-9]+)/$', views.dish_detail),

    # for debug only, commentted out in production
    url(r'^locations/(?P<id>[0-9]+)/$', views.location_detail),
]
