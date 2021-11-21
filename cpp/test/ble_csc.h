#ifndef BLE_CSC_H
#define BLE_CSC_H

#include "BLEDevice.h"
// #include "BLEScan.h"
#include "Arduino.h"


extern unsigned wheel_rev;
extern unsigned last_wheel_time;
extern unsigned prev_wheel_time;
extern unsigned prev_wheel_rev;


static void notifyCallback(
  BLERemoteCharacteristic* pBLERemoteCharacteristic,
  uint8_t* pData,
  size_t length,
  bool isNotify);


class MyClientCallback : public BLEClientCallbacks {

  void onConnect(BLEClient* pclient);

  void onDisconnect(BLEClient* pclient);
};


bool connectToServer();


/**
 * Scan for BLE servers and find the first one that advertises the service we are looking for.
 */
class MyAdvertisedDeviceCallbacks: public BLEAdvertisedDeviceCallbacks {
 /**
   * Called for each advertising BLE server.
   */
  void onResult(BLEAdvertisedDevice advertisedDevice);
}; // MyAdvertisedDeviceCallbacks


void setup_ble_csc();

void run_ble_csc();

#endif