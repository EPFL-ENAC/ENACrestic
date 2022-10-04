"""
Manages the execution of restic command
"""
import os
import re
import time

from PyQt5.QtCore import QProcess, QProcessEnvironment

from enacrestic import const


class ResticBackup:
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
        if self.p.exitStatus() == QProcess.NormalExit:
            if exitCode == 0:
                completion_status = "ok"
            else:
                if self.current_error == "timeout":
                    completion_status = "no network"
                else:
                    completion_status = "failed"
        else:
            completion_status = "failed"
        next_action = self.state.finished_restic_cmd(
            completion_status, self.current_chrono
        )
        self.logger.write(
            f"Process finished ({exitCode}) in "
            f"{self.current_chrono:.3f} seconds with status: '{completion_status}'\n"
        )

        self.p = None
        if next_action == "run forget":
            self._run_forget()
