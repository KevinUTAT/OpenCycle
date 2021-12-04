#include "ble_csc.h"


// The remote service we wish to connect to.
static BLEUUID serviceUUID(uint16_t(0x1816));
// The characteristic of the remote service we are interested in.
static BLEUUID    charUUID(uint16_t(0x2a5b));

static boolean doConnect = false;
boolean connected = false;
static boolean doScan = false;
static BLERemoteCharacteristic* pRemoteCharacteristic;
static BLEAdvertisedDevice* myDevice;

unsigned wheel_rev = 0;
unsigned last_wheel_time = 0;
unsigned prev_wheel_time = 0;
unsigned prev_wheel_rev = 0;


static void notifyCallback(
  BLERemoteCharacteristic* pBLERemoteCharacteristic,
  uint8_t* pData,
  size_t length,
  bool isNotify) {
    Serial.print("Notify callback for characteristic ");
    Serial.print(pBLERemoteCharacteristic->getUUID().toString().c_str());
    Serial.print(" of data length ");
    Serial.println(length);
    Serial.print("data: ");

    unsigned wheel_rev_temp;
    unsigned last_wheel_time_temp;
    if (length >= 7) {
      wheel_rev_temp = (pData[4] << 24) | (pData[3] << 16) | (pData[2] << 8) | pData[1];
      last_wheel_time_temp = (pData[6] << 8) | pData[5];
    }
    else {
      wheel_rev_temp = (pData[2] << 8) | pData[1];
      last_wheel_time_temp = (pData[4] << 8) | pData[3];
    }

    if ( ((wheel_rev_temp - prev_wheel_rev) < 100) &&
          (wheel_rev_temp >= prev_wheel_rev)) {
      prev_wheel_time = last_wheel_time;
      prev_wheel_rev = wheel_rev;
      wheel_rev = wheel_rev_temp;
      last_wheel_time = last_wheel_time_temp;
    }
    else if (prev_wheel_rev == 0 && prev_wheel_time == 0) {
      wheel_rev = wheel_rev_temp;
      last_wheel_time = last_wheel_time_temp;
      prev_wheel_time = last_wheel_time;
      prev_wheel_rev = wheel_rev;
    }

    Serial.print(wheel_rev);
    Serial.print(", ");
    Serial.print(last_wheel_time);
    Serial.print('\n');
}


void MyClientCallback::onConnect(BLEClient* pclient) {
}

void MyClientCallback::onDisconnect(BLEClient* pclient) {
  connected = false;
  Serial.println("onDisconnect");
}


bool connectToServer() {
    Serial.print("Forming a connection to ");
    Serial.println(myDevice->getAddress().toString().c_str());
    
    BLEClient*  pClient  = BLEDevice::createClient();
    Serial.println(" - Created client");

    pClient->setClientCallbacks(new MyClientCallback());

    // Connect to the remove BLE Server.
    for (int i = 0; i < 100; i ++){
      if (pClient->connect(myDevice)) {  // if you pass BLEAdvertisedDevice instead of address, it will be recognized type of peer device address (public or private))
        break;
      }
      Serial.println(" - Fail to connect");
      return false;
    }
    
    Serial.println(" - Connected to server");
    // pClient->setMTU(517); //set client to request maximum MTU from server (default is 23 otherwise)
  
    // Obtain a reference to the service we are after in the remote BLE server.
    BLERemoteService* pRemoteService = pClient->getService(serviceUUID);
    if (pRemoteService == nullptr) {
      Serial.print("Failed to find our service UUID: ");
      Serial.println(serviceUUID.toString().c_str());
      pClient->disconnect();
      return false;
    }
    Serial.println(" - Found our service");


    // Obtain a reference to the characteristic in the service of the remote BLE server.
    pRemoteCharacteristic = pRemoteService->getCharacteristic(charUUID);
    if (pRemoteCharacteristic == nullptr) {
      Serial.print("Failed to find our characteristic UUID: ");
      Serial.println(charUUID.toString().c_str());
      pClient->disconnect();
      return false;
    }
    Serial.println(" - Found our characteristic");

    // Read the value of the characteristic.
    if(pRemoteCharacteristic->canRead()) {
      std::string value = pRemoteCharacteristic->readValue();
      Serial.print("The characteristic value was: ");
      Serial.println(value.c_str());
    }

    if(pRemoteCharacteristic->canNotify())
      pRemoteCharacteristic->registerForNotify(notifyCallback);

    connected = true;
    return true;
}


/**
  * Called for each advertising BLE server.
  */
void MyAdvertisedDeviceCallbacks::onResult(BLEAdvertisedDevice advertisedDevice) {
  Serial.print("BLE Advertised Device found: ");
  Serial.println(advertisedDevice.toString().c_str());

  // We have found a device, let us now see if it contains the service we are looking for.
  if (advertisedDevice.haveServiceUUID() && advertisedDevice.isAdvertisingService(serviceUUID)) {

    BLEDevice::getScan()->stop();
    myDevice = new BLEAdvertisedDevice(advertisedDevice);
    doConnect = true;
    doScan = true;

  } // Found our server
} // onResult


void setup_ble_csc() {
  Serial.println("Starting Arduino BLE Client application...");
  BLEDevice::init("");

  // Retrieve a Scanner and set the callback we want to use to be informed when we
  // have detected a new device.  Specify that we want active scanning and start the
  // scan to run for 5 seconds.
  BLEScan* pBLEScan = BLEDevice::getScan();
  pBLEScan->setAdvertisedDeviceCallbacks(new MyAdvertisedDeviceCallbacks());
  pBLEScan->setInterval(1349);
  pBLEScan->setWindow(449);
  pBLEScan->setActiveScan(true);
  pBLEScan->start(5, false);
}


void run_ble_csc() {
     // If the flag "doConnect" is true then we have scanned for and found the desired
  // BLE Server with which we wish to connect.  Now we connect to it.  Once we are 
  // connected we set the connected flag to be true.
  if (doConnect == true) {
    if (connectToServer()) {
      Serial.println("We are now connected to the BLE Server.");
    } else {
      Serial.println("We have failed to connect to the server; there is nothin more we will do.");
    }
    doConnect = false;
  }

  // If we are connected to a peer BLE Server, update the characteristic each time we are reached
  // with the current time since boot.
  if (connected) {
    String newValue = "Time since boot: " + String(millis()/1000);
    Serial.println("Setting new characteristic value to \"" + newValue + "\"");
    
    // Set the characteristic's value to be the array of bytes that is actually a string.
    // pRemoteCharacteristic->writeValue(newValue.c_str(), newValue.length());
  }else if(doScan){
    BLEDevice::getScan()->start(0);  // this is just example to start scan after disconnect, most likely there is better way to do it in arduino
  }
}
