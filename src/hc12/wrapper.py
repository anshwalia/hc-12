"""HC-12 Wrapper Module"""

import sys

from logging import Logger, StreamHandler, Formatter, INFO, DEBUG
from serial import Serial
from time import sleep
from typing import Callable, Literal

from .data_models import HC12Settings


def check_command_mode(func: Callable) -> Callable:
    """Check if HC-12 module is in command mode before executing AT commands"""

    def wrapper(self, *args, **kwargs):

        try:
            self.write(b"AT")
            response = self.readline().decode().strip()
            if response != "OK":
                raise RuntimeError("HC-12 module not in command mode")
        except RuntimeError as re:
            self._logger.error(str(re))
        else:
            return func(self, *args, **kwargs)
        finally:
            self.flush()

    return wrapper


class HC12(Serial):
    """Wrapper class to provide various functionality for HC-12 module"""

    _logger: Logger

    def __init__(
        self,
        port=None,
        baudrate=9600,
        bytesize=8,
        parity="N",
        stopbits=1,
        timeout=1,
        xonxoff=False,
        rtscts=False,
        write_timeout=None,
        dsrdtr=False,
        inter_byte_timeout=None,
        exclusive=None,
        encoding: Literal["ASCII", "UTF-8"] = "ASCII",
        debug: bool = False,
    ):
        super().__init__(
            port,
            baudrate,
            bytesize,
            parity,
            stopbits,
            timeout,
            xonxoff,
            rtscts,
            write_timeout,
            dsrdtr,
            inter_byte_timeout,
            exclusive,
        )
        self.encoding = encoding
        self._setup_logger(debug)
        self._logger.info("Connecting...")
        # Note :-
        # Adding 2 second delay to account HC-12 requiring a brief period
        # to initialize after the port is opened before it is ready to communicate.
        sleep(2)
        if not self.is_open:
            raise IOError(f"HC-12 @ port {self.port} not open!")

    def _setup_logger(self, debug: bool = False):
        self._logger = Logger(name=f"HC-12 @ {self.port}", level=INFO)
        handler = StreamHandler(sys.stdout)
        formatter = Formatter("%(asctime)s | %(name)s | %(levelname)s | %(message)s")
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)
        if debug:
            self._logger.setLevel(DEBUG)

    def _to_bytes(self, text: str) -> bytes:
        return bytes(text, encoding=self.encoding)

    def _to_string(self, raw_bytes: bytes) -> str:
        return raw_bytes.decode(encoding=self.encoding).strip()

    def _parse_baudrate(self, raw_baudrate: bytes) -> int:
        return int(self._to_string(raw_baudrate).lstrip("OK+B"))

    def _parse_channel(self, raw_channel: bytes) -> int:
        return int(self._to_string(raw_channel).lstrip("OK+RC"))

    def _parse_transmit_power(self, raw_transmit_power: bytes) -> float:
        return float(self._to_string(raw_transmit_power).lstrip("OK+RP:").rstrip("dBm"))

    def _parse_mode(self, raw_mode: bytes) -> str:
        return self._to_string(raw_mode).lstrip("OK+")

    def _parse_settings(self, raw_settings: list[str]) -> HC12Settings:
        baudrate = self._parse_baudrate(raw_settings[0])
        channel = self._parse_channel(raw_settings[1])
        transmit_power = self._parse_transmit_power(raw_settings[2])
        mode = self._parse_mode(raw_settings[3])
        return HC12Settings(baudrate, channel, transmit_power, mode)

    @check_command_mode
    def get_current_settings(self) -> HC12Settings:
        """Get all currently applied settings for HC-12 module"""
        try:
            command = "AT+RX"
            self.write(self._to_bytes(command))
            command_response = self.readlines()
            self._logger.debug(f"Command Response : {command_response}")
            settings = self._parse_settings(command_response)
        except Exception as ex:
            self._logger.error(f"Unable to retrieve settings from module. {str(ex)}")

        return settings

    @check_command_mode
    def set_baudrate(
        self,
        baud_rate: Literal[
            "1200", "2400", "4800", "9600", "19200", "38400", "57600", "115200"
        ],
    ) -> None:
        """Set baudrate for HC-12 module. Default is 9600bps"""
        try:
            command = f"AT+B{baud_rate}"
            self.write(self._to_bytes(command))
            command_response = self.readline()
            self._logger.debug(f"Command Response : {command_response}")
            updated_baudrate = self._parse_baudrate(command_response)
        except Exception as ex:
            self._logger.error(f"Unable to update baudrate. {str(ex)}")
        else:
            self._logger.info(f"Baudrate updated to {updated_baudrate}")

    @check_command_mode
    def set_channel(self, channel: int) -> None:
        """
        Set radio channel for HC-12 module. Range (1 to 127)

        Note:
        -----
        As the wireless receiving sensitivity of the HC-12 module is relatively high,
        when the serial port baud rate exceeds 9600bps five adjacent channels will be
        used in staggered mode. When the serial port baud rate is at or below 9600bps
        for a short communication distance (within 10m), again five adjacent channels
        will be used in staggered mode to improve efficiency.
        """
        try:
            if (channel < 1) or (channel > 127):
                raise ValueError(
                    f"Invalid channel ({channel}), should be in range (1 to 127)"
                )
            command = f"AT+C{str(channel).zfill(3)}"
            self.write(self._to_bytes(command))
            command_response = self.readline()
            self._logger.debug(f"Command Response : {command_response}")
            updated_channel = self._parse_channel(command_response)
        except Exception as ex:
            self._logger.error(f"Unable to set radio channel. {str(ex)}")
        else:
            self._logger.info(f"Radio channel set to {updated_channel}")

    @check_command_mode
    def set_power(self, value: int) -> None:
        """
        Set radio transmit power for HC-12 module. Range (-1 to 20dBm).
        Default value is 8 at +20 dBm. See table below for more reference:

        ====== ===============
        Value | Power (in dBm)
        ====== ===============
        1       -1
        2       2
        3       5
        4       8
        5       11
        6       14
        7       17
        8       20
        ====== ===============
        """
        try:
            if (value < 1) or (value > 8):
                raise ValueError(
                    f"Invalid transmit power ({value}) value, should be in range (1 to 8)"
                )
            command = f"AT+P{value}"
            self.write(self._to_bytes(command))
            command_response = self.readline()
            self._logger.debug(f"Command Response : {command_response}")
            updated_transmit_power = self._parse_channel(command_response)
        except Exception as ex:
            self._logger.error(f"Unable to set radio transmit power. {str(ex)}")
        else:
            self._logger.info(f"Radio transmit power set to {updated_transmit_power}")

    @check_command_mode
    def set_mode(self, mode: Literal["FU1", "FU2", "FU3"]) -> None:
        """Set operating mode for HC-12 module. Default is FU3"""
        try:
            command = f"AT+{mode}"
            self.write(self._to_bytes(command))
            command_response = self.readline()
            self._logger.debug(f"Command Response : {command_response}")
            updated_mode = self._parse_mode(command_response)
        except Exception as ex:
            self._logger.error(f"Unable to apply mode setting. {str(ex)}")
        else:
            self._logger.info(f"Mode set to {updated_mode}")

    @check_command_mode
    def set_defaults(self) -> None:
        """Reset settings to HC-12 default"""
        try:
            command = "AT+DEFAULT"
            self.write(self._to_bytes(command))
            command_response = self.readline()
            self._logger.debug(f"Command Response : {command_response}")
            if self._to_string(command_response) != "OK+DEFAULT":
                raise RuntimeError(command_response)
        except Exception as ex:
            self._logger.error(f"Unable to apply default settings. {str(ex)}")
        else:
            self._logger.info("Default settings applied")
