from django.conf.urls import url

from chat.api import views

urlpatterns = (
    url(r'conversations/$', views.ConversationListView.as_view()),
    url(r'conversations/(?P<pk>\d+)/messages/$', views.MessageListCreateView.as_view())
)
