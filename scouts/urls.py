from django.conf.urls import url
from django.urls import include

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

    url(r'^notifications/$', views.ScoutNotificationListView.as_view()),

    url(r'^wallet/$', views.ScoutWalletRetrieveView.as_view()),
    url(r'^payments/$', views.ScoutPaymentListView.as_view()),

    url(r'^tasks/$', views.ScoutTaskListView.as_view()),

    url(r'^tasks/(?P<pk>\d+)/$', views.ScoutTaskRetrieveUpdateDestroyAPIView.as_view()),
    url(r'^tasks/(?P<pk>\d+)/request/$', views.ScoutTaskAssignmentRequestUpdateAPIView.as_view()),

    # sub_tasks sub app
    url(r'^tasks/(?P<task_id>\d+|)/subtask/', include('scouts.sub_tasks.urls')),


    url(r'^tenant/$', views.TenantRetrieveView.as_view()),

    # Scout Details for a house visit
    url('visits/details/', views.HouseVisitScoutDetailView.as_view()),
    url('^task/rate/', views.rate_scout),

    # Url to make connection between halanx-scout and consumer app and also to create tasks
    url('^task/create/', views.ScoutConsumerLinkAndScoutTaskCreateView.as_view()),

)
