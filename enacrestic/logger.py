"""
Manages the writing to
+ log file
+ stdout

with auto log rotation (gz)
"""


import datetime
import gzip
import logging
import os
from logging.handlers import TimedRotatingFileHandler

from enacrestic import __version__, const


class Logger:
    class GZipRotator:
        def __call__(self, source, dest):
            os.rename(source, dest)
            with open(dest, "rb") as f_in:
                with gzip.open(f"{dest}.gz", "wb") as f_out:
                    f_out.writelines(f_in)
            os.remove(dest)

    def __init__(self, gui_enabled):
        self.logger = logging.getLogger()
        rotating_file_handler = TimedRotatingFileHandler(
            filename=const.RESTIC_LOGFILE,
            when="D",
            interval=const.LOGFILE_ROTATION_EVERY_N_DAYS,
            backupCount=const.LOGFILE_ROTATION_BACKUP_COUNT,
        )
        formatter = logging.Formatter("%(message)s")
        rotating_file_handler.setFormatter(formatter)
        rotating_file_handler.rotator = Logger.GZipRotator()
        self.logger.addHandler(rotating_file_handler)
        self.logger.setLevel(logging.INFO)
        if gui_enabled:
            self.app_flavor = ""
        else:
            self.app_flavor = "(noGUI) "

    def __enter__(self):
        self.write_new_date_section(
            f"Started ENACrestic {self.app_flavor}{__version__}\n"
        )
        return self

    def __exit__(self, typ, value, traceback):
        self.write_new_date_section(f"Stopped ENACrestic {__version__}\n")

    def write_new_date_section(self, message=None):
        section_header = "-" * 50 + f"\n{datetime.datetime.now()}"
        self.write(section_header)
        if message is not None:
            self.write(message)

    def write(self, message=""):
        self.logger.info(message)
        print(message)

    def error(self, message):
        lines = [f"! {line}" for line in message.split("\n")]
        self.logger.error("\n".join(lines))
        print("\n".join(lines))
