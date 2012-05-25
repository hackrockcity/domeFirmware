#include <iostream>
#include <string>

#include "LedStrip.h"
#include "SocketListener.h"


int main( int argc, const char* argv[] ) {
    int display_height = 160;
    int display_width  = 24;

    // Connect to a LED strip
    LedStrip test(display_width,display_height,0);
    test.Connect("/dev/cu.usbmodem12341");
//    test.Connect("/dev/ttyACM0");

    SocketListener listener;
    listener.Connect("0.0.0.0", 58082);
    // 



    // Black test frame
    char data_off[display_width*display_height*3];

    for (int i = 0; i < display_width*display_height*3; i+=1) {
        data_off[i] = 0x00;
    }

    for (int i = 0; i < display_width*display_height*3; i+=8) {
        data_off[i] = 0xFF;
    }

    // White test frame
    char data_on[display_width*display_height*3];

    for (int i = 0; i < display_width*display_height*3; i+=1) {
        data_on[i] = 0xFF;
    }

    while(1) {
        char data[display_width*display_height*3+1];
        listener.GetFrame(data, display_width*display_height*3+1);

        test.LoadData(data);
        test.Flip();
    }
/*
    // Just flash.
    int count = 0;
    while(1) {
        if (count < 1) {
            test.LoadData(data_on);
        }
        else {
            test.LoadData(data_off);
        }
        count = (count+1)%2;
 
        test.Flip();
    }
*/
}
