import asyncio
from bleak import BleakClient


class RxTap:
    def __init__(self, tap_flag: int = 0x09, threshold_ms: int = 300):
        self.tap_flag = tap_flag
        self.threshold = threshold_ms / 1000.0  # Convert to seconds

    async def process_data(self, char: BleakClient, callback):
        last_tap_time = 0
        taps = 0
        tap_timer = None

        def notification_handler(_, data: bytearray):
            nonlocal last_tap_time, taps, tap_timer

            if data[0] != self.tap_flag:
                return

            tap_time = asyncio.get_event_loop().time()

            # Debounce taps that are too close together
            if tap_time - last_tap_time < 0.04:  # 40ms
                last_tap_time = tap_time
                return

            last_tap_time = tap_time
            taps += 1

            if tap_timer:
                tap_timer.cancel()

            async def timer_callback():
                nonlocal taps
                callback(taps)
                taps = 0

            tap_timer = asyncio.create_task(
                asyncio.sleep(self.threshold, timer_callback())
            )

        await char.start_notify(char.uuid, notification_handler)