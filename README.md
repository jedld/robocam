Introduction
============

This is a flask web application that runs on a raspberry pi used to control a EEZYbotARM MK2 with a
raspberry pi camera module mounted on it. This software allows for storing various
camera angles and allow for automated image capture of those camera angles.

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