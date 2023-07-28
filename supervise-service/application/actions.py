from models import DeviceInfo
import requests


class DeviceController:

    def pause(self, device_info):
        device_id = device_info.id
        device_ip = device_info.ip_address
        device_port = device_info.port
        url = "http://" + device_ip + ":" + device_port + "/api/control/pause"
        try:
            response = requests.post(url=url, json={"device_id": device_id})

            if 200 <= response.status_code < 300:
                return response.text, 200

            else:
                return "Device not found", 404

        except Exception as e:
            print(e)
            return "Error pausing device", 500

    def resume(self, device_info):
        device_id = device_info.id
        device_ip = device_info.ip_address
        device_port = device_info.port
        url = "http://" + device_ip + ":" + device_port + "/api/control/resume"
        try:
            response = requests.post(url=url, json={"device_id": device_id})

            if 200 <= response.status_code < 300:
                return response.text, 200

            else:
                return "Device not found", 404

        except Exception as e:
            print(e)
            return "Error resuming device", 500


class StreamController:

    def init