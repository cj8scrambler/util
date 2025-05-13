import os
import sys
import time
import subprocess
import json
import logging

# Using MGC to interact with Micrsoft Graph so that I don't have
# to register this app.
MGC_SESSION_ID = "14d82eec-204b-4c2f-b7e8-296a70dab67e"

VALID_AVAIL_ACTIV = [("Available", "Available"),
                     ("Busy", "InACall"),
                     ("Busy", "InAConferenceCall"),
                     ("Away", "Away"),
                     ("DoNotDisturb", "Presenting")]

class Teams:
  def __init__(self, update_rate_sec=15):
    # Running this verifies the connection
    self.get_status()

    # expiration duration must be 5 - 240 minutes
    update_rate_sec = max(update_rate_sec, 5*60)
    update_rate_sec = min(update_rate_sec, 240*60)
    self.expire_duration = f"PT{update_rate_sec}S"

  def _mgc_command(self, command):
    """Executes a system call and returns the output."""
    try:
      result = subprocess.run(command, capture_output=True, text=True, check=False)
      if result.returncode != 0:
        if "Token acquisition failed" in result.stderr:
          print("Error: mgc is not not authenticated.  Login with:")
          print("mgc login --scopes User.Read Team.ReadBasic.All Presence.ReadWrite")
          sys.exit(1);
        else:
          print(f"Warning command [{command}] returned result code: {result.returncode}")
          print(result.stderr)
          return None
      return result.stdout
    except FileNotFoundError as e:
      print("Error: mgc not found.  Install instructions https://learn.microsoft.com/en-us/graph/cli/installation?tabs=linux")
      sys.exit(1);
    except subprocess.CalledProcessError as e:
      print(f"Error executing command: {e}")
      sys.exit(1);

  def get_status(self):
    response = self._mgc_command(("mgc", "users", "presence", "get", "--user-id", "me"))
    if response:
      presence = json.loads(response)
      logging.debug(f"Teams status is: availability: {presence['availability']}  activity: {presence['activity']}")
      return presence['availability']
    return None

  def set_status(self, status):
    validated = False;
    for (availability, activity) in VALID_AVAIL_ACTIV:
      if status.upper() == availability.upper():
        logging.debug(f"Teams set_status({status}) mapping to: ({availability}, {activity})")
        validated = True;
        break;
    if validated:
      cmd = ("mgc", "users", "presence", "set-presence", "post", "--user-id", "me")
      body = '{"sessionId": ' + f'"{MGC_SESSION_ID}", '
      body += f'"availability": "{availability}", '
      body += f'"activity": "{activity}", '
      body += f'"expirationDuration": "{self.expire_duration}"' + '}'
      logging.debug(f"set Teams status to: {status} by running:")
      logging.debug(cmd +  ("--body", body))
      self._mgc_command(cmd +  ("--body", body))
    else:
      print(f"Error: Unable to map status '{status}' to a Teams activity: {[t[0] for t in VALID_AVAIL_ACTIV]}")
    return(None)

