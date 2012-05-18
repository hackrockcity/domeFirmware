domeFirmware
============

LED driver for the dome project. Each board can control 8 LED strips, each of which is up to 5m long.

## host
A python server that listens on UDP for a serialized 24bit RGB stream (8 bits per channel) that describes a 24 wide by 160 high image from top left to bottom right. (Yo dawg your aspect ratio is wrong). The data is then output to a Teensy over a high-speed serial port.

Usage:

```python
    python domelistener.py
```

## board
PCB design for the breakout board

## firmware
Firmware that should be compiled using the Makefile, then uploaded to the teensy using the teensy utility.

## mounting hardware
3d models for whatever mounts.
