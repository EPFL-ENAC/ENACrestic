#!/usr/bin/env python3

import getpass
import os
import pwd
import sys

from enacrestic import __version__

# Package related
VERSION_INFO = tuple(map(lambda x: int(x), __version__.split(".")))

PYPI_PROJECT_URL = "https://pypi.org/pypi/enacrestic/json"
UPGRADE_DOC = "https://github.com/EPFL-ENAC/ENACrestic#upgrade"
DEF_CHECK_NEW_VERSION_EVERY_N_DAYS = 7

# App related
DEF_BACKUP_EVERY_N_MINUTES = 30
DEF_FORGET_EVERY_N_BACKUPS = 10

DEF_GUI_AUTOSTART = False

NB_CHRONOS_TO_SAVE = 10

ENACRESTIC_PREF_FOLDER = os.path.expanduser("~/.enacrestic")

RESTIC_USER_PREFS = {
    "FILESFROM": os.path.join(ENACRESTIC_PREF_FOLDER, "bkp_include"),
    "EXCLUDEFILE": os.path.join(ENACRESTIC_PREF_FOLDER, "bkp_exclude"),
    "PASSWORDFILE": os.path.join(ENACRESTIC_PREF_FOLDER, ".pw"),
    "ENV": os.path.join(ENACRESTIC_PREF_FOLDER, "env.sh"),
}
RESTIC_LOGFILE = os.path.join(ENACRESTIC_PREF_FOLDER, "last_backups.log")
RESTIC_CONFFILE = os.path.join(ENACRESTIC_PREF_FOLDER, "prefs.json")
RESTIC_STATEFILE = os.path.join(ENACRESTIC_PREF_FOLDER, "state.json")
PRE_BACKUP_HOOK = os.path.join(ENACRESTIC_PREF_FOLDER, "pre_backup")
RESTIC_AUTOSTART_FILE = os.path.expanduser("~/.config/autostart/enacrestic.desktop")

LOGFILE_ROTATION_EVERY_N_DAYS = 30
LOGFILE_ROTATION_BACKUP_COUNT = 5

ENACRESTIC_BIN = os.path.abspath(sys.argv[0])

USERNAME = getpass.getuser()
UID = pwd.getpwnam(USERNAME).pw_uid
PID_FILE = os.path.join(ENACRESTIC_PREF_FOLDER, "enacrestic.pid")

ICONS_FOLDER = os.path.abspath(f"{__file__}/../pixmaps")

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
