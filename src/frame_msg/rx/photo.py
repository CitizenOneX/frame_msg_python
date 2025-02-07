from PIL import Image
import io
from bleak import BleakClient

class RxPhoto:
    def __init__(self, non_final_chunk_flag: int = 0x07, final_chunk_flag: int = 0x08,
                 upright: bool = True, is_raw: bool = False, quality: str = None,
                 resolution: int = None):
        self.non_final_chunk_flag = non_final_chunk_flag
        self.final_chunk_flag = final_chunk_flag
        self.upright = upright
        self.is_raw = is_raw
        self.quality = quality
        self.resolution = resolution
        self._jpeg_headers = {}  # Quality_Resolution -> header bytes mapping

    async def process_data(self, char: BleakClient, callback):
        image_data = bytearray()
        raw_offset = 0

        # Add JPEG header if this is raw data
        if self.is_raw:
            key = f"{self.quality}_{self.resolution}"
            if key not in self._jpeg_headers:
                raise Exception("No JPEG header found - request full JPEG once before requesting raw")
            image_data.extend(self._jpeg_headers[key])

        def notification_handler(_, data: bytearray):
            nonlocal image_data, raw_offset

            if data[0] not in (self.non_final_chunk_flag, self.final_chunk_flag):
                return

            image_data.extend(data[1:])
            raw_offset += len(data) - 1

            if data[0] == self.final_chunk_flag:
                # Save header if this is first full JPEG for this quality/resolution
                if not self.is_raw:
                    key = f"{self.quality}_{self.resolution}"
                    if key not in self._jpeg_headers:
                        self._jpeg_headers[key] = image_data[:623]

                # Rotate if needed
                if self.upright:
                    img = Image.open(io.BytesIO(image_data))
                    img = img.rotate(270, expand=True)
                    output = io.BytesIO()
                    img.save(output, format='JPEG')
                    final_data = output.getvalue()
                else:
                    final_data = bytes(image_data)

                callback(final_data)
                image_data.clear()
                raw_offset = 0

        await char.start_notify(char.uuid, notification_handler)