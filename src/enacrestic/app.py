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
import re
import sys
import time
import webbrowser
from enacrestic import const
from enacrestic.logger import Logger
from enacrestic.state import State
from pidfile import AlreadyRunningError, PIDFile
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer, QProcess, QProcessEnvironment
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction


class ResticBackup:
    """
    Manages the execution of restic command
    """

    def __init__(self, state, logger):
        self.state = state
        self.logger = logger
        self._load_env_variables()

    def run(self):
        if not self.state.want_to_backup():
            self.logger.write_new_date_section()
            self.logger.write(
                f"Backup not launched. " f"Current state is {self.state.current_state}"
            )
            return

        # Run restic backup
        self._run_backup()
        self.logger.write()

    def _load_env_variables(self):
        """
        Load expected env vars from ~/.enacrestic/env.sh
        to be used by restic commands
        """
        self.env = QProcessEnvironment.systemEnvironment()
        variables_i_search = [
            r"RESTIC_\S+",
            r"AWS_ACCESS_KEY_ID",
            r"AWS_SECRET_ACCESS_KEY",
        ]
        try:
            with open(const.RESTIC_USER_PREFS["ENV"], "r") as f:
                for line in f.readlines():
                    # remove comments
                    # A) starting with #
                    # B) having ' #'
                    line = re.sub(r"^#.*", "", line)
                    line = re.sub(r"\s+#.*", "", line)

                    for var in variables_i_search:
                        match = re.match(r"export (%s)=(.*)$" % var, line)
                        if match:
                            self.env.insert(match.group(1), match.group(2))
        except FileNotFoundError:
            pass
        if not self.env.contains("RESTIC_REPOSITORY"):
            self.logger.write(
                f'Warning: {const.RESTIC_USER_PREFS["ENV"]} '
                f"seems not configured correctly"
            )

    def _run_backup(self):
        self.logger.write_new_date_section()
        self.logger.write("Running restic backup!")
        cmd = "restic"
        args = [
            "backup",
            "--files-from",
            const.RESTIC_USER_PREFS["FILESFROM"],
            "--password-file",
            const.RESTIC_USER_PREFS["PASSWORDFILE"],
        ]
        if os.path.isfile(const.RESTIC_USER_PREFS["EXCLUDEFILE"]):
            args += ["--exclude-file", const.RESTIC_USER_PREFS["EXCLUDEFILE"]]
        self._run(cmd, args)

    def _run_forget(self):
        self.logger.write_new_date_section()
        self.logger.write("Running restic forget!")
        cmd = "restic"
        args = [
            "forget",
            "--prune",
            "-g",
            "host",
            "-c",
            "--password-file",
            const.RESTIC_USER_PREFS["PASSWORDFILE"],
            "--keep-last",
            "3",
            "--keep-hourly",
            "24",
            "--keep-daily",
            "7",
            "--keep-weekly",
            "4",
            "--keep-monthly",
            "12",
            "--keep-yearly",
            "5",
        ]
        self._run(cmd, args)

    def _run(self, cmd, args):
        self.p = QProcess()
        self.p.setProcessEnvironment(self.env)
        self.p.readyReadStandardOutput.connect(self._handle_stdout)
        self.p.readyReadStandardError.connect(self._handle_stderr)
        self.p.stateChanged.connect(self._handle_state)
        self.p.finished.connect(self._process_finished)
        self.p.start(cmd, args)
        self.current_error = ""

    def _handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.logger.write(stdout)

    def _handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        if re.search(r"timeout", stderr):
            self.current_error = "timeout"
        self.logger.error(stderr)

    def _handle_state(self, proc_state):
        if proc_state == QProcess.Starting:
            self.current_time_starting = time.time()
        elif proc_state == QProcess.NotRunning:
            self.current_chrono = time.time() - self.current_time_starting

    def _process_finished(self):
        exitCode = self.p.exitCode()
        self.logger.write(
            f"Process finished ({exitCode}) in " f"{self.current_chrono:.3f} seconds.\n"
        )
        next_action = ""
        if self.p.exitStatus() == QProcess.NormalExit:
            if exitCode == 0:
                next_action = self.state.finished_restic_cmd("ok", self.current_chrono)
            else:
                if self.current_error == "timeout":
                    self.state.finished_restic_cmd("no network", self.current_chrono)
                else:
                    self.state.finished_restic_cmd("failed", self.current_chrono)
        else:
            self.state.finished_restic_cmd("failed", self.current_chrono)

        self.p = None
        if next_action == "run forget":
            self._run_forget()


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
