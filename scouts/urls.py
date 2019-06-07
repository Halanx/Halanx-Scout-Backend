from django.conf.urls import url

from scouts.api import views


urlpatterns = (
    url(r'^register/$', views.register),
    url(r'^get_otp/(?P<phone_no>\w+)/$', views.generate_otp),
    url(r'^login_otp/$', views.login_with_otp),
)
