import os
import requests


class ZaloOA():
    def __init__(self):
        self.access_token = os.getenv('ZALO_ACCESS_TOKEN')
        self.zalo_api_end_point = os.getenv('ZALO_API_ENPOINT')

    def sent_tex_message(self, uid, message):
        endpoint = "{}/{}?access_token={}".format(self.zalo_api_end_point, "message", self.access_token)
        body = {
            "recipient": {
                "user_id": uid
            },
            "message": {
                "text": message
            }
        }
        return requests.post(endpoint, body)
