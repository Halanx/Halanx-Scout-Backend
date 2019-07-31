from django.conf.urls import url

from scouts.sub_tasks.api import views


urlpatterns = (
    url(r'^move_out/remarks/$', views.MoveOutRemarkUpdateView.as_view()),
    url(r'^move_out/amenity_check/$', views.MoveOutAmenitiesCheckupRetrieveUpdateView.as_view()),

)
