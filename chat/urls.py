from django.conf.urls import url

from chat.api import views
urlpatterns = (
    url(r'^conversations/$', views.ConversationListAPIView.as_view()),
    url(r'^conversations/(?P<pk>\d+)/messages/$', views.MessageListCreateAPIView.as_view()),
)
