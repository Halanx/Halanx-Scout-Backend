import codecs
import json
import pickle
import requests
from decouple import config
from redis import StrictRedis

from utility.logging_utils import sentry_debug_logger
from utility.render_response_utils import STATUS, SUCCESS, ERROR


class ConsumerAppRedis:
    """ it is a dummy Redis Class that only executes redis functions from consumer app and return results """

    def __getattr__(self, attr):
        # if attr in ['get', 'publish']:
        if attr in [func for func in dir(StrictRedis) if
                    callable(getattr(StrictRedis, func)) and not func.startswith("__")]:
            def func(*args, **kwargs):
                sentry_debug_logger.debug(str(attr) + " called with args=" + str(args) + " and kwargs=" + str(kwargs),
                                          exc_info=True)

                x = requests.post(config('HOMES_REDISAPI_EVENT_URL'),
                                  headers={'Content-type': 'application/json'},
                                  data=json.dumps({'attr': attr, 'args': args, 'kwargs': kwargs}),
                                  auth=(config('HOMES_ADMIN_USERNAME'), config('HOMES_ADMIN_PASSWORD')))

                response = x.json()
                if response[STATUS] == SUCCESS:
                    result = response['result']
                    result_type = response['result_type']
                    if result_type == 'bytes':
                        result = result.encode()
                        response['result'] = result

                    return response['result']

                elif response[STATUS] == ERROR:
                    message = response['message']
                    exception = response['exception']
                    print("error occurs with message" + str(message))
                    unpickled_exception = pickle.loads(codecs.decode(exception.encode(), "base64"))
                    raise unpickled_exception

            return func

        raise NotImplementedError


myinstance = ConsumerAppRedis()
