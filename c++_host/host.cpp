
#include <iostream>
#include <String>

// First, try to send data to the usb port
#include <fcntl.h>   /* File control definitions */
#include <errno.h>   /* Error number definitions */
#include <termios.h> /* POSIX terminal control definitions */


class LedStrip {
  public:
    /**
     * Create a new LedStrip
     * @param image_width Width of the source impage
     * @param image_height Height of the source image
     * @param offst Row offset to write to this strip
     */
    LedStrip(int image_width, int image_height, int offset) :
      m_image_width(image_width),
      m_image_height(image_height),
      m_offset(offset) {
    }

    /**
     * Open a serial device for writing
     * @param portname Name of the serial port to open (example: /dev/ttyACM0)
     */
    void Connect(std::string portname);

    /**
     * Write a buffer of data out to the serial port
     * @param data Frame of color data to load, image_height*image_width*3 bytes
     */
    void LoadData(char* data);

    void Flip();

  private:
    /**
     * Send 64 bytes of data to the machine
     **/
    void SendBytes64(char* data);

    int m_image_width;
    int m_image_height;
    int m_offset;

    int m_fd;	// File descriptor
};

void LedStrip::Connect(std::string portname)
{
  m_fd = open(portname.c_str(), O_RDWR | O_NOCTTY | O_NDELAY);
  if (m_fd == -1)
  {
    perror("open_port: Unable to open port:");
    perror(portname.c_str());
    exit(1);  // TODO: Should we actually exit here?
  }

  struct termios options;
  tcgetattr(m_fd, &options);
  cfsetispeed(&options, B115200);
  cfsetospeed(&options, B115200);
  tcsetattr(m_fd, TCSANOW, &options);
}

void LedStrip::SendBytes64(char* data) {
    int return_code;
    int count = 0;

    do {
        return_code = write(m_fd, data, 64);
        if (return_code < 0) {
            tcdrain(m_fd);
            count++;
//            std::cerr << "LedStrip::LoadData: Failure to write to serial port"
//                      << " error=" << strerror(errno)
//                      << " index=" << index
//                      << std::endl;
        }
    }
    while (return_code < 0);
    if (count > 0) {
        std::cout << "index=" << index << ", count=" << count << std::endl;
    }

}

void LedStrip::LoadData(char* data) {

    char test[64];
    for (int index = 0; index < 64; index++) {
        test[index] = 0xFF;
    }

    // Write out the appropriate amount of data
    for (int index = 0; index < m_image_height*8*3; index+=64) {
        SendBytes64(data);
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

int main( int argc, const char* argv[] ) {
    std::cout << "Connecting!" << std::endl;
    LedStrip test(24,160,0);
    test.Connect("/dev/cu.usbmodem12341");

    // Black test frame
    char data_off[24*160*3];

    for (int i = 0; i < 24*160*3; i+=1) {
        data_off[i] = 0x00;
    }

    for (int i = 0; i < 24*160*3; i+=8) {
        data_off[i] = 0xFF;
    }

    // White test frame
    char data_on[24*160*3];

    for (int i = 0; i < 24*160*3; i+=1) {
        data_on[i] = 0xFF;
    }

    int count = 0;
    while(1) {
        std::cout << "Loading!" << std::endl;
        if (count < 1) {
            test.LoadData(data_on);
        }
        else {
            test.LoadData(data_off);
        }
        count = (count+1)%2;
 
        std::cout << "Flipping!" << std::endl;
        test.Flip();
    }
}
