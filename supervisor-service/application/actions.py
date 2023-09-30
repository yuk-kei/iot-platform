import requests
"""
DeviceController manages and interacts with external devices.
Handles operations such as pausing, resuming, and changing the operating rate of devices.

Other Controller classes may be added in the future to handle other part of system operations.
"""


class DeviceController:
    """
    Controller to manage and interact with external devices.
    """
    def pause(self, device_info):
        """
        Pause a specified device.

        :param device_info: Information about the device to be paused. Contains attributes: id, ip_address, port.
        :return: Status message along with appropriate HTTP status code.
        :doc-author: Yukkei
        """
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
        """
        Resume a specified device.

        :param device_info: Information about the device to be resumed.
            Contains attributes: id, ip_address, port.
        :return: Status message along with appropriate HTTP status code.
        :doc-author: Yukkei
        """
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
        """
        Change the operating rate of a specified device.

        :param device_info: Information about the device whose rate is to be changed.
            Contains attributes: id, ip_address, port.
        :param rate: The new operating rate for the device.
        :return: Status message indicating the outcome of the rate change, along with the appropriate HTTP status code.
        :doc-author: Yukkei
        """
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

