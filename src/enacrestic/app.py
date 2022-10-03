#!/usr/bin/env python3

"""
Does :

+ Run every 30 minutes : `restic backup`
+ Run every 10 iteration : `restic forget` (for the backup rotation)

It uses the following files to be configured :

+ ~/.enacrestic/bkp_include
  This is given to --files-from option
+ ~/.enacrestic/bkp_exclude
  This is given to --exclude-file option
+ ~/.enacrestic/.pw
  This is given to --password-file option
+ ~/.enacrestic/env.sh
  This file has to configure env variables such as :
  + RESTIC_REPOSITORY
  + AWS_ACCESS_KEY_ID (if using S3)
  + AWS_SECRET_ACCESS_KEY (if using S3)

It writes to the following files :

+ ~/.enacrestic/last_backups.log
  All execution log
+ ~/.enacrestic/state.json
  State of previous execution
"""

import os
import sys
import webbrowser

from pidfile import AlreadyRunningError, PIDFile
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QSystemTrayIcon

from enacrestic import const
from enacrestic.logger import Logger
from enacrestic.restic_backup import ResticBackup
from enacrestic.state import State


class QTEnacRestic(QApplication):
    """
    Main app, starting QApplication and QSystemTrayIcon when it's ready.
    """

    def __init__(self, argv, logger, state):
        super().__init__(argv)
        self.logger = logger
        self.state = state

        QTimer.singleShot(2000, self._start_when_systray_available)

    def _start_when_systray_available(self):
        self.tray_icon = QSystemTrayIcon(
            QIcon(const.ICONS["program_just_launched"][False]), parent=self
        )
        self.tray_icon.show()

        menu = QMenu()
        # Entry to display informations to the user
        info_action = menu.addAction("ENACrestic launched")

        # Entry to display informations when an upgrade is available
        upgrade_action = menu.addAction(
            "New version is available.\nClick here to read the upgrade instructions."
        )
        upgrade_action.triggered.connect(self.open_upgrade_instructions)
        upgrade_action.setVisible(False)

        menu.addSection("Actions")

        # Entry to set if the application has
        # to auto-start with the session
        autostart_action = QAction("Auto-start", checkable=True)
        menu.addAction(autostart_action)

        # Entry to exit the application by the user
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.quit)

        self.tray_icon.setContextMenu(menu)

        self.state.connect_to_gui(
            self.tray_icon, info_action, upgrade_action, autostart_action
        )
        self.restic_backup = ResticBackup(self.state, self.logger)
        self.timer = QTimer()
        self.timer.timeout.connect(self.restic_backup.run)
        self.timer.start(self.state.backup_every_n_minutes * 60_000)

        self.check_for_latest_version_timer = QTimer()
        self.check_for_latest_version_timer.timeout.connect(
            self.state.maybe_check_for_latest_version
        )
        self.check_for_latest_version_timer.start(86_400_000)  # every hour

    def open_upgrade_instructions(self):
        webbrowser.open(const.UPGRADE_DOC)


def main():
    # Create pref folder if doesn't exist yet
    if not os.path.exists(const.ENACRESTIC_PREF_FOLDER):
        os.makedirs(const.ENACRESTIC_PREF_FOLDER)

    with Logger() as logger:
        try:
            with PIDFile(const.PID_FILE):
                with State(logger) as state:
                    app = QTEnacRestic(sys.argv, logger, state)
                    sys.exit(app.exec_())
        except AlreadyRunningError:
            logger.write("Already running -> quit")
