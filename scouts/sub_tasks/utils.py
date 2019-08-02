from utility.random_utils import generate_random_code

OK = 'ok'
DAMAGED = 'damaged'
MISSING = 'missing'

AMENITY_DEFAULT_JSON = {
    "data": {
        "amenities_dict": {}
    }
}

MOVE_OUT_AMENITIES_CHECKUP_DEFAULT_JSON = AMENITY_DEFAULT_JSON

PROPERTY_ON_BOARD_AMENITIES_DEFAULT_JSON = AMENITY_DEFAULT_JSON

# Sample Data for AMENITIES_CHECKUP_JSON
"""
{
    'data': {
        'amenities_dict': {
            0: {'id': 1,'name': 'fridge', 'status': 'ok' },
            1: {'id': 1, 'name': 'fridge', 'status': 'damaged'},
            2: {'id': 1, 'name': 'fridge', 'status': 'missing'},
        }
    }
}
"""


def get_property_on_boarding_house_picture_upload_path(instance, filename):
    return "scouts/tasks/{}/PropertyOnBoardingHousePhoto/{}/pictures/{}-{}".format(
        instance.property_on_boarding_house_photo_sub_task.task.id,
        instance.property_on_boarding_house_photo_sub_task.id,
        generate_random_code(n=5),
        filename.split('/')[-1])
