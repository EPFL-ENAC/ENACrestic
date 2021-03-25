# ENACrestic

![ENACrestic](doc_pixmaps/enacrestic.png)

A simple Qt GUI to automate backups with [restic](https://restic.net/)

1. Automate your *restic* backups at a choosen frequency
2. Run *restic forget* in a regular basis to keep your backup light and useful
3. Let you see when :
  + ![backup_in_progress](doc_pixmaps/backup_in_progress.png) `restic backup` is running
  + ![forget_in_progress](doc_pixmaps/forget_in_progress.png) `restic forget` is running
  + ![backup_success](doc_pixmaps/backup_success.png) backup is completed
  + ![backup_failed](doc_pixmaps/backup_failed.png) last backup failed
  + ![backup_no_network](doc_pixmaps/backup_no_network.png) last backup failed because of a network timeout (maybe the VPN is not running?)
