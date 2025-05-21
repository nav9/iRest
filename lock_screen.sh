#!/bin/bash

# This script is meant to put the monitor into power saving mode just before dm-tool is used to lock the screen (without swayidle, the monitor remains
# switched on even after the screen is locked). Make sure screen blanking is switched on before using this script by going to Raspberry Pi Preferences > Raspberry Pi Configuration > Display > Screen Blanking.
# This script assumes that the screen gets locked only when the User manually selects lock. To make this script runnable on lock, go to Preferences > Main Menu Editor and create a new item with the name of this script's file as the "command".
# This script also creates a SCREEN_LOCKED environment variable which allows external programs to detect if the screen is locked.

# Path to the environment file that stores information about whether the screen is locked or not
LOCK_STATUS_FILE="$HOME/.screen_locked_env"

# Function to update the lock status in the file. The file will get created if it does not exist
update_lock_status() {
    local status="$1"
    echo "export SCREEN_LOCKED=$status" > "$LOCK_STATUS_FILE"
}

# Kill existing swayidle processes
pkill -f swayidle

# Set lock status to 1 (locked) for any other program to detect if screen is locked
update_lock_status 1

# Run swayidle with timeout 1. Screen blanking will happen after 1 second
# wlopm is Wayland output power management. See its man page
swayidle -w timeout 1 'wlopm --off \*' resume 'wlopm --on \* ; pkill -f swayidle' 

# Lock the screen (actually locks only after swayidle resume happens)
/usr/bin/dm-tool lock

# Set lock status to 0 (unlocked)
update_lock_status 0

# Set screen blanking to 5 minutes (300 seconds)
swayidle -w timeout 300 'wlopm --off \*' resume 'wlopm --on \*' &

