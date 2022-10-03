#!/usr/bin/env python3

import os
import sys
import pwd
import getpass

# Package related
VERSION_INFO = (0, 1, 10)
VERSION = ".".join([str(num) for num in VERSION_INFO])

PYPI_PROJECT_URL = "https://pypi.org/pypi/ENACrestic/json"
UPGRADE_DOC = "https://github.com/EPFL-ENAC/ENACrestic#upgrade"
CHECK_NEW_VERSION_EVERY_N_DAYS = 7

# App related
DEF_BACKUP_EVERY_N_MINUTES = 30
DEF_FORGET_EVERY_N_ITERATIONS = 10

ENACRESTIC_PREF_FOLDER = os.path.expanduser("~/.enacrestic")

RESTIC_USER_PREFS = {
    "FILESFROM": os.path.join(ENACRESTIC_PREF_FOLDER, "bkp_include"),
    "EXCLUDEFILE": os.path.join(ENACRESTIC_PREF_FOLDER, "bkp_exclude"),
    "PASSWORDFILE": os.path.join(ENACRESTIC_PREF_FOLDER, ".pw"),
    "ENV": os.path.join(ENACRESTIC_PREF_FOLDER, "env.sh"),
}
RESTIC_LOGFILE = os.path.join(ENACRESTIC_PREF_FOLDER, "last_backups.log")
RESTIC_STATEFILE = os.path.join(ENACRESTIC_PREF_FOLDER, "state.json")
RESTIC_AUTOSTART_FILE = os.path.expanduser("~/.config/autostart/enacrestic.desktop")

LOGFILE_ROTATION_EVERY_N_DAYS = 30
LOGFILE_ROTATION_BACKUP_COUNT = 5

ENACRESTIC_BIN = os.path.abspath(sys.argv[0])

USERNAME = getpass.getuser()
UID = pwd.getpwnam(USERNAME).pw_uid
PID_FILE = f"/run/user/{UID}/enacrestic.pid"

ICONS_FOLDER = os.path.abspath(f"{__file__}/../pixmaps")

ICONS = {
    "program_just_launched": {
        False: f"{ICONS_FOLDER}/just_launched.png",
        True: f"{ICONS_FOLDER}/just_launched_badge.png",
    },
    "backup_in_pause": {
        False: f"{ICONS_FOLDER}/backup_in_pause.png",
        True: f"{ICONS_FOLDER}/backup_in_pause_badge.png",
    },
    "backup_success": {
        False: f"{ICONS_FOLDER}/backup_success.png",
        True: f"{ICONS_FOLDER}/backup_success_badge.png",
    },
    "backup_failed": {
        False: f"{ICONS_FOLDER}/backup_failed.png",
        True: f"{ICONS_FOLDER}/backup_failed_badge.png",
    },
    "backup_no_network": {
        False: f"{ICONS_FOLDER}/backup_no_network.png",
        True: f"{ICONS_FOLDER}/backup_no_network_badge.png",
    },
    "backup_in_progress": {
        False: f"{ICONS_FOLDER}/backup_in_progress.png",
        True: f"{ICONS_FOLDER}/backup_in_progress.png",
    },
    "backup_in_progress_failed": {
        False: f"{ICONS_FOLDER}/backup_in_progress.png",
        True: f"{ICONS_FOLDER}/backup_in_progress.png",
    },
    "backup_in_progress_no_network": {
        False: f"{ICONS_FOLDER}/backup_in_progress.png",
        True: f"{ICONS_FOLDER}/backup_in_progress.png",
    },
    "forget_in_progress": {
        False: f"{ICONS_FOLDER}/forget_in_progress.png",
        True: f"{ICONS_FOLDER}/forget_in_progress.png",
    },
}
