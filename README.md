Introduction
============

This is a flask web application that runs on a raspberry pi used to control a EEZYbotARM MK2 with a
raspberry pi camera module mounted on it. This software allows for storing various
camera angles and allow for automated image capture of those camera angles.

![Alt text](robocam.jpg?raw=true "Robocam")
![Alt text](sample2.png?raw=true "Robocam")


I've created this for enabling remote DnD RPG sessions but can in theory be used for other turn based games.

Details for the Robot Parts other Hardware
==========================================

3D printed Parts:

EEZYBotARM Mk2 base files: https://www.thingiverse.com/thing:1454048
EEZYBotARM Mk2 improved Base: https://www.thingiverse.com/thing:2830251
EEZYBotARM Camera ARM Conversion: https://www.thingiverse.com/thing:5837656

Other Electronics not convered above:

- Polulu Maestro Mini 12 Channel
- additional SG90 micro servo
- Raspberry Pi 4
- Raspberry Pi Camera Module 3 (This can be customized to any Pi compatible Camera) w/ a long Pi Camera Cable
  

Requirements
============

Because of the libraries used, this requires a raspberry pi 4 to completely work, however this can
be done on a desktop for development purposes.

Install
========

Setup python requirements

```
pip install -r requirements.txt
```

How to start
============

When running  under a non raspberry pi environment use the following command below (with TEST=true)

```
TEST=true python -m flask --debug run --host=0.0.0.0 --port=5001
```

otherwise

```
python -m flask run --host=0.0.0.0 --port=5001
```

The Application Dashboard should now be available at the specified port: 5001