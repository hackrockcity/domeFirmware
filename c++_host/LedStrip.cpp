#include <iostream>
#include <fcntl.h>   /* File control definitions */
#include <errno.h>   /* Error number definitions */
#include <termios.h> /* POSIX terminal control definitions */

#include "LedStrip.h"

void LedStrip::Connect(std::string portname)
{
    m_fd = open(portname.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
    if (m_fd == -1)
    {
        perror("open_port: Unable to open port:");
        perror(portname.c_str());
        exit(1);  // TODO: Should we actually exit here?
    }

// Don't need to set a baud rate, the teensy ignores it
//    struct termios options;
//    tcgetattr(m_fd, &options);
//    cfsetispeed(&options, B115200);
//    cfsetospeed(&options, B115200);
//    tcsetattr(m_fd, TCSANOW, &options);
}

void LedStrip::SendBytes64(char* data) {
    int return_code;
    int count = 0;

    do {
        return_code = write(m_fd, data, 64);
        // If a write error occurs, it is probably because the buffer is full.
        // Force it to drain, then try again.
        if (return_code < 0) {
            tcdrain(m_fd);
            count++;
        }
    }
    while (return_code < 0);

    if (count > 0) {
        std::cerr << "count=" << count << std::endl;
    }
}

void LedStrip::ConvertColor24(char* data) {
    char newData[24];

    memset(newData,0,24);

    newData[0] = 0xFF;
    newData[8] = 0xFF;
    newData[16] = 0xFF;


    for (int bit_index = 7; bit_index > 0; bit_index--) {
        for (int pixel_index = 0; pixel_index < 8; pixel_index++) {
            newData[1 +7-bit_index] |= ((data[1 + 3*pixel_index] >> bit_index) & 1) << pixel_index;
            newData[9 +7-bit_index] |= ((data[    3*pixel_index] >> bit_index) & 1) << pixel_index;
            newData[17+7-bit_index] |= ((data[2 + 3*pixel_index] >> bit_index) & 1) << pixel_index;
        }
    }

//    for (int i = 0; i < 7; i++) {
//       newData[i+1] = 0x00;
//       newData[i+9] = 0x00;
//       newData[i+17] = 0x00;
//    }

    memcpy(data, newData, 24);
}

void LedStrip::LoadData(char* data) {
    // Convert the data to the appropriate space
    for (int index = 1; index < m_image_height*8*3; index+=24) {
        ConvertColor24(data+index);
    }

    // Write out the appropriate amount of data
    for (int index = 1; index < m_image_height*8*3; index+=64) {
        SendBytes64(data+index);
    }
}

void LedStrip::Flip() {
    char test[64];
    for (int index = 0; index < 64; index++) {
        test[index] = 0x00;
    }

    // Write out the appropriate amount of data
    SendBytes64(test);
}
