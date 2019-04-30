#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import alsaaudio, time, audioop
import threading

class Queue: 
    def __init__(self):
        self.size = 35
        self.in_stack = []
        self.out_stack = []
        self.ordered = []

    def push(self, obj):
        self.in_stack.append(obj)

    def pop(self):
        if not self.out_stack:
            while self.in_stack:
                self.out_stack.append(self.in_stack.pop())
        return self.out_stack.pop()

    def clear(self):
        self.in_stack = []
        self.out_stack = []

    def makeOrdered(self):
        self.ordered = []
        tmp = []
        for i in range(self.size):
            item = self.pop()
            self.ordered.append(item)
            tmp.append(item)
        while tmp:
            self.out_stack.append(tmp.pop())

    def totalAvg(self):
        tot = 0
        for el in self.in_stack:
            tot += el

        for el in self.out_stack:
            tot += el

        return float(tot) / (len(self.in_stack) + len(self.out_stack))

    def firstAvg(self):
        tot = 0
        for i in range(5):
            tot += self.ordered[i]
        return tot/5.0

    def secondAvg(self):
        tot = 0
        for i in range(5,15):
            tot += self.ordered[i]
        return tot/10.0

    def thirdAvg(self):
        tot = 0
        for i in range(15,20):
            tot += self.ordered[i]
        return tot/5.0

    def fourthAvg(self):
        tot = 0
        for i in range(20,30):
            tot += self.ordered[i]
        return tot/10.0

    def fifthAvg(self):
        tot = 0
        for i in range(30,35):
            tot += self.ordered[i]
        return tot/5.0


class ClapDetector:
    def __init__(self, pcm_device_name):
        self.on_detect_func = None
        self.on_detect_func_args = None
        self.pcm_device_name = pcm_device_name
        self.called_stop = False

    def set_on_detect_func(self, func, *args):
        self.on_detect_func = func
        self.on_detect_func_args = args

    def start_detection_thread(self):
        self.called_stop = False
        th = threading.Thread(target=ClapDetector.detect, name="clap_detector_thread", args=(self,))
        th.start()

    def stop_detection_thread(self):
        self.called_stop = True

    def detection_sleep(self):
        time.sleep(0.01)
        
    def detect(self):
    
        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK, self.pcm_device_name)
    
        # Set attributes: Mono, 8000 Hz, 16 bit little endian samples
        inp.setchannels(1)
        inp.setrate(16000)
        inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    
        # The period size controls the internal number of frames per period.
        # The significance of this parameter is documented in the ALSA api.
        # For our purposes, it is suficcient to know that reads from the device
        # will return this many frames. Each frame being 2 bytes long.
        # This means that the reads below will return either 320 bytes of data
        # or 0 bytes of data. The latter is possible because we are in nonblocking
        # mode.
        inp.setperiodsize(160)
    
        queue = Queue();
        avgQueue = Queue();
    
        n = 0; 
        n2 = 0;
        while True:
            if self.called_stop:
                break
    
            # Read data from device
            l,data = inp.read()

            if not l:
                self.detection_sleep()
                continue

            err = False
            volume = -1
            try:
                volume = audioop.max(data, 2)
                if volume > 300:
                    print(volume)
            
                except: 
                print("err")
                err = True
            if err: continue

            queue.push(volume)
            avgQueue.push(volume)
            n = n + 1
            n2 = n2 + 1
            if n2 > 500:
                avgQueue.pop()

            if n > queue.size:avg = avgQueue.totalAvg()
                
                low_limit = avg + 500
                high_limit = avg + 2000

                queue.pop();
                queue.makeOrdered();
                v1 = queue.firstAvg();
                v2 = queue.secondAvg();
                v3 = queue.thirdAvg();
                v4 = queue.fourthAvg();
                v5 = queue.fifthAvg();
                
                # debug print
                if v4 - avg > 2000:
                    print("avg last fragments: " + str(avg))
                    
                    na = ['v1', 'v2', 'v3', 'v4', 'v5']
                    va = [v1, v2, v3, v4, v5]
                    for i in range(len(va)):
                        print(str(n) + ": " + na[i] + " " + str(va[i] - avg))
                
                if (v1 < low_limit and 
                    v2 < low_limit and 
                    v3 < low_limit and 
                    v4 > high_limit and 
                    v5 < low_limit):

                    # Detected clap
                    print(str(time.time())+": sgaMED")
                    if self.on_detect_func:
                        self.on_detect_func(*self.on_detect_func_args)
                    queue.clear()
                    n = 0
    
            self.detection_sleep()
