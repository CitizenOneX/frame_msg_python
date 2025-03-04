from dataclasses import dataclass
import struct

@dataclass
class TxAutoExpSettings:
    """
    Message for auto exposure and gain settings.

    Attributes:
        metering_index: Zero-based index into ['SPOT', 'CENTER_WEIGHTED', 'AVERAGE'] i.e. 0, 1 or 2.
        exposure: Target exposure value (0.0-1.0)
        exposure_speed: Speed of exposure adjustments (0.0-1.0)
        shutter_limit: Maximum shutter value (4-16383)
        analog_gain_limit: Maximum analog gain value (1-248)
        white_balance_speed: Speed of white balance adjustments (0.0-1.0)
    """
    metering_index: int = 2
    exposure: float = 0.18
    exposure_speed: float = 0.5
    shutter_limit: int = 16383
    analog_gain_limit: int = 1
    white_balance_speed: float = 0.5

    def pack(self) -> bytes:
        """Pack the settings into 7 bytes."""
        return struct.pack('>BBBHBB',
            self.metering_index & 0xFF,
            int(self.exposure * 255) & 0xFF,
            int(self.exposure_speed * 255) & 0xFF,
            self.shutter_limit & 0x3FFF,
            self.analog_gain_limit & 0xFF,
            int(self.white_balance_speed * 255) & 0xFF
        )