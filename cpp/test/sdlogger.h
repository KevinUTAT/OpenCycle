#ifndef SDLOGGER_H
#define SDLOGGER_H

#include "config.h"
#include "FS.h"
#include "SD.h"
#include "SPI.h"

class SDLogger {
    private:
    bool no_sd = true;
    TTGOClass *watch_ptr;
    File log_file;
    bool log_started = false;

    public:
    SDLogger();
    int init(TTGOClass *watch_ptr);
    int startNewLog();
    int log(const char* msg);
    // int log(int msg);
    int start();
    void finish();
};

#endif