from dataclasses import dataclass


@dataclass
class HC12Settings:
    baud_rate: str
    channel: str
    power: str
    mode: str
