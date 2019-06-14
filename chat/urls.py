from django.conf.urls import url

from chat.api import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    # url(r'^(?P<room_name>[^/]+)/$', views.room, name='room'),

    url(r'get_logged_in_user/$', views.get_logged_in_user),
    # Generic Conversation urls
    url(r'conversations/$', views.GenericConversationListView.as_view()),
    url(r'conversations/(?P<pk>\d+)/messages/$', views.GenericMessageListCreateView.as_view())
]
