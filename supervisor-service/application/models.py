from dataclasses import dataclass


@dataclass
class DeviceInfo:
    id: str
    ip_address: str
    port: int
