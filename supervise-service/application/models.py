from dataclasses import dataclass


@dataclass
class DeviceInfo:
    id: str
    name: str
    ipaddress: str
    port: int
    status: str
