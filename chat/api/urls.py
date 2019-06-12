from django.conf import settings
from django.conf.urls import url

from chat.api import views

urlpatterns = [
    url(r'get_logged_in_user/$', views.get_logged_in_user),
    url(r'^conversations/$', views.ConversationListAPIView.as_view()),
    url(r'^conversations/(?P<pk>\d+)/messages/$', views.MessageListCreateAPIView.as_view()),
]

if settings.ENVIRONMENT == "development":
    urlpatterns.append(url(r'login/$', views.login_api))
