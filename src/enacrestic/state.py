import datetime
import json
from enum import Enum

from dynaconf import Dynaconf

from enacrestic import __version__, const
from enacrestic.utils import local_str_to_utc, utc_to_local_str


class Operation(Enum):
    """
    Enumerate all operations that app can run
    """

    BACKUP = "backup"
    FORGET = "forget"


class CurrentOperation(Enum):
    """
    Enumerate all "what is the current operation" possible
    """

    JUST_LAUNCHED = "just_launched"
    BACKUP_IN_PROGRESS = "backup_in_progress"
    FORGET_IN_PROGRESS = "forget_in_progress"
    IDLE = "idle"


class Status(Enum):
    """
    Enumerate all status possible (last command was ok or had an error)
    """

    OK = "ok"
    LAST_OPERATION_FAILED = "last_operation_failed"
    NO_NETWORK = "no_network"


class State:
    """
    Load / Stores the state of the application
    """

    def __init__(self, app):
        self.app = app

    def __enter__(self):
        self._load()
        return self

    def __exit__(self, *args):
        self._save()

    def _load(self):
        conf_read = Dynaconf(
            settings_files=[const.RESTIC_STATEFILE],
        )
        self.current_operation = CurrentOperation.JUST_LAUNCHED
        self.current_status = Status.OK
        self.queue = []
        self.last_check_new_version_utc_dt = local_str_to_utc(
            conf_read.get("last_check_new_version_datetime", "1970-01-01 00:00:00")
        )
        self.latest_version_available = conf_read.get(
            "latest_version_available", __version__
        )
        self.nb_backups_before_forget = conf_read.get(
            "nb_backups_before_forget", self.app.conf.forget_every_n_backups
        )
        self.prev_backup_chronos = []
        for chrono in conf_read.get("prev_backup_chronos", []):
            self.prev_backup_chronos.append((local_str_to_utc(chrono[0]), chrono[1]))
        self.prev_forget_chronos = []
        for chrono in conf_read.get("prev_forget_chronos", []):
            self.prev_forget_chronos.append((local_str_to_utc(chrono[0]), chrono[1]))

    def _save(self):
        prev_backup_chronos = []
        for chrono in self.prev_backup_chronos:
            prev_backup_chronos.append((utc_to_local_str(chrono[0]), chrono[1]))
        prev_forget_chronos = []
        for chrono in self.prev_forget_chronos:
            prev_forget_chronos.append((utc_to_local_str(chrono[0]), chrono[1]))

        with open(const.RESTIC_STATEFILE, "w") as fh:
            json.dump(
                {
                    "current_operation": self.current_operation.value,
                    "current_status": self.current_status.value,
                    "last_check_new_version_datetime": utc_to_local_str(
                        self.last_check_new_version_utc_dt
                    ),
                    "latest_version_available": self.latest_version_available,
                    "nb_backups_before_forget": self.nb_backups_before_forget,
                    "prev_backup_chronos": prev_backup_chronos,
                    "prev_forget_chronos": prev_forget_chronos,
                    "version": __version__,
                },
                fh,
                sort_keys=True,
                indent=2,
            )

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

    def get_icon(self):
        """
        return path to icon matching current state
        """
        if self.current_operation == CurrentOperation.JUST_LAUNCHED:
            return (
                f"{const.ICONS_FOLDER}/just_launched_badge.png"
                if self.version_need_upgrade()
                else f"{const.ICONS_FOLDER}/just_launched.png"
            )
        elif self.current_operation == CurrentOperation.IDLE:
            if self.current_status == Status.OK:
                return (
                    f"{const.ICONS_FOLDER}/backup_success_badge.png"
                    if self.version_need_upgrade()
                    else f"{const.ICONS_FOLDER}/backup_success.png"
                )
            elif self.current_status == Status.LAST_OPERATION_FAILED:
                return (
                    f"{const.ICONS_FOLDER}/backup_failed_badge.png"
                    if self.version_need_upgrade()
                    else f"{const.ICONS_FOLDER}/backup_failed.png"
                )
            elif self.current_status == Status.NO_NETWORK:
                return (
                    f"{const.ICONS_FOLDER}/backup_no_network_badge.png"
                    if self.version_need_upgrade()
                    else f"{const.ICONS_FOLDER}/backup_no_network.png"
                )
            else:
                self.app.logger.error(
                    f"unexpected state: {self.current_operation=} {self.current_status=}"
                )
                return (
                    f"{const.ICONS_FOLDER}/just_launched_badge.png"
                    if self.version_need_upgrade()
                    else f"{const.ICONS_FOLDER}/just_launched.png"
                )
        elif self.current_operation == CurrentOperation.BACKUP_IN_PROGRESS:
            return f"{const.ICONS_FOLDER}/backup_in_progress.png"
        elif self.current_operation == CurrentOperation.FORGET_IN_PROGRESS:
            return f"{const.ICONS_FOLDER}/forget_in_progress.png"
        else:
            self.app.logger.error(
                f"unexpected state: {self.current_operation=} {self.current_status=}"
            )
            return (
                f"{const.ICONS_FOLDER}/just_launched_badge.png"
                if self.version_need_upgrade()
                else f"{const.ICONS_FOLDER}/just_launched.png"
            )

    def want_to_backup(self):
        """
        + Answer if a backup/forget can be run now
        + Set self.queue if possible
        """
        if self.current_operation in (
            CurrentOperation.IDLE,
            CurrentOperation.JUST_LAUNCHED,
        ):
            self.queue = [Operation.BACKUP]
            return True
        else:
            return False

    def next_operation(self):
        """
        + return next Operation from self.queue
        + set self.current_operation accordingly
        + return None if nothing in the queue
        """
        if len(self.queue) > 0:
            operation = self.queue.pop(0)
            if operation == Operation.BACKUP:
                self.current_operation = CurrentOperation.BACKUP_IN_PROGRESS
            elif operation == Operation.FORGET:
                self.current_operation = CurrentOperation.FORGET_IN_PROGRESS
            else:
                self.app.logger.error(
                    f"unexpected Operation: {operation.value=} -> skipping"
                )
                return self.next_operation()

            return operation
        else:
            self.current_operation = CurrentOperation.IDLE
            return None

    def finished_restic_cmd(self, completion_status, start_utc_dt, chrono):
        """
        + when success:
          + save chrono for current operation (backup or forget)
          + queue a forget if needed
        + otherwise:
          + empty queue
          + set self.last_failed_utc_dt
        """

        # Save Chrono if success
        if completion_status == Status.OK:
            chrono_seconds = round(chrono.total_seconds(), 2)  # Keep only 2 digits
            if self.current_operation == CurrentOperation.BACKUP_IN_PROGRESS:
                self.nb_backups_before_forget -= 1
                if self.nb_backups_before_forget <= 0:
                    self.nb_backups_before_forget = self.app.conf.forget_every_n_backups
                    self.queue.append(Operation.FORGET)
                self.prev_backup_chronos.insert(0, (start_utc_dt, chrono_seconds))
                if len(self.prev_backup_chronos) > const.NB_CHRONOS_TO_SAVE:
                    self.prev_backup_chronos.pop()
            elif self.current_operation == CurrentOperation.FORGET_IN_PROGRESS:
                self.prev_forget_chronos.insert(0, (start_utc_dt, chrono_seconds))
                if len(self.prev_forget_chronos) > const.NB_CHRONOS_TO_SAVE:
                    self.prev_forget_chronos.pop()
        else:
            # Don't do more things yet if NO_NETWORK or LAST_OPERATION_FAILED
            self.last_failed_utc_dt = datetime.datetime.utcnow()
            self.queue = []
        self.current_status = completion_status
