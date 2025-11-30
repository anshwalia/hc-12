from dataclasses import dataclass


@dataclass
class HC12Settings:
    baudrate: int
    channel: int
    power: float
    mode: str

    def __str__(self):
        """
        Returns a user-friendly string representation of HC-12 settings.
        """
        return f"\n[Current Settings]\nBaudrate : {self.baudrate}bps\nChannel : {self.channel}\nPower : {self.power}dBm\nMode : {self.mode}\n"
