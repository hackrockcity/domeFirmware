#include <iostream>
#include <string>
#include <vector>
#include <pthread.h>

#include "LedStrip.h"
#include "SocketListener.h"

int frame;
char* global_data;
pthread_mutex_t load_mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t load_signal = PTHREAD_COND_INITIALIZER;
bool load_signal_ready;

pthread_mutex_t flip_mutex;
pthread_cond_t flip_signal;
bool flip_signal_ready;

void * dataloader(void * arg)
{
    LedStrip* strip = (LedStrip*) arg;
    while(1) {

        // Load phase
//        pthread_mutex_lock(&load_mutex);
//        while( !load_signal_ready) {
//            std::cout << "waiting" << strip << std::endl;
            pthread_cond_wait(&load_signal, &load_mutex);
//        }
        pthread_mutex_unlock(&load_mutex);

//        std::cout << "flip" << strip << std::endl;
        strip->Flip();
//	std::cout << "load" << strip << std::endl;
        strip->LoadData(global_data + 1);
//        std::cout << "done load" << strip << std::endl;
    }

    return NULL;
}

int main( int argc, const char* argv[] ) {
    int display_height = 160;
    int display_width  = 24;

    frame = 0;

    // Create a thread for each LED strip
    std::vector<pthread_t*> threads;

    // Connect to a LED strip
    std::vector<LedStrip> strips;

    // Specify the screen geometry and strips on the command line, like this:
    // host 160 40 /dev/ttyACM0 0 /dev/ttyACM1 8

    display_height = atoi(argv[1]);
    display_width = atoi(argv[2]);

    // Init a data buffer, let's only make this once. TODO: WTF!
    global_data = new char[display_width*display_height*3+1];
    

    for(int i = 3; i < argc; i+=2) {
        strips.push_back(LedStrip(display_width,display_height,atoi(argv[i+1])));
        strips.back().Connect(argv[i]);
        pthread_t thread;
        pthread_create(&thread, NULL,dataloader, (void *)&(strips.back()));
        threads.push_back(&thread);
    }

    SocketListener listener;
    listener.Connect("0.0.0.0", 58082);

    while(1) {
        frame++;
        listener.GetFrame(global_data, display_width*display_height*3+1);


        pthread_mutex_lock(&load_mutex);
        load_signal_ready = true;
        pthread_mutex_unlock(&load_mutex);
        pthread_cond_broadcast(&load_signal);
//        load_signal_ready = false;


//        for(int i = 0; i < strips.size(); i++) {
//            strips[i].Flip();
//        }

       
//        for(int i = 0; i < strips.size(); i++) {
//            strips[i].LoadData(global_data + 1);
//        }
    }

    //pthread_join(thread, NULL);
}
