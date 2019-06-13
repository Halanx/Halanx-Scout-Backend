from django.conf.urls import url

from chat.api import views

urlpatterns = [
    # Scout urls
    url(r'scouts/get_logged_in_user/$', views.get_logged_in_user),
    url(r'^scouts/conversations/$', views.ScoutConversationListAPIView.as_view()),
    url(r'^scouts/conversations/(?P<pk>\d+)/messages/$', views.ScoutMessageListCreateAPIView.as_view()),

    # Customer urls
    url(r'^customers/conversations/$', views.CustomerConversationListAPIView.as_view()),
    url(r'^customers/conversations/(?P<pk>\d+)/messages/$', views.CustomerMessageListCreateAPIView.as_view()),

]
