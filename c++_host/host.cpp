#include <iostream>
#include <string>
#include <vector>

#include "LedStrip.h"
#include "SocketListener.h"


int main( int argc, const char* argv[] ) {
    int display_height = 160;
    int display_width  = 24;

    // Connect to a LED strip
    std::vector<LedStrip> strips;

    strips.push_back(LedStrip(display_width,display_height,0));
    strips.push_back(LedStrip(display_width,display_height,0));
//    strips.push_back(LedStrip(display_width,display_height,0));
//    strips[0].Connect("/dev/ttyACM0");
//    strips[1].Connect("/dev/ttyACM1");
//    strips[0].Connect("/dev/ttyACM2");
    strips[0].Connect("/dev/cu.usbmodem12341");

    SocketListener listener;
    listener.Connect("0.0.0.0", 58082);

    while(1) {
       char data[display_width*display_height*3+1];
        listener.GetFrame(data, display_width*display_height*3+1);
        for(int i = 0; i < strips.size(); i++) {
            strips[i].Flip();
        }

        for(int i = 0; i < strips.size(); i++) {
            strips[i].LoadData(data);
        }
    }
}
