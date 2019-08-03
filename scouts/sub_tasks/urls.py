from django.conf.urls import url

from scouts.sub_tasks.api import views


urlpatterns = (
    # MoveOut Sub Tasks
    url(r'^move_out/remarks/$', views.MoveOutRemarkUpdateView.as_view()),
    url(r'^move_out/amenity_check/$', views.MoveOutAmenitiesCheckupRetrieveUpdateView.as_view()),

    # PropertyOnBoarding Sub Tasks
    url(r'^property_onboard/house_address/$', views.PropertyOnBoardHouseAddressCreateView.as_view()),
    url(r'^property_onboard/house_photos/$', views.PropertyOnBoardHousePhotosUploadView.as_view()),
    url(r'^property_onboard/house_amenities/$', views.PropertyOnBoardHouseAmenitiesUpdateView.as_view()),
    url(r'^property_onboard/house_basic_details/$', views.PropertyOnBoardHouseBasicDetailsCreateView.as_view()),
)
