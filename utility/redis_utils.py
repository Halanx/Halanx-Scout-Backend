import codecs
import pickle
import requests
from decouple import config
from redis import StrictRedis

from utility.render_response_utils import STATUS, SUCCESS, ERROR


class ConsumerAppRedis:
    """ it is a dummy Redis Class that only executes redis functions from consumer app and return results """

    def __getattr__(self, attr):
        # if attr in ['get', 'publish']:
        if attr in [func for func in dir(StrictRedis) if callable(getattr(StrictRedis, func)) and not func.startswith("__")]:
            def func(*args, **kwargs):
                print(attr, "called with ", args, kwargs)
                x = requests.post(config('HOMES_REDISAPI_EVENT_URL'),
                                  headers={'Content-type': 'application/json'},
                                  auth=(config('HOMES_ADMIN_USERNAME'), config('HOMES_ADMIN_PASSWORD')))

                response = x.json()
                if response[STATUS] == SUCCESS:
                    result = response['result']
                    result_type = response['result_type']

                elif response[STATUS] == ERROR:
                    message = response['message']
                    exception = response['exception']
                    unpickled_exception = pickle.loads(codecs.decode(exception.encode(), "base64"))
            return func

        raise NotImplementedError


myinstance = ConsumerAppRedis()