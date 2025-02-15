from dataclasses import dataclass
import struct

@dataclass
class TxManualExpSettings:
    """
    Message for manual exposure and gain settings.

    Attributes:
        manual_shutter: Shutter value (4-16383)
        manual_analog_gain: Analog gain value (0-248)
        manual_red_gain: Red gain value (0-1023)
        manual_green_gain: Green gain value (0-1023)
        manual_blue_gain: Blue gain value (0-1023)
    """
    manual_shutter: int = 800
    manual_analog_gain: int = 124
    manual_red_gain: int = 512
    manual_green_gain: int = 512
    manual_blue_gain: int = 512

    def pack(self) -> bytes:
        """Pack the settings into 9 bytes."""
        return struct.pack('>HBHHHH',
            self.manual_shutter & 0x3FFF,          # 2 bytes
            self.manual_analog_gain & 0xFF,        # 1 byte
            self.manual_red_gain & 0x3FF,          # 2 bytes
            self.manual_green_gain & 0x3FF,        # 2 bytes
            self.manual_blue_gain & 0x3FF          # 2 bytes
        )