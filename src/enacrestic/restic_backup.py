"""
Manages the execution of restic command
"""
import datetime
import os
import re
import signal
from enum import Enum

from PyQt5.QtCore import QProcess, QProcessEnvironment

from enacrestic import const
from enacrestic.state import CurrentOperation, Operation, Status


class ResticCompletionStatus(Enum):
    """
    Enumerate all possible restic completion status
    """

    NO_ERROR = ""
    TIMEOUT = "timeout"
    REPO_LOCKED = "repo locked"


class ResticBackup:
    def __init__(self, app):
        self.app = app
        self._load_env_variables()
        self.current_utc_dt_starting = None
        self.p = None
        self.need_to_unlock = False

    def run(self):
        if not self.app.state.want_to_backup():
            self.app.logger.write_new_date_section(
                f"Backup not launched. "
                f"Current state is {self.app.state.current_operation.value}"
            )
            return

        # Run queued commands, one by one
        self._run_next_operation()

    def terminate(self):
        """
        Terminate currently running process, if any
        with SIGINT, equivalent to sending ctrl-c.
        This is the clean way to interrupt restic
        """
        if self.p is not None:
            os.kill(self.p.processId(), signal.SIGINT)

    def _run_next_operation(self):
        self.need_to_unlock = False
        next_operation = self.app.state.next_operation()
        self.app.qt_app.update_system_tray()
        if next_operation is None:
            return
        elif next_operation == Operation.PRE_BACKUP:
            self._run_prebackup()
        elif next_operation == Operation.BACKUP:
            self._run_backup()
        elif next_operation == Operation.FORGET:
            self._run_forget()
        elif next_operation == Operation.UNLOCK:
            self._run_unlock()

    def _load_env_variables(self):
        """
        Load expected env vars from ~/.enacrestic/env.sh
        to be used by restic commands
        """
        self.env = QProcessEnvironment.systemEnvironment()

        # Be sure to get output messages in english
        self.env.insert("LC_ALL", "C")

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
            self.app.logger.error(
                f"{const.RESTIC_USER_PREFS['ENV']} seems not configured correctly"
            )

    def _run_prebackup(self):
        self.app.logger.write_new_date_section("Running restic pre_backup!")
        cmd = const.PRE_BACKUP_HOOK
        args = []
        self._run(cmd, args)

    def _run_backup(self):
        self.app.logger.write_new_date_section("Running restic backup!")
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
        self.app.logger.write_new_date_section("Running restic forget!")
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

    def _run_unlock(self):
        self.app.logger.write_new_date_section("Running restic unlock!")
        cmd = "restic"
        args = [
            "unlock",
            "--password-file",
            const.RESTIC_USER_PREFS["PASSWORDFILE"],
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
        self.current_process_completion_status = ResticCompletionStatus.NO_ERROR

    def _handle_stdout(self):
        data = self.p.readAllStandardOutput()
        stdout = bytes(data).decode("utf8")
        self.app.logger.write(stdout)

    def _handle_stderr(self):
        data = self.p.readAllStandardError()
        stderr = bytes(data).decode("utf8")
        self.app.logger.error(stderr)
        if self.app.state.current_operation in (
            CurrentOperation.BACKUP_IN_PROGRESS,
            CurrentOperation.FORGET_IN_PROGRESS,
            CurrentOperation.UNLOCK_IN_PROGRESS,
        ):
            if re.search(r"timeout", stderr):
                self.current_process_completion_status = ResticCompletionStatus.TIMEOUT
            if re.search(
                r"the `unlock` command can be used to remove stale locks", stderr
            ):
                self.current_process_completion_status = (
                    ResticCompletionStatus.REPO_LOCKED
                )
                lock_ago_str = re.search(
                    r"lock was created at.* \((.*)\)", stderr
                ).group(1)
                lock_hours_bool = re.search(r"\dh\d", lock_ago_str) is not None
                try:
                    lock_minutes_int = int(re.search(r"(\d+)m", lock_ago_str).group(1))
                except AttributeError:
                    lock_minutes_int = 0
                self.need_to_unlock = lock_hours_bool or lock_minutes_int > 30
                if not self.need_to_unlock:
                    self.app.logger.write(
                        "The lock is too new. We expect 30+ minutes to unlock manually."
                    )

    def _handle_state(self, proc_state):
        if proc_state == QProcess.Starting:
            self.current_utc_dt_starting = datetime.datetime.utcnow()
            self.app.qt_app.update_system_tray()
        elif proc_state == QProcess.NotRunning:
            self.current_chrono = (
                datetime.datetime.utcnow() - self.current_utc_dt_starting
            )

    def _process_finished(self):
        exitCode = self.p.exitCode()
        if self.p.exitStatus() == QProcess.NormalExit:
            if exitCode == 0:
                completion_status = Status.OK
            else:
                if (
                    self.current_process_completion_status
                    == ResticCompletionStatus.TIMEOUT
                ):
                    completion_status = Status.NO_NETWORK
                elif (
                    self.current_process_completion_status
                    == ResticCompletionStatus.REPO_LOCKED
                ):
                    completion_status = Status.REPO_LOCKED
                else:
                    completion_status = Status.LAST_OPERATION_FAILED
        else:
            completion_status = Status.LAST_OPERATION_FAILED
        self.app.state.finished_restic_cmd(
            completion_status,
            self.current_utc_dt_starting,
            self.current_chrono,
            self.need_to_unlock,
        )
        self.app.logger.write(
            f"Process finished ({exitCode}) in "
            f"{self.current_chrono.total_seconds():.2f} seconds "
            f"with status: '{completion_status.value}'\n\n"
        )

        self.current_utc_dt_starting = None
        self.p = None
        self._run_next_operation()
