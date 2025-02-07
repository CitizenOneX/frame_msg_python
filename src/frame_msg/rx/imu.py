from typing import Tuple, Optional, List
from dataclasses import dataclass
import math
import struct
from bleak import BleakClient

class SensorBuffer:
    """Buffer class for smoothing sensor readings"""
    def __init__(self, max_size: int):
        self.max_size = max_size
        self._buffer: List[Tuple[int, int, int]] = []

    def add(self, value: Tuple[int, int, int]):
        self._buffer.append(value)
        if len(self._buffer) > self.max_size:
            self._buffer.pop(0)

    @property
    def average(self) -> Tuple[int, int, int]:
        if not self._buffer:
            return (0, 0, 0)

        sum_x = sum(v[0] for v in self._buffer)
        sum_y = sum(v[1] for v in self._buffer)
        sum_z = sum(v[2] for v in self._buffer)
        size = len(self._buffer)
        return (sum_x // size, sum_y // size, sum_z // size)

@dataclass
class IMURawData:
    compass: Tuple[int, int, int]
    accel: Tuple[int, int, int]

@dataclass
class IMUData:
    compass: Tuple[int, int, int]
    accel: Tuple[int, int, int]
    raw: Optional[IMURawData] = None

    @property
    def pitch(self) -> float:
        return math.atan2(self.accel[1], self.accel[2]) * 180.0 / math.pi

    @property
    def roll(self) -> float:
        return math.atan2(self.accel[0], self.accel[2]) * 180.0 / math.pi

class RxIMU:
    def __init__(self, imu_flag: int = 0x0A, smoothing_samples: int = 1):
        self._smoothing_samples = smoothing_samples
        self.imu_flag = imu_flag
        self._compass_buffer = SensorBuffer(smoothing_samples)
        self._accel_buffer = SensorBuffer(smoothing_samples)

    async def process_data(self, char: BleakClient, callback):
        def notification_handler(_, data: bytearray):
            if data[0] != self.imu_flag:
                return

            # Convert bytes to signed 16-bit integers
            s16 = struct.unpack('<6h', data[2:14])  # 6 signed shorts

            raw_compass = (s16[0], s16[1], s16[2])
            raw_accel = (s16[3], s16[4], s16[5])

            self._compass_buffer.add(raw_compass)
            self._accel_buffer.add(raw_accel)

            imu_data = IMUData(
                compass=self._compass_buffer.average,
                accel=self._accel_buffer.average,
                raw=IMURawData(compass=raw_compass, accel=raw_accel)
            )

            callback(imu_data)

        await char.start_notify(char.uuid, notification_handler)