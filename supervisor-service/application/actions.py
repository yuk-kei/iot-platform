import requests


class DeviceController:

    def pause(self, device_info):
        device_id = device_info.id
        device_ip = device_info.ip_address
        device_port = str(device_info.port)
        url = "http://" + device_ip + ":" + str(device_port) + "/api/v1/device/pause"
        try:
            response = requests.post(url=url, json={"device_id": device_id})

            if response.status_code == 200:
                return "Device paused", 200
            elif response.status_code == 400:
                return "Device is not running", 400

            else:
                return "Device not found", 404

        except Exception as e:
            print(e)
            return "Error pausing device", 500

    def resume(self, device_info):
        device_id = device_info.id
        device_ip = device_info.ip_address
        device_port = str(device_info.port)
        url = "http://" + device_ip + ":" + device_port + "/api/v1/device/resume"
        try:
            response = requests.post(url=url, json={"device_id": device_id})

            if response.status_code == 200:
                return "Device resumed", 200
            elif response.status_code == 400:
                return "Device is not paused", 400

            else:
                return "Device not found", 404

        except Exception as e:
            print(e)
            return "Error resuming device", 500

    def change_rate(self, device_info, rate=1):
        device_id = device_info.id
        device_ip = device_info.ip_address
        device_port = str(device_info.port)

        url = "http://" + device_ip + ":" + device_port + "/api/v1/device/change_rate"
        try:
            response = requests.post(url=url, json={"device_id": device_id, "rate": rate})

            if response.status_code == 200:
                return "rate change to " + str(rate), 200

            else:
                return "Device not found or not running", 404

        except Exception as e:
            print(e)
            return "Error changing rate", 500

# class StreamController:
#
#     def init
