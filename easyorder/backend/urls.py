from django.conf.urls import url, include
# from rest_framework import routers

from . import views

# router = routers.DefaultRouter()
# router.register(r'locations', views.LocationViewSet)

urlpatterns = [
    # url(r'^', include(router.urls)),
    url(r'^time/$', views.current_datetime),
    url(r'^locations/$', views.location_list),
    url(r'^locations/(?P<id>[0-9]+)/$', views.location_detail),
]
