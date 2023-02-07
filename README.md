# ENACrestic

[![License: MIT](https://img.shields.io/badge/license-GPLv3-blue&style=flat)](https://opensource.org/licenses/MIT)
[![release to PyPI](https://github.com/EPFL-ENAC/ENACrestic/actions/workflows/release-please-pypi.yml/badge.svg)](https://github.com/EPFL-ENAC/ENACrestic/actions/workflows/release-please-pypi.yml/badge.svg)
[![Python](https://img.shields.io/pypi/pyversions/enacrestic?style=flat&logo=Python)](https://pypi.org/project/enacrestic)
[![Version](https://img.shields.io/pypi/v/enacrestic?style=flat&logo=PyPI&color=%2334D058)](https://pypi.org/project/enacrestic)

[![Last commit](https://img.shields.io/github/last-commit/EPFL-ENAC/ENACrestic.svg?style=flat&logo=github)](https://github.com/EPFL-ENAC/ENACrestic/commits)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/EPFL-ENAC/ENACrestic?style=flat&logo=github)](https://github.com/EPFL-ENAC/ENACrestic/commits)
[![Github Stars](https://img.shields.io/github/stars/EPFL-ENAC/ENACrestic?style=flat&logo=github)](https://github.com/EPFL-ENAC/ENACrestic/stargazers)
[![Github Forks](https://img.shields.io/github/forks/EPFL-ENAC/ENACrestic?style=flat&logo=github)](https://github.com/EPFL-ENAC/ENACrestic/network/members)
[![Github Watchers](https://img.shields.io/github/watchers/EPFL-ENAC/ENACrestic?style=flat&logo=github)](https://github.com/EPFL-ENAC/ENACrestic)
[![GitHub contributors](https://img.shields.io/github/contributors/EPFL-ENAC/ENACrestic?style=flat&logo=github)](https://github.com/EPFL-ENAC/ENACrestic/graphs/contributors)

![ENACrestic](doc_pixmaps/enacrestic.png)

A simple Qt GUI to automate backups with [restic](https://restic.net/)

1. Automate your _restic_ backups at a choosen frequency
2. Run _restic forget_ in a regular basis (and transparently) to keep your backup light and useful
3. Let you see when :

- ![pre_backup_in_progress](doc_pixmaps/pre_backup_in_progress.png) `pre_backup` script is running
- ![backup_in_progress](doc_pixmaps/backup_in_progress.png) `restic backup` is running
- ![forget_in_progress](doc_pixmaps/forget_in_progress.png) `restic forget` is running
- ![unlock_in_progress](doc_pixmaps/unlock_in_progress.png) `restic unlock` is running
- ![backup_success](doc_pixmaps/backup_success.png) backup is completed
- ![error](doc_pixmaps/error.png) last operation failed
- ![no_network](doc_pixmaps/no_network.png) last backup failed because of a network timeout (maybe the VPN is not running?)

# Installation

This has been tested and validated on

- _Ubuntu 18.04 LTS_
- _Ubuntu 20.04 LTS_
- _Ubuntu 22.04 LTS_

```bash
sudo apt install restic python3-pip qt5dxcb-plugin
pip3 install --user --upgrade pip
pip3 install --user enacrestic
```

# Upgrade

To upgrade ENACrestic to latest release, just run the following command :

```bash
pip3 install --user --upgrade enacrestic
```

# Config ENACrestic

Note: For this documentation, we have chosen to use the `vi` text editor.
Adapt the commands below by replacing it with the editor of your choice. (`nano`, `gedit`, ...)

```bash
mkdir ~/.enacrestic
```

### Write environment setup file

Choose the right section according to your destination storage

```bash
vi ~/.enacrestic/env.sh
```

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

Note, although Restic is able to manage several computers being backed up on a common respository, it's not recommended with ENACrestic. Keep a dedicated `RESTIC_REPOSITORY` per machine.

### Write password file

Add a one line password in it. This is used to encrypt your backups.

```bash
vi ~/.enacrestic/.pw
```

**Be careful !** If you loose this password ... you loose your backups.

### Write include list file

Add one line per folder / file that has to be backed up.

```bash
vi ~/.enacrestic/bkp_include
```

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

### Write exclude list file (optional)

Add one line per folder / file / expression that has to be excluded.

Before running your first backup, you might want to exclude heavy and unnecessary folders (Like the Downloads or the Trash). You can use the `baobab` utility to find those.

Here is an example of some typical things you might want to exclude from backup :

```bash
vi ~/.enacrestic/bkp_exclude
```

```snip
*.iso
*.sav
*.bak
*.bak2
*.log
*.ost
*.part
*.temp
*.tmp
*.vhd
*.vhdx
*.vmdk
*.vdi
/home/username/Downloads/
/home/username/ENACdrives/
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

### Make it available to your shell

Add the following 2 lines to have :

- enacrestic in your `$PATH`
- enacrestic's env variables available.

```bash
vi ~/.bashrc # or ~/.zshrc or whatever is your shell rc file
```

```snip
export PATH=$PATH:/home/username/.local/bin
. ~/.enacrestic/env.sh
```

Now close + open a new terminal to get it all into your environment ... or simply reload your rc file :

```bash
. ~/.bashrc # or ~/.zshrc or whatever is your shell rc file
```

# Init restic repo by hand

```bash
restic init --password-file  ~/.enacrestic/.pw
```

🎉 Setup is now complete! You're now ready to send your 1st backup. 🎉

# Run `enacrestic`

- from Ubuntu's Application launcher
- or from command line with the single command `enacrestic`

You'll see a new icon in the system tray (upper-right corner of your screen) with following icon.

![just_launched](doc_pixmaps/just_launched.png)

This is the indicator that ENACrestic is running in the background and it'll change over time, reflecting current state.

By clicking on it, you can view detailed status and opt-in for the auto-start feature (start _ENACrestic_ when Ubuntu user session is started).

From now on, ENACrestic is running in the background and doing the backups on a regular basis.

You can check it's activity by reading the `~/.enacrestic/last_backups.log` file.

Note : **First backup can take a long time!** Please consider having enough time for the 1st backup to complete. It'll be the longest backup ever, since everything has to be copied. All future backups will then be only incremental.

# Note on old backups retention policy

By default, every 10 backups, a `restic forget` will clean repository from backups that don't need to be kept, according the following retention policy:

- keep the last `3` backups
- keep the last `24` hourly backups
- keep the last `7` daily backups
- keep the last `4` weekly backups
- keep the last `12` monthly backups
- keep the last `5` yearly backups

# What ENACrestic doesn't do

ENACrestic is here to help you, running backups on a regular basis. If you want to browse backups, restore files/folders, you'll have to use _restic_ itself. Here are basic commands :

### List the snapshots (backups)

```bash
restic snapshots -c --password-file  ~/.enacrestic/.pw
```

### Mount the backups ...

... and be able to

- browse the different snapshots
- restore any file / folder

```bash
mkdir -p ~/mnt/my_backups
restic mount ~/mnt/my_backups --password-file  ~/.enacrestic/.pw
```

Now you can browse `~/mnt/my_backups` folder and copy from it anything you want to restore. When done, you can simply _Ctrl-c_ in the terminal where you had issued the `restic mount ...` command.
