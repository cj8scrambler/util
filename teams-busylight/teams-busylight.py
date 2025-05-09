import logging
from time import sleep
from busylight.lights.embrava import Blynclight
from busylight.manager import LightManager
from busylight.effects import Effects
from teams import Teams
from activity import Activity

logging.basicConfig(level=logging.INFO)

POLL_RATE_SEC = 15
VALID_AVAIL_ACTIV = [("Available", "Available"),
                     ("Busy", "InACall"),
                     ("Busy", "InAConferenceCall"),
                     ("Away", "Away"),
                     ("BeRightBack", "BeRightBack"),
                     ("DoNotDisturb", "Presenting")]
ERROR_COLOR = (171, 71, 188) # Purple

class TeamsBusylight:

  # Map Teams status to RGB color: ((red, green, blue) , flash)
  colormap = {
    'DoNotDisturb': ((255,   0, 0), True),  # flash red
    'Busy':         ((255,   0, 0), False), # red
    'Available':    ((  0, 128, 0), False), # green
    'AvailableIdle':((255,  64, 0), False), # orange (looks yellow on embrava)
    'Away':         ((255,  64, 0), False), # orange (looks yellow on embrava)
    'BeRightBack':  ((255,  64, 0), False), # orange (looks yellow on embrava)
    'Offline':      ((  0,   0, 0), False), # black (off)
  }

  def __init__(self):
    self.activity = Activity()
    self.teams = Teams(POLL_RATE_SEC)
    self.light = None
    self.log_light = True

  def update(self):
    # If there is local activity, but Team's status is
    # "Away" then update Team's status to "Available"
    teams_status = self.teams.get_status()
    activity_status = self.activity.get_status()
    if (activity_status == "Available" and teams_status == "Away"):
      logging.info(f"Update Teams status from {teams_status} to {activity_status}")
      self.teams.set_status(activity_status)
      teams_status = self.teams.get_status()

    # Update LED based on Teams status
    if teams_status in self.colormap:
      color = self.colormap[teams_status][0]
    else:
      logging.Error(f"Missing color map entry for Teams status: {teams_status}")
      color = ERROR_COLOR

    # If light has never been connected
    if self.light is None:
      if Blynclight.available_lights():
        self.light = Blynclight.first_light()
      else:
        if self.log_light:
          logging.warning("No light available")
          self.log_light = False
        else:
          logging.debug("No light available")

    if self.light:
      # Check if light was unplugged
      if self.light.is_unplugged and Blynclight.available_lights():
        logging.info("Light was re-connected")
        self.light = Blynclight.first_light()
        self.log_light = True

      if self.light.is_pluggedin:
        self.light.on(color)
        logging.debug(f"Set light color: {color}")
      else:
        if self.log_light:
          logging.warning("Light was removed")
          self.log_light = False
        else:
          logging.debug("Light was removed")

# Would like to get flash/pulse to work:
#    if self.colormap[teams_status][1]:
#      pulse_effect = Effects.for_name("gradient")(color, 0.75/16, 8)
#      self.manager.apply_effect(pulse_effect)
#    else:
#      self.manager.on(color)


if __name__ == '__main__':
  import sdnotify

  notifier = sdnotify.SystemdNotifier()
  tbl = TeamsBusylight()

  notifier.notify("READY=1")

  try:
    while True:
      tbl.update()
      sleep(POLL_RATE_SEC)
  except KeyboardInterrupt:
    print("\nStopping")
    tbl.light.off()
