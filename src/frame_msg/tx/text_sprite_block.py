from dataclasses import dataclass
import struct
from typing import List, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from frame_msg import TxSprite

@dataclass
class TxTextSpriteBlock:
    """
    A block of text rendered as sprites.

    Attributes:
        msg_code: Message type identifier
        width: Width constraint for text layout
        font_size: Font size in pixels
        max_display_rows: Maximum number of rows to display
        text: The text to render
        font_family: Optional font family name
    """
    msg_code: int
    width: int
    font_size: int
    max_display_rows: int
    text: str
    font_family: Optional[str] = None

    def __post_init__(self):
        self.sprites: List[TxSprite] = []
        self._create_text_sprites()

    def _create_text_sprites(self):
        """Create sprites from rendered text."""
        # Create image large enough for text
        img = Image.new('RGB', (self.width, self.font_size * self.max_display_rows), 'black')
        draw = ImageDraw.Draw(img)

        # Try to load specified font or use default
        try:
            font = ImageFont.truetype(self.font_family, self.font_size) if self.font_family else \
                   ImageFont.load_default()
        except OSError:
            font = ImageFont.load_default()

        # Draw text and split into lines
        lines = []
        y = 0
        for line in self.text.split('\n'):
            bbox = draw.textbbox((0, y), line, font=font)
            if bbox[3] - bbox[1] > 0:  # If line has height
                draw.text((0, y), line, font=font, fill='white')
                lines.append((bbox[0], y, bbox[2], bbox[3]))
            y += self.font_size

        # Convert each line to a sprite
        for left, top, right, bottom in lines:
            line_img = img.crop((left, top, right, bottom))

            # Convert to TxSprite with 2-color palette
            sprite = TxSprite(
                msg_code=self.msg_code,
                width=line_img.width,
                height=line_img.height,
                num_colors=2,
                palette_data=bytes([0,0,0, 255,255,255]),  # Black and white
                pixel_data=bytes(1 if p[0] > 127 else 0 for p in line_img.getdata())
            )
            self.sprites.append(sprite)

    def pack(self) -> bytes:
        """Pack the text block header."""
        if not self.sprites:
            raise Exception("No sprites to pack")

        # Create offsets for each line
        offsets = []
        y = 0
        for sprite in self.sprites:
            offsets.extend([0, 0, y >> 8, y & 0xFF])  # x=0, y=running total
            y += sprite.height

        return bytes([
            0xFF,  # Block marker
            self.width >> 8,
            self.width & 0xFF,
            self.max_display_rows & 0xFF,
            len(self.sprites) & 0xFF
        ]) + bytes(offsets)


@dataclass
class TxImageSpriteBlock:
    """
    An image split into horizontal sprite strips.

    Attributes:
        msg_code: Message type identifier
        image: Source sprite to split
        sprite_line_height: Height of each sprite strip
        progressive_render: Whether to render lines as they arrive
        updatable: Whether lines can be updated after initial render
    """
    msg_code: int
    image: TxSprite
    sprite_line_height: int
    progressive_render: bool = True
    updatable: bool = True

    def __post_init__(self):
        self.sprite_lines: List[TxSprite] = []
        self._split_into_lines()

    def _split_into_lines(self):
        """Split the source image into horizontal strips."""
        pixels = np.frombuffer(self.image.pixel_data, dtype=np.uint8)
        pixels = pixels.reshape((self.image.height, self.image.width))

        # Process full-height lines
        for i in range(0, self.image.height // self.sprite_line_height):
            start_y = i * self.sprite_line_height
            line_pixels = pixels[start_y:start_y + self.sprite_line_height]

            self.sprite_lines.append(TxSprite(
                msg_code=self.msg_code,
                width=self.image.width,
                height=self.sprite_line_height,
                num_colors=self.image.num_colors,
                palette_data=self.image.palette_data,
                pixel_data=line_pixels.tobytes()
            ))

        # Process final partial line if any
        remaining_height = self.image.height % self.sprite_line_height
        if remaining_height > 0:
            final_line = pixels[-remaining_height:]
            self.sprite_lines.append(TxSprite(
                msg_code=self.msg_code,
                width=self.image.width,
                height=remaining_height,
                num_colors=self.image.num_colors,
                palette_data=self.image.palette_data,
                pixel_data=final_line.tobytes()
            ))

    def pack(self) -> bytes:
        """Pack the image block header."""
        if not self.sprite_lines:
            raise Exception("No sprite lines to pack")

        return struct.pack('>BHHHHBB',
            0xFF,  # Block marker
            self.image.width,
            self.image.height,
            self.sprite_line_height,
            1 if self.progressive_render else 0,
            1 if self.updatable else 0
        )