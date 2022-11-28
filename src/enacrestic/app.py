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
  State of the app (useful for upcoming executions)
+ ~/.enacrestic/prefs.json
  User preferences
"""

import datetime
import functools
import json
import os
import signal
import socket
import sys
import webbrowser

import requests
from pidfile import AlreadyRunningError, PIDFile
from PyQt5.QtCore import QCoreApplication, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtNetwork import QAbstractSocket
from PyQt5.QtWidgets import QAction, QApplication, QMenu, QSystemTrayIcon

from enacrestic import __version__, const
from enacrestic.conf import Conf
from enacrestic.logger import Logger
from enacrestic.restic_backup import ResticBackup
from enacrestic.state import CurrentOperation, State, Status
from enacrestic.utils import utc_to_local


class QTNoGuiApp(QCoreApplication):
    """
    Main app, starting QCoreApplication
    used when --no-gui (typically on server)
    """

    def __init__(self, argv, app):
        super().__init__(argv)
        self.app = app

    def update_system_tray(self):
        pass  # no-gui


class QTGuiApp(QApplication):
    """
    Main app, starting QApplication and QSystemTrayIcon when it's ready.
    """

    def __init__(self, argv, app):
        super().__init__(argv)
        self.tray_icon = None
        self.app = app

        # start app when systray is available
        # workaround to fix automatic start when ENACrestic is launched at the session opening
        QTimer.singleShot(2000, self._start_app)

    def _start_app(self):
        """
        Start Qt System tray when everything is ready
        """
        icon_path = self.app.state.get_icon()
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), parent=self)
        self.tray_icon.show()

        menu = QMenu()
        # Entry to display informations to the user
        self.info_action = menu.addAction("ENACrestic launched")

        # Entry to display informations when an upgrade is available
        self.upgrade_action = menu.addAction(
            "New version is available.\nClick here to read the upgrade instructions."
        )
        self.upgrade_action.triggered.connect(self.open_upgrade_instructions)
        self.upgrade_action.setVisible(False)

        menu.addSection("Actions")

        # Entry to set if the application has
        # to auto-start with the session
        self.autostart_action = QAction("Auto-start", checkable=True)
        self.autostart_action.triggered.connect(self._toggle_autostart)
        self.autostart_action.setChecked(self.app.conf.gui_autostart)
        menu.addAction(self.autostart_action)

        # Entry to exit the application by the user
        exit_action = menu.addAction("Exit")
        exit_action.triggered.connect(self.app.quit)

        self.tray_icon.setContextMenu(menu)

        self.update_system_tray()

    def open_upgrade_instructions(self):
        webbrowser.open(const.UPGRADE_DOC)

    def update_system_tray(self):
        """
        update system tray according to the state
        + icon to current state
        + info_action with current state infos
        + Show upgrade_action if needed
        """

        def _str_date(utc_dt):
            """
            return nice date (with only h:m:s if it's in the last 24h)
            """

            if datetime.datetime.utcnow() - utc_dt < datetime.timedelta(days=1):
                return "at %s" % utc_to_local(utc_dt).strftime("%H:%M:%S")
            else:
                return "on %s" % utc_to_local(utc_dt).strftime("%Y-%m-%d %H:%M:%S")

        def _str_duration(seconds, shortest=False):
            """
            return nice duration as __h __m __s
            if not shortest :
                __s | __m __s | __h __m __s
            if shortest :
                __h | __m | __s |
                __h __m | __m __s |
                __h __m __s
            """
            seconds = int(seconds)
            hours, seconds = divmod(seconds, 3600)
            minutes, seconds = divmod(seconds, 60)
            if shortest:
                if hours > 0:
                    if minutes > 0:
                        if seconds > 0:
                            return f"{hours}h {minutes}m {seconds}s"
                        else:
                            return f"{hours}h {minutes}m"
                    else:
                        if seconds > 0:
                            return f"{hours}h {minutes}m {seconds}s"
                        else:
                            return f"{hours}h"
                else:
                    if minutes > 0:
                        if seconds > 0:
                            return f"{minutes}m {seconds}s"
                        else:
                            return f"{minutes}m"
                    else:
                        return f"{seconds}s"
            else:
                if hours > 0:
                    return f"{hours}h {minutes}m {seconds}s"
                elif minutes > 0:
                    return f"{minutes}m {seconds}s"
                else:
                    return f"{seconds}s"

        def _str_last_chronos(subject, list_chronos):
            """
            return msg with latest chrono and average over the last n
            """
            nb_chronos = len(list_chronos)
            if nb_chronos == 0:
                return ""
            msg = """
-> latest %s %s : %s""" % (
                subject,
                _str_date(list_chronos[0][0]),
                _str_duration(list_chronos[0][1]),
            )
            if nb_chronos >= 2:
                sum_chronos = sum([chrono[1] for chrono in list_chronos])
                average_chrono = sum_chronos / nb_chronos
                msg += """
average over the last %d : %s""" % (
                    nb_chronos,
                    _str_duration(average_chrono),
                )
            return msg

        if self.tray_icon is None:
            return

        icon_path = self.app.state.get_icon()
        self.tray_icon.setIcon(QIcon(icon_path))

        state_msg = f"ENACrestic {__version__}\n\n"

        if self.app.state.current_operation == CurrentOperation.JUST_LAUNCHED:
            state_msg += (
                "Just launched,\n"
                "a backup will be done every "
                f"{_str_duration(self.app.conf.backup_every_n_minutes * 60, True)}."
            )
        elif self.app.state.current_operation == CurrentOperation.IDLE:
            if self.app.state.current_status == Status.OK:
                state_msg += "Last backup was successful"
                if self.app.state.pre_backup_failed:
                    state_msg += " but pre-backup hook failed"
            elif self.app.state.current_status == Status.LAST_OPERATION_FAILED:
                state_msg += (
                    f"Last operation failed, {_str_date(self.app.state.last_failed_utc_dt)}\n"
                    f"see {const.RESTIC_LOGFILE} for details."
                )
            if self.app.state.current_status == Status.NO_NETWORK:
                state_msg += (
                    f"Network timeout {_str_date(self.app.state.last_failed_utc_dt)}"
                )
        elif (
            self.app.state.current_operation == CurrentOperation.PRE_BACKUP_IN_PROGRESS
        ):
            state_msg += "Pre-backup in progress"
            if self.app.restic_backup.current_utc_dt_starting is not None:
                state_msg += f" (started {_str_date(self.app.restic_backup.current_utc_dt_starting)})"
        elif self.app.state.current_operation == CurrentOperation.BACKUP_IN_PROGRESS:
            state_msg += "Backup in progress"
            if self.app.restic_backup.current_utc_dt_starting is not None:
                state_msg += f" (started {_str_date(self.app.restic_backup.current_utc_dt_starting)})"
        elif self.app.state.current_operation == CurrentOperation.FORGET_IN_PROGRESS:
            state_msg += "Cleanup in progress"
            if self.app.restic_backup.current_utc_dt_starting is not None:
                state_msg += f" (started {_str_date(self.app.restic_backup.current_utc_dt_starting)})"
        elif self.app.state.current_operation == CurrentOperation.UNLOCK_IN_PROGRESS:
            state_msg += "Unlock in progress"
            if self.app.restic_backup.current_utc_dt_starting is not None:
                state_msg += f" (started {_str_date(self.app.restic_backup.current_utc_dt_starting)})"

        # Add conditionnal stats on last backups and last cleanups
        last_chronos = _str_last_chronos("backup", self.app.state.prev_backup_chronos)
        last_chronos += _str_last_chronos("cleanup", self.app.state.prev_forget_chronos)
        if last_chronos != "":
            state_msg += "\n"
            state_msg += last_chronos
        self.info_action.setText(state_msg)

        # show / hide upgrade_action
        self.upgrade_action.setVisible(self.app.state.version_need_upgrade())

    def _toggle_autostart(self):
        """
        Save and apply user's choice to autostart or not
        """

        gui_autostart = self.autostart_action.isChecked()
        self.app.conf.set(gui_autostart=gui_autostart)
        if gui_autostart:
            # Want the app to autostart with user's session
            autostart_folder = os.path.dirname(const.RESTIC_AUTOSTART_FILE)
            os.makedirs(autostart_folder, exist_ok=True)
            with open(const.RESTIC_AUTOSTART_FILE, "w") as f:
                f.write(
                    f"""\
[Desktop Entry]
Name=ENACrestic
Comment=Automated Backup with restic
Exec={const.ENACRESTIC_BIN}
Icon=enacrestic
Terminal=false
Type=Application
Encoding=UTF-8
Categories=Utility;Archiving;
Keywords=backup;enac;restic
Name[en_US]=ENACrestic
X-GNOME-Autostart-enabled=true
"""
                )
        else:
            # Users doesn't want ENACrestic to autostart
            try:
                os.remove(const.RESTIC_AUTOSTART_FILE)
            except FileNotFoundError:
                pass


class SignalWatchdog(QAbstractSocket):
    """
    Watchdog to propagates system signals from Python to QEventLoop
    https://stackoverflow.com/a/65802260/446302
    This is necessary to handle SIGINT signals
    """

    def __init__(self):
        super().__init__(QAbstractSocket.SctpSocket, None)
        self.writer, self.reader = socket.socketpair()
        self.writer.setblocking(False)
        signal.set_wakeup_fd(self.writer.fileno())  # Python hook
        self.setSocketDescriptor(self.reader.fileno())  # Qt hook
        self.readyRead.connect(lambda: None)  # Dummy function call


def sigterm_handler(app, signal_num, stack_frame):
    """
    Handler for the SIGINT signal
    Will ensures that everything is closed on SIGTERM
    """
    app.quit()


class App:
    def __init__(self, gui_enabled=True):
        self.gui_enabled = gui_enabled
        # Create pref folder if doesn't exist yet
        if not os.path.exists(const.ENACRESTIC_PREF_FOLDER):
            os.makedirs(const.ENACRESTIC_PREF_FOLDER)

        with Logger(self.gui_enabled) as self.logger:
            try:
                with PIDFile(const.PID_FILE):
                    with Conf() as self.conf:
                        with State(self) as self.state:
                            self.restic_backup = ResticBackup(self)
                            self._start_app()
                            sys.exit(self.qt_app.exec_())
            except AlreadyRunningError:
                self.logger.write("Already running -> quit")

    def _start_app(self):
        """
        + Start GUI/noGUI Qt
        + manages SIGTERM
        + Launch timers that will trigger expected operations
        """
        if self.gui_enabled:
            self.qt_app = QTGuiApp(sys.argv, self)
        else:
            self.qt_app = QTNoGuiApp(sys.argv, self)
        signal.signal(
            signal.SIGTERM,
            functools.partial(
                sigterm_handler,
                self,
            ),
        )

        self.next_backup_timer = QTimer()
        self.next_backup_timer.timeout.connect(self.restic_backup.run)
        self.next_backup_timer.start(self.conf.backup_every_n_minutes * 60_000)

        self.check_for_latest_version_timer = QTimer()
        self.check_for_latest_version_timer.timeout.connect(
            self._maybe_check_for_latest_version
        )
        self.check_for_latest_version_timer.start(86_400_000)  # every hour
        self._maybe_check_for_latest_version()

        self.signal_watchdog = SignalWatchdog()

    def _maybe_check_for_latest_version(self):
        """
        If enough time has passed since last check
        + Check for latest version on PYPI and store it in self.state.latest_version_available (as str)
        + Update self.state.last_check_new_version_utc_dt with curent datetime
        + It writes info to logger about it.
        """
        next_check_utc_dt = (
            self.state.last_check_new_version_utc_dt
            + datetime.timedelta(days=self.conf.check_new_version_every_n_days)
        )
        if datetime.datetime.utcnow() > next_check_utc_dt:
            try:
                self.logger.write_new_date_section("Checking for latest release")
                pypi_response = requests.get(const.PYPI_PROJECT_URL)
                pypi_json = pypi_response.json()
                self.state.latest_version_available = pypi_json["info"]["version"]
                if self.state.version_need_upgrade():
                    self.logger.write(
                        f"new release available : {self.state.latest_version_available}"
                    )
                else:
                    self.logger.write("ok")
                self.state.last_check_new_version_utc_dt = datetime.datetime.utcnow()
            except (
                requests.exceptions.ConnectionError,
                json.decoder.JSONDecodeError,
                KeyError,
            ):
                self.logger.error(
                    "Could not retrieve latest release number. "
                    "Considering it's fine."
                )
                self.state.latest_version_available = __version__
            self.qt_app.update_system_tray()

    def quit(self):
        """
        triggered when the app is being closed
        """
        self.state.empty_queue()
        if self.state.current_operation in (
            CurrentOperation.BACKUP_IN_PROGRESS,
            CurrentOperation.FORGET_IN_PROGRESS,
        ):
            self.logger.write(
                "Closing the app. Waiting for restic process to be finished"
            )
            self.restic_backup.terminate()
        QTimer.singleShot(100, self._quit_part2)

    def _quit_part2(self):
        """
        triggered behind self.quit + a short delay
        to let current operations to close cleanly
        """
        if self.state.current_operation in (
            CurrentOperation.BACKUP_IN_PROGRESS,
            CurrentOperation.FORGET_IN_PROGRESS,
        ):
            self.logger.write("Waiting for restic process to be finished")
            QTimer.singleShot(200, self._quit_part2)
        else:
            self.qt_app.quit()
