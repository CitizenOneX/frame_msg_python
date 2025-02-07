import struct
from bleak import BleakClient

class RxAudio:
    def __init__(self, non_final_chunk_flag: int = 0x05, final_chunk_flag: int = 0x06,
                 streaming: bool = False):
        self.non_final_chunk_flag = non_final_chunk_flag
        self.final_chunk_flag = final_chunk_flag
        self.streaming = streaming

    async def process_data(self, char: BleakClient, callback):
        audio_data = bytearray() if not self.streaming else None
        raw_offset = 0

        def notification_handler(_, data: bytearray):
            nonlocal audio_data, raw_offset

            if data[0] not in (self.non_final_chunk_flag, self.final_chunk_flag):
                return

            chunk = data[1:]

            if self.streaming:
                # Stream mode - send each chunk directly
                if len(chunk) % 2 == 0:  # Ensure whole 16-bit PCM samples
                    callback(bytes(chunk))
            else:
                # Single clip mode - accumulate until final chunk
                audio_data.extend(chunk)
                raw_offset += len(chunk)

            if data[0] == self.final_chunk_flag:
                if not self.streaming:
                    callback(bytes(audio_data))
                    audio_data.clear()
                    raw_offset = 0
                callback(None)  # Signal end of stream

        await char.start_notify(char.uuid, notification_handler)

    @staticmethod
    def to_wav_bytes(pcm_data: bytes, sample_rate: int = 8000,
                    bits_per_sample: int = 16, channels: int = 1) -> bytes:
        byte_rate = sample_rate * channels * bits_per_sample // 8
        data_size = len(pcm_data)
        file_size = 36 + data_size

        # Create WAV header
        header = struct.pack(
            '<4sI4s4sIHHIIHH4sI',
            b'RIFF',
            file_size,
            b'WAVE',
            b'fmt ',
            16,                    # Subchunk1Size
            1,                     # AudioFormat (PCM)
            channels,
            sample_rate,
            byte_rate,
            channels * bits_per_sample // 8,  # BlockAlign
            bits_per_sample,
            b'data',
            data_size
        )

        return header + pcm_data
