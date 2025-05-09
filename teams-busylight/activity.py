import os
import time
import logging
from pathlib import Path

class Activity:
  def __init__(self, activity_file = os.path.join(Path.home(), ".activity"),
               idle_sec = 60, away_sec = 300, offline_sec = 1800):
    self.file = activity_file
    self.thresholds = { 'idle': idle_sec,
                        'away': away_sec,
                        'offline': offline_sec }
    self._last_activity = None

  def last_activity(self):
    return (int(time.time() - os.path.getmtime(self.file)))

  def new_status(self):
    """ Only returns activity status if it has changed since the last call """
    activity = self.get_status()
    if (activity != self._last_activity):
      logging.debug(f"Local activity change: {self._last_activity} -> {activity}")
      self._last_activity = activity
      return activity
    return None

  def get_status(self):
    """ Maps idle time to an activity state """
    time = self.last_activity()
    if (time < self.thresholds['idle']):
      activity = "Available"
    elif (time < self.thresholds['away']):
      activity = "Idle"
    elif (time < self.thresholds['offline']):
      activity = "Away"
    else:
      activity = "Offline"

    logging.debug (f"Local idle time is: {time} mapped to: {activity}")
    return activity
