# Special cases to manage :

## repo is not initialized (TODO)

## repo is locked (TODO)

### we see :

```out
Mo 08 Feb 2021 20:20:01 CET
--> Running BACKUP
Fatal: unable to create lock in backend: repository is already locked exclusively by PID 42079 on dell-2020 by sbancal (UID 1000, GID 1000)
lock was created at 2021-02-05 16:40:11 (75h39m50.869903846s ago)
storage ID 61c9df09
Duration : 1.136s
```

### we fix it :

```out
restic unlock --password-file ~/.restic/.pw
repository ac01d61d opened successfully, password is correct
successfully removed locks
```
