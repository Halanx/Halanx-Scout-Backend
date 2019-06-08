from django.conf.urls import url

from scouts.api import views


urlpatterns = (
    url(r'^register/$', views.register),
    url(r'^get_otp/(?P<phone_no>\w+)/$', views.generate_otp),
    url(r'^login_otp/$', views.login_with_otp),

    url(r'^$', views.ScoutRetrieveUpdateView.as_view()),
    url(r'^pictures/$', views.ScoutPictureCreateView.as_view()),
    url(r'^documents/$', views.ScoutDocumentListCreateView.as_view()),
    url(r'^documents/(?P<pk>\d+)/$', views.ScoutDocumentDestroyView.as_view()),

    url(r'^scheduled_availability/$', views.ScheduledAvailabilityListCreateView.as_view()),
    url(r'^scheduled_availability/(?P<pk>\d+)/$', views.ScheduledAvailabilityRetrieveUpdateDestroyView.as_view()),
)
