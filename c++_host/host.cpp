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

    // Specify the screen geometry and strips on the command line, like this:
    // host height width /dev/ttyACM0 0 /dev/ttyACM1 8

    display_height = atoi(argv[1]);
    display_width = atoi(argv[2]);

    for(int i = 3; i < argc; i+=2) {
      strips.push_back(LedStrip(display_width,display_height,atoi(argv[i+1])));
      strips.back().Connect(argv[i]);
    }

    SocketListener listener;
    listener.Connect("0.0.0.0", 58082);

    while(1) {
       char data[display_width*display_height*3+1];
        listener.GetFrame(data, display_width*display_height*3+1);
        for(int i = 0; i < strips.size(); i++) {
            strips[i].Flip();
        }

        for(int i = 0; i < strips.size(); i++) {
            strips[i].LoadData(data + 1);
        }
    }
}
