import sys
import alsaaudio, time, audioop
import threading
import clapdetector as cld
import ..neochi

clap_detector = cld.ClapDetector("default:CARD=Device")
print(alsaaudio.PCM_CAPTURE)
print(alsaaudio.PCM_NONBLOCK)
#alsaaudio.pcms()
clap_detector.detect()
