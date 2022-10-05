import datetime
import json
import os

import requests
from PyQt5.QtGui import QIcon

from enacrestic import __version__, const

"""
Stores the state of the application
Manages the transitions
Updates the icon to match the state
"""


class State:
    DEF_START_STATE = "program_just_launched"
    DEF_NB_BACKUPS_BEFORE_FORGET = const.DEF_FORGET_EVERY_N_ITERATIONS
    NB_CHRONOS_TO_SAVE = 10
    DEF_AUTOSTART = False
    DEF_LAST_CHECK_NEW_VERSION_DATETIME = datetime.datetime(
        year=1970, month=1, day=1, hour=0, minute=0, second=0
    )

    def __init__(self, logger):
        self.logger = logger
        self.tray_icon = None  # filled by connect_to_gui
        self.info_action = None  # filled by connect_to_gui
        self.autostart_action = None  # filled by connect_to_gui
        self.last_failed_datetime = None

    def connect_to_gui(self, tray_icon, info_action, upgrade_action, autostart_action):
        self.tray_icon = tray_icon
        self.info_action = info_action
        self.upgrade_action = upgrade_action
        self.autostart_action = autostart_action
        self.autostart_action.triggered.connect(self._toggle_autostart)
        self.autostart_action.setChecked(self.autostart)
        self._update_icon()

    def __enter__(self):
        try:
            with open(const.RESTIC_STATEFILE) as fh:
                state_from_file = json.load(fh)
                self.current_state = state_from_file.get(
                    "current_state", State.DEF_START_STATE
                )
                if self.current_state != "backup_in_pause":
                    self.current_state = State.DEF_START_STATE
                self.nb_backups_before_forget = state_from_file.get(
                    "nb_backups_before_forget", State.DEF_NB_BACKUPS_BEFORE_FORGET
                )
                self.prev_backup_chronos = state_from_file.get(
                    "prev_backup_chronos", []
                )
                self.prev_forget_chronos = state_from_file.get(
                    "prev_forget_chronos", []
                )
                self.autostart = state_from_file.get("autostart", State.DEF_AUTOSTART)
                self.backup_every_n_minutes = state_from_file.get(
                    "backup_every_n_minutes", const.DEF_BACKUP_EVERY_N_MINUTES
                )
                self.forget_every_n_iterations = state_from_file.get(
                    "forget_every_n_iterations", const.DEF_FORGET_EVERY_N_ITERATIONS
                )
                self.check_new_version_every_n_days = state_from_file.get(
                    "check_new_version_every_n_days",
                    const.CHECK_NEW_VERSION_EVERY_N_DAYS,
                )
                try:
                    self.last_check_new_version_datetime = datetime.datetime.strptime(
                        state_from_file.get("last_check_new_version_datetime", ""),
                        "%Y-%m-%d %H:%M:%S",
                    )
                except ValueError:
                    self.last_check_new_version_datetime = (
                        State.DEF_LAST_CHECK_NEW_VERSION_DATETIME
                    )
                self.latest_version_available = state_from_file.get(
                    "latest_version_available", __version__
                )
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            self.current_state = State.DEF_START_STATE
            self.nb_backups_before_forget = State.DEF_NB_BACKUPS_BEFORE_FORGET
            self.prev_backup_chronos = []
            self.prev_forget_chronos = []
            self.autostart = State.DEF_AUTOSTART
            self.backup_every_n_minutes = const.DEF_BACKUP_EVERY_N_MINUTES
            self.forget_every_n_iterations = const.DEF_FORGET_EVERY_N_ITERATIONS
            self.check_new_version_every_n_days = const.CHECK_NEW_VERSION_EVERY_N_DAYS
            self.last_check_new_version_datetime = (
                State.DEF_LAST_CHECK_NEW_VERSION_DATETIME
            )
            self.latest_version_available = __version__

        self.maybe_check_for_latest_version()

        self._update_icon()
        return self

    def __exit__(self, typ, value, traceback):
        if "in_progress" in self.current_state:
            self.current_state = "backup_failed"
            self.last_failed_datetime = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        with open(const.RESTIC_STATEFILE, "w") as fh:
            json.dump(
                {
                    "current_state": self.current_state,
                    "nb_backups_before_forget": self.nb_backups_before_forget,
                    "prev_backup_chronos": self.prev_backup_chronos,
                    "prev_forget_chronos": self.prev_forget_chronos,
                    "autostart": self.autostart,
                    "backup_every_n_minutes": self.backup_every_n_minutes,
                    "forget_every_n_iterations": self.forget_every_n_iterations,
                    "check_new_version_every_n_days": self.check_new_version_every_n_days,
                    "last_check_new_version_datetime": self.last_check_new_version_datetime.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                    "latest_version_available": self.latest_version_available,
                },
                fh,
                sort_keys=True,
                indent=4,
            )

    def want_to_backup(self):
        """
        Answer if it is possible to run a backup
        it modifies the state (and icon if True)
        """
        if self.current_state == "program_just_launched":
            self.current_state = "backup_in_progress"

        elif self.current_state == "backup_in_pause":
            return False

        elif self.current_state == "backup_success":
            self.current_state = "backup_in_progress"

        elif self.current_state == "backup_failed":
            self.current_state = "backup_in_progress_failed"

        elif self.current_state == "backup_no_network":
            self.current_state = "backup_in_progress_no_network"

        elif self.current_state == "backup_in_progress":
            return False

        elif self.current_state == "backup_in_progress_failed":
            return False

        elif self.current_state == "backup_in_progress_no_network":
            return False

        elif self.current_state == "forget_in_progress":
            return False

        self._save_chrono_start_datetime()
        self._update_icon()
        return True

    def finished_restic_cmd(self, completion_status, chrono):
        """
        Modify state because backup/forget command finished
        returns :
        + 'run forget' if it is the right condition to do so
        + 'ok' otherwise
        """
        if completion_status == "ok":
            if self.current_state == "forget_in_progress":
                self.current_state = "backup_success"
                self._save_new_chrono("forget", chrono)
            else:  # that was a backup in progress
                self.nb_backups_before_forget -= 1
                if self.nb_backups_before_forget == 0:
                    self.nb_backups_before_forget = self.forget_every_n_iterations
                    self.current_state = "forget_in_progress"
                else:
                    self.current_state = "backup_success"
                self._save_new_chrono("backup", chrono)
        elif completion_status == "no network":
            self.current_state = "backup_no_network"
            self.last_failed_datetime = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        else:
            self.current_state = "backup_failed"
            self.last_failed_datetime = datetime.datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        if self.current_state == "forget_in_progress":
            self._save_chrono_start_datetime()
            self._update_icon()
            return "run forget"
        else:
            self._update_icon()
            return "ok"

    def _save_chrono_start_datetime(self):
        """Store datetime just before a new backup/forget operation starts"""
        self.start_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _save_new_chrono(self, action, chrono):
        """Store new chrono to previous backup/forget chronos"""
        chrono = round(chrono, 2)  # Keep only 2 digits
        if action == "backup":
            self.prev_backup_chronos.insert(0, (self.start_datetime, chrono))
            if len(self.prev_backup_chronos) > State.NB_CHRONOS_TO_SAVE:
                self.prev_backup_chronos.pop()
        else:
            self.prev_forget_chronos.insert(0, (self.start_datetime, chrono))
            if len(self.prev_forget_chronos) > State.NB_CHRONOS_TO_SAVE:
                self.prev_forget_chronos.pop()

    def _update_icon(self):
        """
        + Update icon to current state
        + Update info_action with current state infos
        + Show upgrade_action if needed
        """

        def _str_date(str_date):
            """return nice date (with only h:m:s if it's in the last 24h)"""
            date = datetime.datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S")
            if datetime.datetime.now() - date < datetime.timedelta(days=1):
                return "at %s" % date.strftime("%H:%M:%S")
            else:
                return "on %s" % date.strftime("%Y-%m-%d %H:%M:%S")

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
            """returns msg with latest chrono and average over the last n"""
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

        self.tray_icon.setIcon(
            QIcon(const.ICONS[self.current_state][self.version_need_upgrade()])
        )

        state_msg = f"ENACrestic {__version__}\n\n"

        if self.current_state == "program_just_launched":
            state_msg += (
                f"Just launched,\n"
                f"a backup will be done every "
                f"{_str_duration(self.backup_every_n_minutes * 60, True)}."
            )
        elif self.current_state == "backup_in_pause":
            state_msg += "Paused"
        elif self.current_state == "backup_success":
            state_msg += "Last backup was successful"
        elif self.current_state == "backup_failed":
            state_msg += (
                f"Last backup failed, {_str_date(self.last_failed_datetime)}\n"
                f"see {const.RESTIC_LOGFILE} for details."
            )
        elif self.current_state == "backup_no_network":
            state_msg += f"Network timeout {_str_date(self.last_failed_datetime)}"
        if self.current_state.startswith("backup_in_progress"):
            state_msg += (
                f"Currently running a backup (started {_str_date(self.start_datetime)})"
            )
        elif self.current_state == "forget_in_progress":
            state_msg += (
                f"Currently doing a cleanup (started {_str_date(self.start_datetime)})"
            )

        # Add conditionnal stats on last backups and last cleanup
        last_chronos = _str_last_chronos("backup", self.prev_backup_chronos)
        last_chronos += _str_last_chronos("cleanup", self.prev_forget_chronos)
        if last_chronos != "":
            state_msg += "\n"
            state_msg += last_chronos
        self.info_action.setText(state_msg)

        # show / hide upgrade_action
        self.upgrade_action.setVisible(self.version_need_upgrade())

    def _toggle_autostart(self):
        """Save and apply user's choice to autostart or not"""

        if self.autostart_action is None:
            return

        self.autostart = self.autostart_action.isChecked()
        if self.autostart:
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

    def maybe_check_for_latest_version(self):
        """
        This will call check_for_latest_version if enough time has passed since last check
        """
        next_check_datetime = self.last_check_new_version_datetime + datetime.timedelta(
            days=self.check_new_version_every_n_days
        )
        if datetime.datetime.now() > next_check_datetime:
            self.check_for_latest_version()
            self._update_icon()

    def check_for_latest_version(self):
        """
        + Check for latest version on PYPI and store it in self.latest_version_available (as str)
        + Update self.last_check_new_version_datetime with curent datetime
        + It writes info to logger about it.
        """
        try:
            self.logger.write_new_date_section()
            self.logger.write("Checking for latest release")
            pypi_response = requests.get(const.PYPI_PROJECT_URL)
            pypi_json = pypi_response.json()
            self.latest_version_available = pypi_json["info"]["version"]
            if self.version_need_upgrade():
                self.logger.write(
                    f"new release available : {self.latest_version_available}"
                )
            else:
                self.logger.write("ok")
            self.last_check_new_version_datetime = datetime.datetime.now()
        except (
            requests.exceptions.ConnectionError,
            json.decoder.JSONDecodeError,
            KeyError,
        ):
            self.logger.error(
                "Could not retrieve latest release number. " "Considering it's fine."
            )
            self.latest_version_available = __version__

    def version_need_upgrade(self):
        """
        return bool if new version > current version
        """

        def try_to_int(string):
            try:
                return int(string)
            except ValueError:
                return string

        latest_version_info = tuple(
            try_to_int(ver) for ver in self.latest_version_available.split(".")
        )
        return latest_version_info > const.VERSION_INFO