from django.conf.urls import url

from scouts.sub_tasks.api import views


urlpatterns = (
    url(r'^move_out/remarks/$', views.MoveOutRemarkUpdateView.as_view()),

)
