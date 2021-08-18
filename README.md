# ENACrestic

![ENACrestic](doc_pixmaps/enacrestic.png)

A simple Qt GUI to automate backups with [restic](https://restic.net/)

1. Automate your *restic* backups at a choosen frequency
2. Run *restic forget* in a regular basis (and transparently) to keep your backup light and useful
3. Let you see when :
  + ![backup_in_progress](doc_pixmaps/backup_in_progress.png) `restic backup` is running
  + ![forget_in_progress](doc_pixmaps/forget_in_progress.png) `restic forget` is running
  + ![backup_success](doc_pixmaps/backup_success.png) backup is completed
  + ![backup_failed](doc_pixmaps/backup_failed.png) last backup failed
  + ![backup_no_network](doc_pixmaps/backup_no_network.png) last backup failed because of a network timeout (maybe the VPN is not running?)


# Installation

This has been tested and validated on

+ *Ubuntu 18.04 LTS*
+ *Ubuntu 20.04 LTS*

```bash
sudo apt install restic python3-pip qt5dxcb-plugin
pip3 install --user --upgrade pip
pip3 install --user ENACrestic
```


# Upgrade

To upgrade ENACrestic to latest release, just run the following command :

```bash
pip3 install --user --upgrade ENACrestic
```


# Config ENACrestic

```bash
mkdir ~/.enacrestic
```

### Edit `~/.enacrestic/env.sh` file

Choose the right section according to your destination storage

```snip
# Local (not recommended!)
export RESTIC_REPOSITORY=/path/to/my/restic-repo

# SSH / SFTP
export RESTIC_REPOSITORY=sftp:my-server.epfl.ch:/home/username/path

# S3 Bucket
export RESTIC_REPOSITORY=s3:s3.epfl.ch/bucket_name/restic_MyComputerName
export AWS_ACCESS_KEY_ID=TheBucketRWAccessKey
export AWS_SECRET_ACCESS_KEY=TheBucketRWSecretKey
```

### Edit `~/.enacrestic/.pw` file

Add a one line password in it. This is used to encrypt your backups.

**Be careful !** If you loose this password ... you loose your backups.

### Edit `~/.enacrestic/bkp_include` file

Add one line per folder / file that has to be backed up.

**Example 1** - list every important folder :

```snip
/home/username/.enacrestic/
/home/username/Documents/
/home/username/Teaching/
/home/username/Pictures/
/home/username/Projects/
/home/username/Learn/
/home/username/.gitconfig
/home/username/.mozilla/
/home/username/.ssh/
# heavy !
/home/username/Videos/
```

**Example 2** - backup all my home directory (and probably exclude some things just after) :

```snip
/home/username/
```

note : Lines starting with a `#` are ignored.

### Edit `~/.enacrestic/bkp_exclude` file (optional)

Add one line per folder / file / expression that has to be excluded.

Before running your first backup, you might want to exclude heavy and unnecessary folders (Like the Downloads or the Trash). You can use the `baobab` utility to find those.

Here is an example of some typical things you might want to exclude from backup :

```snip
*.iso
/home/username/Downloads/
/home/username/.local/share/Trash/
/home/username/VirtualBox VMs/
/home/username/snap/
/home/username/.cache/
/home/username/**/nobackup*
/home/username/.local/share/virtualenvs/
/home/username/.arduino15/
/home/username/.atom/
/home/username/.npm/
/home/username/.nvm/
```

Exact syntax is described [here](https://restic.readthedocs.io/en/latest/040_backup.html#excluding-files)

### Edit `~/.bashrc` or `~/.zshrc` (depending on your shell)

Add the following 2 lines to have :
+ enacrestic in your `$PATH`
+ enacrestic's env variables available.

```snip
export PATH=$PATH:/home/username/.local/bin
. ~/.enacrestic/env.sh
 ```


# Init restic repo by hand

```bash
restic init --password-file  ~/.enacrestic/.pw
```

You're now ready to send your 1st backup.

**This may take much time!** Please consider having enough time for the 1st backup to complete. It'll be the longest backup ever, since everything has to be copied. All future backups will then be only incremental.


# Run `ENACrestic`

+ from Ubuntu's Application launcher
+ or from command line with the single command `enacrestic`

You'll see a new icon in the system tray (upper-right corner of your screen) with following icon.

![just_launched](doc_pixmaps/just_launched.png)

This is the indicator that ENACrestic is running in the background and it'll change over time, reflecting current state.

By clicking on it, you can view detailed status and opt-in for the auto-start feature (start *ENACrestic* when Ubuntu user session is started).

From now on, ENACrestic is running in the background and doing the backups on a regular basis.

You can check it's activity by reading the `~/.enacrestic/last_backups.log` file.


# What ENACrestic doesn't do

ENACrestic is here to help you, running backups on a regular basis. If you want to browse backups, restore files/folders, you'll have to use *restic* itself. Here are basic commands :

### List the snapshots (backups)

```bash
restic snapshots -c --password-file  ~/.enacrestic/.pw
```

### Mount the backups ...

... and be able to
+ browse the different snapshots
+ restore any file / folder

```bash
mkdir -p ~/mnt/my_backups
restic mount ~/mnt/my_backups --password-file  ~/.enacrestic/.pw
```

Now you can browse `~/mnt/my_backups` folder and copy from it anything you want to restore. When done, you can simply *Ctrl-c* in the terminal where you had issued the `restic mount ...` command.
