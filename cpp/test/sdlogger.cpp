#include "sdlogger.h"


SDLogger::SDLogger() {}


int SDLogger::init(TTGOClass *watch_ptr) {
    watch_ptr = watch_ptr;
    for (int i=0; i < 10; i++) {
        if (watch_ptr->sdcard_begin()) {
            Serial.println("sd begin pass");
            no_sd = false;
            break;
        }
        Serial.println("sd begin fail,wait 1 sec");
        delay(500);
    }
    if (no_sd) return 1;

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
    if (no_sd) return 1;

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
    if (no_sd) return 1;

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
    if (no_sd) return 1;

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
    if (no_sd) return;

    log_file.close();
    log_started = false;
}