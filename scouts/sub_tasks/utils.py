OK = 'ok'
DAMAGED = 'damaged'
MISSING = 'missing'

MOVE_OUT_AMENITIES_CHECKUP_DEFAULT_JSON = {
    "data": {
        "amenities_dict": {}
    }
}

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