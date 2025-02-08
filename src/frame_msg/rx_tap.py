import asyncio
import logging
import time
from typing import Callable, Optional

logging.basicConfig()
_log = logging.getLogger("RxTap")

class RxTap:
    def __init__(self, tap_flag: int = 0x09, threshold: float = 0.3):
        """
        Initialize a tap handler that aggregates taps within a threshold window.

        Args:
            tap_flag: The message type identifier for tap events (default: 0x09)
            threshold: Time window in seconds to aggregate taps (default: 0.3)
        """
        self.tap_flag = tap_flag
        self.threshold = threshold
        self.queue: Optional[asyncio.Queue] = None
        self._last_tap_time = 0
        self._tap_count = 0
        self._threshold_task: Optional[asyncio.Task] = None

    def _reset_threshold_timer(self) -> None:
        """Cancel existing threshold timer and start a new one"""
        if self._threshold_task and not self._threshold_task.done():
            self._threshold_task.cancel()

        self._threshold_task = asyncio.create_task(self._threshold_timeout())

    async def _threshold_timeout(self) -> None:
        """Handle threshold timer expiration by sending tap count to queue"""
        try:
            await asyncio.sleep(self.threshold)
            if self.queue and self._tap_count > 0:
                await self.queue.put(self._tap_count)
                self._tap_count = 0
        except asyncio.CancelledError:
            pass

    def get_callback(self) -> Callable[[bytes], None]:
        """
        Returns a callback function that can be used to process incoming data packets.
        The callback will filter for tap events and aggregate them within the threshold window.

        Returns:
            Callable that takes a bytes parameter containing the data packet
        """
        def handle_data(data: bytes) -> None:
            # Check if this is a tap event
            if not data or data[0] != self.tap_flag:
                return

            current_time = time.time()

            # Debounce taps that occur too close together (40ms)
            if current_time - self._last_tap_time < 0.04:
                _log.debug('Tap ignored - debouncing')
                self._last_tap_time = current_time
                return

            _log.debug('Tap detected')
            self._last_tap_time = current_time
            self._tap_count += 1

            # Reset the threshold timer
            asyncio.create_task(self._reset_threshold_timer())

        return handle_data

    async def start(self) -> asyncio.Queue:
        """
        Start the tap handler and return a queue that will receive tap counts.

        Returns:
            asyncio.Queue that will receive integers representing tap counts
        """
        self.queue = asyncio.Queue()
        self._last_tap_time = 0
        self._tap_count = 0
        return self.queue

    def stop(self) -> None:
        """Stop the tap handler and clean up resources"""
        if self._threshold_task and not self._threshold_task.done():
            self._threshold_task.cancel()
        self.queue = None
        self._tap_count = 0