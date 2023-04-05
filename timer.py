import time

ms = time.time_ns() // 1_000_000

timers = {}

class Timer:

    timers = {}

    @staticmethod
    def startTimer(text):
        global timers
        timers[text] = time.time_ns() // 1_000
    
    @staticmethod
    def endTimer(text):
        global timers
        if text in timers:
            ans = time.time_ns() // 1_000 - timers[text]
            del timers[text]
            return ans