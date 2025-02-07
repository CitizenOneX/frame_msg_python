# Frame Message Package

Note: Currently a work-in-progress, breaking changes likely.

A Python package for handling various types of messages for the Brilliant Labs Frame, including sprites, text, IMU data, and photos.

## Installation

```bash
pip install frame_msg
```

## Usage

```python
# Import specific classes
from frame_msg.tx import TxSprite, TxPlainText, TxTextSpriteBlock
from frame_msg.rx import RxIMU, RxPhoto

# Or import everything
from frame_msg import *
```
