import json

from dynaconf import Dynaconf

from enacrestic import __version__, const


class Conf:
    """
    Load / Stores the config of the application
    """

    def __init__(self):
        pass

    def __enter__(self):
        self._load()
        return self

    def __exit__(self, *args):
        self._save()

    def _load(self):
        conf_read = Dynaconf(
            settings_files=[const.RESTIC_CONFFILE],
        )
        self.backup_every_n_minutes = conf_read.get(
            "backup_every_n_minutes", const.DEF_BACKUP_EVERY_N_MINUTES
        )
        self.forget_every_n_backups = conf_read.get(
            "forget_every_n_backups", const.DEF_FORGET_EVERY_N_BACKUPS
        )
        self.check_new_version_every_n_days = conf_read.get(
            "check_new_version_every_n_days", const.DEF_CHECK_NEW_VERSION_EVERY_N_DAYS
        )
        self.gui_autostart = conf_read.get("gui_autostart", const.DEF_GUI_AUTOSTART)

    def _save(self):
        """
        Save conf do file
        """
        with open(const.RESTIC_CONFFILE, "w") as fh:
            json.dump(
                {
                    "backup_every_n_minutes": self.backup_every_n_minutes,
                    "forget_every_n_backups": self.forget_every_n_backups,
                    "check_new_version_every_n_days": self.check_new_version_every_n_days,
                    "gui_autostart": self.gui_autostart,
                    "version": __version__,
                },
                fh,
                sort_keys=True,
                indent=2,
            )

    def set(self, **kwargs):
        """
        + Store new conf value
        + Save it to conf file
        """
        for key in (
            "backup_every_n_minutes",
            "forget_every_n_backups",
            "check_new_version_every_n_days",
            "gui_autostart",
        ):
            if kwargs.get(key) is not None:
                setattr(self, key, kwargs[key])
        self._save()
