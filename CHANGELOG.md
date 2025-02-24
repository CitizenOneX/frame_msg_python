## 4.0.0

* Allow multiple Rx classes to register for Frame data responses and specify their msg_code filter.

## 3.0.0

* Initial version of `FrameMsg` wrapper for FrameBle with added lifecycle and convenience functions for loading standard Lua helpers
* Reworked receive (Rx) handlers to attach and detach from the data response stream (only one Rx listener supported at the moment)
* Added `RxAudio` and `audio.lua` for handling streaming audio from Frame

## 2.2.0

* Added `RxTap` and the corresponding `tap.lua` library to receive taps and multi-taps from Frame

## 2.1.0

* Added support for lz4 compression of sprites and image sprite blocks
* Modified acknowledgement byte from data handler to return 0 for successful processing and 1 for error
* Set guidance in comments for photo capture resolution to 256-720 - low values for resolution near 100 cause issues with the subsequent photo capture

## 2.0.0

* Breaking: removed redundant `msg_code` attribute from Tx classes - pass the `msg_code` independently to `frame.send_message()`

## 1.0.1

* Fixed bug in image sprite block packing.
  TxSprite, TxImageSpriteBlock, RxPhoto available.

## 1.0.0

* First PyPI package release. TxSprite available, most Tx/Rx types unavailable.

## 0.1.0

* Initial version adapted from [the Flutter implementation](https://pub.dev/packages/frame_msg)
