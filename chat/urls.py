from django.conf.urls import url

from chat.api import views

urlpatterns = (
    url(r'conversations/$', views.ConversationListView.as_view()),
    url(r'conversations/(?P<pk>\d+)/messages/$', views.MessageListCreateView.as_view()),
    url('get_socket_id/', views.get_socket_id_from_node_server),

)
