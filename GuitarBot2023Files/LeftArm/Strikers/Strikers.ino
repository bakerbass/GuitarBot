//
// Created by Raghavasimhan Sankaranarayanan on 03/30/22.
// Modified for GuitarBot by Marcus Parker on 12/7/23
// Modified for general send_msg + executeCommand by Shayahn Mirfendereski 10/30/24
// Modified for executeEvent()
// Modified by Derrick 11/14/2024 at 5:49pm
#include "src/strikerController.h"
#include "src/logger.h"
#include <Ethernet.h>
#include <EthernetUdp.h>

StrikerController* pController = nullptr;
byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED}; //mac adress
IPAddress ip(10, 2, 1, 177); //ip address

unsigned int localPort = 8888; //udp port to listen for packets on

char packetBuffer[1024];
uint8_t playcommands[6];
uint8_t frets[6];
uint8_t pickings[6];
int8_t strumAngle;
char event;

EthernetUDP udp;

bool complete = false;    // Setting this flag will start processing of received message

void setup() {
    Ethernet.init(10); // set CS pin for ethernet shield
    Ethernet.begin(mac, ip); //initialize ethernet with mac and ip addresses
    //Checks for presence of Ethernet shield. Halts if no ethernet hardware present. 
    if (Ethernet.hardwareStatus() == EthernetNoHardware) {
      LOG_LOG("Ethernet shield was not found. Sorry, can't run without hardware.");
      while (true) {
        delay(1);
      }
    } else {LOG_LOG("Ethernet shield found!");};
    //Checks for presence of etherner link.Halts if no link present. 
    if (Ethernet.linkStatus() == LinkOFF) {
      LOG_LOG("Ethernet cable is not connected.");
    } else {LOG_LOG("Ethernet cable connected!");};
    udp.begin(localPort); //begins udp on port specified above.
    Serial.begin(115200);

    delay(2000); //Added delay for output reading
    LOG_LOG("Initializing GuitarBot...");
    pController = StrikerController::createInstance();
    LOG_LOG("Initializing Pressers and Striker...");
    int err = pController->init(MotorSpec::EC45_Slider); //Sliders
   
    if (err != 0) {
        LOG_ERROR("Controller Init failed");
        return;
    }
//  int err = PController->init(MotorSpec::EC20); //Pressers
    if (err != 0) {
        LOG_ERROR("Controller Init failed");
        return;
    }
    delay(2000);
    LOG_LOG("Successfully Initialized! Controller Starting....");
    pController->start();
    delay(500);
    uint8_t frets1[6] = {1, 2, 2, 1, 1, 1};
    uint8_t playcommands1[6] = {1, 2, 2, 1, 1, 1};
    pController->executeSlideDEMO(frets1, playcommands1);
    pController->executeStrumTest(45, 100, 0);
    delay(500);
    
    pController->executeStrumTest(-45, 100, 0);
    delay(500);
    
    pController->executeStrumTest(45, 100, 0);
    delay(500);
    
    pController->executeStrumTest(-45, 100, 1);
    delay(500);
    
    pController->executeStrumTest(45, 100, 0);
    delay(500);
    
    pController->executeStrumTest(-45, 100, 1);
    delay(500);
    
    pController->executeStrumTest(45, 100, 1);
    delay(500);

    

//    pController->executeSetPickerTest('U');
//    delay(500);
//    pController->executeStrumTest('D', 50);
//    delay(500);
    uint8_t frets2[6] = {1, 1, 2, 2, 1, 1};
    uint8_t playcommands2[6] = {3, 1, 2, 2, 2, 1};
    pController->executeSlideDEMO(frets2, playcommands2);

    pController->executeStrumTest(-45, 100, 0);

    // pController->executeStrumTest('U', 50);
    // delay(5000);
    // pController->executeStrumTest('D', 50);
    // pController->executeStrumTest('U', 50);
    //Next time I'm gonna see if it's possible to output to this terminal so you can see output

    //At some point I want to test just adding to all_trajs in the traj functions and all queue pushing in executeEvent

    // delay(500);
    // pController->executeSetPickerTest('D');
    // delay(500);
    // pController->executeStrumTest('U', 30);
    // delay(500);
    // uint8_t frets3[6] = {1, 1, 1, 2, 3, 2};
    // uint8_t playcommands3[6] = {3, 3, 1, 2, 2, 2};
    // pController->executeSlide(frets3, playcommands3);
    // delay(500);
    // pController->executeSetPickerTest('U');
    // delay(500);
    // pController->executeStrumTest('D', 30);
    // delay(500);
    // uint8_t frets4[6] = {1, 1, 5, 4, 3, 3};
    // uint8_t playcommands4[6] = {3, 3, 2, 2, 2, 2};
    // pController->executeSlideDEMO(frets4, playcommands4);
    // delay(500);
    // pController->executeSetPickerTest('D');
    // delay(500);
    // pController->executeStrumTest('U', 30);
    // delay(500);
    

    LOG_LOG("Listening for commands...");   // "in format (ascii characters) <mode><id code><midi velocity>"
    //pController->executePluckTest(0);
}

