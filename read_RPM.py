

import time
import pigpio 

class reader:

   def __init__(self, pi, gpio, pulses_per_rev=1.0, weighting=0.0, min_RPM=5.0):

      self.pi = pi
      self.gpio = gpio
      self.pulses_per_rev = pulses_per_rev

      if min_RPM > 1000.0:
         min_RPM = 1000.0
      elif min_RPM < 1.0:
         min_RPM = 1.0

      self.min_RPM = min_RPM

      self._watchdog = 200 # Milliseconds.

      if weighting < 0.0:
         weighting = 0.0
      elif weighting > 0.99:
         weighting = 0.99

      self._new = 1.0 - weighting # Weighting for new reading.
      self._old = weighting       # Weighting for old reading.

      self._high_tick = None
      self._period = None

      pi.set_mode(gpio, pigpio.INPUT)

      self._cb = pi.callback(gpio, pigpio.RISING_EDGE, self._cbf)
      pi.set_watchdog(gpio, self._watchdog)

   def _cbf(self, gpio, level, tick):

      if level == 1: # Rising edge.

         if self._high_tick is not None:
            t = pigpio.tickDiff(self._high_tick, tick)

            if self._period is not None:
               self._period = (self._old * self._period) + (self._new * t)
            else:
               self._period = t

         self._high_tick = tick

      elif level == 2: # Watchdog timeout.

         if self._period is not None:
            if self._period < 2000000000:
               self._period += (self._watchdog * 1000)

   def RPM(self):
      """
      Returns the RPM.
      """
      RPM = 0.0
      if self._period is not None:
         RPM = 60000000.0 / (self._period * self.pulses_per_rev)
         if RPM < self.min_RPM:
            RPM = 0.0

      return RPM

   def cancel(self):
      """
      Cancels the reader and releases resources.
      """
      self.pi.set_watchdog(self.gpio, 0) # cancel watchdog
      self._cb.cancel()

if __name__ == "__main__":

   import time
   import pigpio
   import read_RPM
   import datetime

   RPM_GPIO = 4
   RUN_TIME = 120.0
   SAMPLE_TIME = 2.0
   F=0.86

   pi = pigpio.pi()

   p = read_RPM.reader(pi, RPM_GPIO)

   start = time.time()

   while (time.time() - start) < RUN_TIME:

      time.sleep(SAMPLE_TIME)

      RPM = p.RPM()
      POWER= RPM * F
      DATE_TIME=datetime.datetime.now()
     
      print("{},{},{}".format(float(RPM+0.5),POWER,DATE_TIME))

   p.cancel()

   pi.stop()

