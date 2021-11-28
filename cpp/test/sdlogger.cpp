#include "sdlogger.h"


SDLogger::SDLogger() {}


int SDLogger::init(TTGOClass *watch_ptr) {
    watch_ptr = watch_ptr;
    while (1) {
        if (watch_ptr->sdcard_begin()) {
            Serial.println("sd begin pass");
            break;
        }
        Serial.println("sd begin fail,wait 1 sec");
        delay(1000);
    }
    uint8_t cardType = SD.cardType();

    if (cardType == CARD_NONE) {
        Serial.println("No SD card attached");
        return 2;
    }
    Serial.print("SD Card Type: ");
    if (cardType == CARD_MMC) {
        Serial.println("MMC");
    } else if (cardType == CARD_SD) {
        Serial.println("SDSC");
    } else if (cardType == CARD_SDHC) {
        Serial.println("SDHC");
    } else {
        Serial.println("UNKNOWN");
    }
    uint64_t cardSize = SD.cardSize() / (1024 * 1024);
    Serial.printf("SD Card Size: %lluMB\n", cardSize);

    return 0;
}


int SDLogger::startNewLog() {
    char* log_name = "/log.csv";
    log_file = SD.open(log_name, FILE_WRITE);
    if(!log_file){
        Serial.println("Failed to open file for writing");
        return 1;
    }
    log_file.print("New log: \n");
    log_file.close();
    return 0;
}


int SDLogger::log(const char* msg) {
    if (log_started) {
        if (log_file.print(msg)) {
            return 0;
        }
        else return 1;
    }
    else return 2;
}


// int SDLogger::log(int msg) {
//     if (log_started) {
//         if (log_file.print("%d", msg)) {
//             return 0;
//         }
//         else return 1;
//     }
//     else return 2;
// }


int SDLogger::start() {
    char* log_name = "/log.csv";
    log_file = SD.open(log_name, FILE_APPEND);
    if(!log_file){
        Serial.println("Failed to open file for writing");
        return 1;
    }
    log_started = true;
    return 0;
}


void SDLogger::finish() {
    log_file.close();
    log_started = false;
}