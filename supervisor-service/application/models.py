from dataclasses import dataclass

"""
Module for defining data classes used in the application.

data class `DeviceInfo` that captures basic information 
about a device, including its ID, IP address, and port.

Other data classes may be added to this module as the application expands.
"""
@dataclass
class DeviceInfo:
    """
    Represents basic information about a device.

    Attributes:
        id (str): Unique identifier for the device.
        ip_address (str): IP address assigned to the device.
        port (int): Port number used for communicating with the device.

    """
    id: str
    ip_address: str
    port: int
