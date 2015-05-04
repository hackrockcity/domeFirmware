# DomeStar Users Manual

## Introduction

This document serves as a general purpose overview for DomeStar.  It will walk through construction, the various software components and protocols, and applications that have been developed for the project.

## Setup

### Requirements

To install DomeStar you will need a somewhat recent MacBook Pro or Linux laptop with a decent amount of horse power.  You will needed the following software:

* Git
* GCC build tools
* [domeFirmware](https://github.com/hackrockcity/domeFirmware)
* [Processing](http://www.processing.org)
* [Processing UDP library](http://www.ubaa.net/shared/processing/udp/)
* [Processing OSC Library](http://www.sojamo.de/libraries/oscP5/)
* [domeTransmitter](https://github.com/hackrockcity/domeTransmitter)
* DarwiinRemoteOSC or something similar (WiiMote -> Open Sound Control)

### Components

DomeStar is made up of the following components

* 5 x Controller Boxes
* 5 x Wood Strip Mounts
* 40 x 5m LED strips
* Power Supply
* 5 x DC power cables
* USB hub
* USB extension cables
* Lot of zip ties

### Physical construction

![Top of DomeStar](http://www.jplt.com/domestar-gallery/images/8041951025_79645ba656_b.jpg)

To build DomeStar first build a dome.  The dome should be at least 8ft in diameter, but preferably bigger.  Only 2V domes have been used, it is unknown if other configurations will work.

At the top of the dome zip tie the five controller boxes with the JST connector wires facing out from the center of the dome.  Make sure the lids of the boxes face down so they can be accessed.

At the very center of the dome zip tie the USB hub down.  Connect each box to the USB hub.  Plug a USB cable into the hub and zip tie it down the side of the dome as far as it will go.  Then connect the USB extension and continue down to the ground and to the laptop.

Zip tie the DC power cables up the same path the USB extension took and plug one cable into each box.  The connector should push in, turn and click to lock.  Some of the connectors are damaged and take some finessing, it would be worthwhile to try it on the ground before doing it on the top of a dome.

Zip tie the wood strip mounts across two poles of the dome so that they create a bridge just below the controller boxes.  Route a zip tie through each pair of slots in the mount and close but leave loose enough to guide an LED strip through.

Zip tie the LED strips around the sides of the dome, spacing them evently.  Eight strips should connect to each box.  Make sure that the strips are tied such that the strain on the JST connector is minimized.  There should be some slack at the top.  See the 
picture at the top.

Connect the DC power cables to the power supply and connect the power supply to a AC power source like a generator or the grid.

### Configuration

You should be ready to power on DomeStar and configure it.  First do a quick on and off test of the power supply as a smoke test. If something smokes, STOP and contact a DomeStar Service Technician immediately.

Once the USB cable has been connected to the notebook you should see additional USB devices show up in /dev.  Open a terminal and take a look:

```
macbook$ ls /dev/cu.*

/dev/cu.Bluetooth-Port  /dev/cu.Bluetooth-Modem /dev/cu.JustinsJAMBOX-SPPDev-1
/dev/cu.usbmodem00001   /dev/cu.usbmodem10001   /dev/cu.usbmodem20001
/dev/cu.usbmodem30001   /dev/cu.usbmodem40001
```

You should see 5 devices matching "cu.usbmodemNNNNN".  The numbers are usually but not always five digits.  These are the controler boxes.  Now go to the domeFirmware/c++_host directory and edit run_osx.sh.

```
#!/bin/bash
./host 160 40 /dev/cu.usbmodem00001 0 /dev/cu.usbmodem10001 8 /dev/cu.usbmodem20001 16 /dev/cu.usbmodem30001 24 /dev/cu.usbmodem40001 32
```

The syntax of the host program is:

```
./host [height] [width] [device] [offset]...[device] [offset]
```

For now just replace the usbmodem devices with ones that came up on your notebook if they are different.  You will need to reorder them in the next step.

Run the script to start the listener

```
./run_osx.sh
```

Now start Processing and open domeTransmitter.  You will need to make some changes to the code to get it ready for configuration.  In the main domeTransmitter.pde find the section near the top that lists all the enabled routines, comment all but TestPattern.

``` Java
public Routine[] enabledRoutines = new Routine[] {
    new TestPattern(true)
    //new Configulate(),
    //new TestPattern(false),
    //new Waves(),
    //new WarpSpeedMrSulu(),
    //new Warp(),
    //new TrialOfZod(),
    //new Seizure(),
    //new RainbowColors(),
    //new RGBRoutine(),
    //new Pong(),
    //new Greetz(),
    //new FFTDemo(),
    //new DropTheBomb(),
    //new ColorDrop(),
    //new Chase(),
    //new Bursts(),
    //new Animator("anim-nyancat",1,.5,0,0,0),
};
```

Run the Processing sketch and hopefully you should see strips turning on and off in a seemingly random order.  If so, YAY IT IS WORKING!

Now turn on the Configulate routine.

``` Java
public Routine[] enabledRoutines = new Routine[] {
    new Configulate()
    //new TestPattern(true),
    //new TestPattern(false),
    //new Waves(),
    //new WarpSpeedMrSulu(),
    //new Warp(),
    //new TrialOfZod(),
    //new Seizure(),
    //new RainbowColors(),
    //new RGBRoutine(),
    //new Pong(),
    //new Greetz(),
    //new FFTDemo(),
    //new DropTheBomb(),
    //new ColorDrop(),
    //new Chase(),
    //new Bursts(),
    //new Animator("anim-nyancat",1,.5,0,0,0),
};
```

Run the sketch again.  You should see one strip colored blue.  Use the left and right arrows to move around the dome, it should seem to go in slightly random order. Some newer strips will actually be green, they have their green and blue colors swapped.

Move around to any starting point you find reasonable.  Press space, the strip will turn light blue and another strip will turn the previous deep blue.  Move the left and right arrows until the strip to the right of the light blue one is lit.  If it's green press down to swap green and blue, press up to undo the swap.  Press space and that strip will turn light blue.  Repeat this process until you've gone through the whole dome.  

Once completed press "s" and you should see some code show up in the Processing debug console.  Copy/paste this code into the Config class replacing the STRIP_LOOKUP and SWAP_LOOKUP sections.

Now re-enable the TestPattern routine and you should see the strips going in order around the dome.

### Running DomeStar

Now that you have everything configured you can set the FRAMERATE back to 30 and comment out the TestPattern and uncomment the other modes in enabledModes.  You're ready to run DomeStar! 

You'll want to test out the WiiMote controls next.  We've used DarwiinOSC in the past, but it can be a pain to get working on newer versions of OSX. 

### Running DomeStar.us (EXPERIMENTAL)

DomeStar.us is an attempt to allow people to control DomeStar using their smartphone. It uses a web app hosted at [domestar.us](http://www.domestar.us) that takes the phone's orientation data and sends it to the dome using WebSockets.  If DomeStar and the phone are on the same WiFi network it will do this using a direct connection, otherwise it will send via a proxy on domestar.us.

<img src="http://www.domestar.us/rocket.jpg" width="64" /> <img src="http://www.domestar.us/beer.jpg" width="64" /> <img src="http://www.domestar.us/squirrel.jpg" width="64" /> <img src="http://www.domestar.us/globe.jpg" width="64" />

There are four "totems" that need to be placed in the dome at about eye level.  The totems are a rocket, a beer mug, a squirrel and a globe.  These allow the user to calibrate their phone so that its orientation data lines up with the dome.  Each totem should be placed 90 degrees from the previous one so that the "north", "south", "east" and "west" points in the dome are covered.  These points don't need to coordinate with actual north, south, east or west.  The order of the totems should be: rocket, beer, squirrel, and then globe.

To run DomeStar in this mode, first get [DomeWebProxy](https://github.com/hackrockcity/DomeWebProxy).  Edit the Config class and paste in the appropriate STRIP_LOOKUP and SWAP_LOOKUP lines from domeTransmitter.  Run the sketch and it should connect to the domestar.us website.  If you see lots of connection errors in the Processing error console, contact Justin and have him restart the domestar proxy.

Now connect to domestar.us website using your smartphone.  Go through the calibration  routine, pointing at each totem and pressing the button.  Then tap a color swatch and use your phone like a brush.  The part of the dome you're pointing at *should* light up.

### Creating your own Routines

If you're ready to start making your own DomeStar routines go and grab [BlinkeyDomeSimulator](https://github.com/hackrockcity/BlinkeyDomeSimulator).  This sketch is a virtual version of DomeStar.  Run it and then run domeTransmitter and you should see the routines on the virtual DomeStar.  Now add a new class to domeTransmitter.

``` Java
class MyRoutine extends Routine {
  
  public MyRoutine() {
  }
  
  void draw() {
    draw.background(primaryColor);
  }
}
```

The D-Pad on the WiiMote changes the value of primaryColor, secondaryColor and teriaryColor so you should try to incorporate those into your routine.  You can also use the controller object to get the accelerometer data from the WiiMote.  Look at routines like TrialOfZod to get an idea of how that works.  Add your routine to the enabledRoutines array and run it.  


