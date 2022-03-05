"""
Manages the writing to
+ log file
+ stdout
"""

import datetime
from enacrestic import const


class Logger:
    def __init__(self):
        pass

    def __enter__(self):
        self.f_handler = open(const.RESTIC_LOGFILE, "a")
        self.write_new_date_section()
        self.write(f"Started ENACrestic {const.VERSION}\n")
        return self

    def __exit__(self, typ, value, traceback):
        self.write_new_date_section()
        self.write(f"Stopped ENACrestic {const.VERSION}\n")
        self.f_handler.close()

    def write_new_date_section(self):
        message = "-" * 50 + f"\n{datetime.datetime.now()}"
        self.write(message)

    def write(self, message="", end="\n"):
        self.f_handler.write(f"{message}{end}")
        self.f_handler.flush()
        print(message, end=end)

    def error(self, message, end="\n"):
        lines = [f"! {line}" for line in message.split("\n")]
        self.write("\n".join(lines), end)