void loop() {
    ethernetEvent();
    if (complete) {

        complete = false;

        LOG_LOG("slide 1: %i, slide 2: %i, slide 3: %i, slide 4: %i, slide 5: %i, slide 6: %i", frets[0], frets[1], frets[2], frets[3], frets[4], frets[5]);
        LOG_LOG("press 1: %i, press 2: %i, press 3: %i, press 4: %i, press 5: %i, press 6: %i", playcommands[0], playcommands[1], playcommands[2], playcommands[3], playcommands[4], playcommands[5]);
        LOG_LOG("pick 1: %i, pick 2: %i, pick 3: %i, pick 4: %i, pick 5: %i, pick 6: %i", pickings[0], pickings[1], pickings[2], pickings[3], pickings[4], pickings[5]);
        LOG_LOG("strummer: %i", strumAngle);
        // To do:
        // ExecuteEvent needs another variable to control which message is handled between LH, strum, and pick. Add in 'event' as a char/string variable.
      
        pController->executeEvent(event, frets, playcommands, pickings, strumAngle);
        // pController->executeSlide(frets, playcommands);
        //pController->executeSlideDEMO(fret[0], fret[1], fret[2], fret[3], fret[4], fret[5], playcommand[0], playcommand[1], playcommand[2], playcommand[3], playcommand[4], playcommand[5]);
        

        //delay(10);
    }
}

void ethernetEvent() {
    int packetSize = udp.parsePacket();
    if (packetSize) {
      udp.read(packetBuffer, 1024);
      //Convert each byte in packet_buffer to a uint8_t
      event = packetBuffer[0];
      if (event == 'L') {
        LOG_LOG("LH event");
        frets[0] = static_cast<uint8_t>(packetBuffer[1]);
        frets[1] = static_cast<uint8_t>(packetBuffer[2]);
        frets[2] = static_cast<uint8_t>(packetBuffer[3]);
        frets[3] = static_cast<uint8_t>(packetBuffer[4]);
        frets[4] = static_cast<uint8_t>(packetBuffer[5]);
        frets[5] = static_cast<uint8_t>(packetBuffer[6]);
        playcommands[0] = static_cast<uint8_t>(packetBuffer[7]);
        playcommands[1] = static_cast<uint8_t>(packetBuffer[8]);
        playcommands[2] = static_cast<uint8_t>(packetBuffer[9]);
        playcommands[3] = static_cast<uint8_t>(packetBuffer[10]);
        playcommands[4] = static_cast<uint8_t>(packetBuffer[11]);
        playcommands[5] = static_cast<uint8_t>(packetBuffer[12]);

      }
      else if (event == 'S') {
        LOG_LOG("Strum event");
        strumAngle = packetBuffer[1];
        
      }
      else if (event == 'P') {
        LOG_LOG("Pick event");
        for (int i = 1; i <= 6; i++) {
          pickings[i - 1] = static_cast<uint8_t>(packetBuffer[i]);
        }
        
        
      }
      
      complete = true;
    }        
}