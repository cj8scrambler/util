# teams-busylight
Microsft Teams has some basic Linux support via a webapp.  However this
doesn't work the busylights I have in the office and it doesn't keep
my status up to date when I'm working in my [shell](https://tabby.sh) all day.
This crude python script runs in the background and does two things:
  * Updates my status to Available when I'm working in shell
  * Sets my local busy light color based on Teams status

## Setup

**mgc**
This script uses the mgc utility to get and set Teams status.  This avoids
having to register directly with Microsoft as an app.

  * [Install mgc](https://learn.microsoft.com/en-us/graph/cli/installation?tabs=linux)
  * Authenticate and authorize with: `mgc login --scopes User.Read Team.ReadBasic.All Presence.ReadWrite`

**shell**
Local acitivity is based on the timestamp of a marker file [~/.activity].
The command prompt can be used to update the timestamp on this file while
working in the shell.  Add the following to your ~/.bashrc:
```
ACTIVITY_FILE=${HOME}/.activity
activity() {
  if [[ ! -f ${ACTIVITY_FILE} ]]
  then
    mkdir -p $(dirname ${ACTIVITY_FILE})
  fi
  touch ${ACTIVITY_FILE}
}
PROMPT_COMMAND="activity; $PROMPT_COMMAND"
```

**busylight**
If an [Embrava Blynclightght](https://www.embrava.com/products) is present, it
will update the color based on the Teams status.  This could easily be changed
to any other light supported by the [busylight-for-humans](https://pypi.org/project/busylight-for-humans/)
python package.

**systemd**
To have this script always running in the background, a user service can be setup.
Set the path to the script in the `ExecStart` line of [teams-busylight.service](teams-busylight.service).
Then install the user service with:
```
mkdir -p ~/.config/systemd/user
cp teams-busylight.service ~/.config/systemd/user/teams-busylight.service
systemctl --user daemon-reload
systemctl --user enable teams-busylight
systemctl --user start
```
