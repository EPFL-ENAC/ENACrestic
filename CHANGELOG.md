# Changelog

## [0.6.0](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.5.1...v0.6.0) (2023-01-26)


### Features

* **PyPI:** release package to PyPI as CD ([a963c75](https://github.com/EPFL-ENAC/ENACrestic/commit/a963c75362b40f7941ce5b44d4633c6a711ceafb)), closes [#20](https://github.com/EPFL-ENAC/ENACrestic/issues/20)


### Bug Fixes

* **package:** fix build & fix .desktop file ([e99ec86](https://github.com/EPFL-ENAC/ENACrestic/commit/e99ec863d36b4197bad4bf8c0084a356379deedf)), closes [#20](https://github.com/EPFL-ENAC/ENACrestic/issues/20)
* **restic_backup.py:** fix error handling ([f5bb05b](https://github.com/EPFL-ENAC/ENACrestic/commit/f5bb05bc6e06c6bd76a8da7800f69b856eb0e4ad)), closes [#57](https://github.com/EPFL-ENAC/ENACrestic/issues/57)
* **typo:** fix [#53](https://github.com/EPFL-ENAC/ENACrestic/issues/53) ([34b31d3](https://github.com/EPFL-ENAC/ENACrestic/commit/34b31d3bb67660dd556e0d22bfc8e9bad09e6e8f))
* **vscode:** fix non-sense config ([c3099cb](https://github.com/EPFL-ENAC/ENACrestic/commit/c3099cb7f5be1d694deff5e81248cff53505ba3c))

## [0.5.1](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.5.0...v0.5.1) (2022-11-30)


### Bug Fixes

* **pidfile:** fix to run on server ([4eebd69](https://github.com/EPFL-ENAC/ENACrestic/commit/4eebd69c8f58d0a3a11e17a9178db2c6049e504c)), closes [#51](https://github.com/EPFL-ENAC/ENACrestic/issues/51)

## [0.5.0](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.4.0...v0.5.0) (2022-11-29)


### Features

* **--no-gui:** app able to run on a server with no GUI ([d8c2276](https://github.com/EPFL-ENAC/ENACrestic/commit/d8c22764021457f49ced070f6c5943cf79bc43e5)), closes [#14](https://github.com/EPFL-ENAC/ENACrestic/issues/14)
* **logging:** auto rotation every 30 days ([24e8ad7](https://github.com/EPFL-ENAC/ENACrestic/commit/24e8ad7b726afda1cf9fb570f707537130a1aafd)), closes [#5](https://github.com/EPFL-ENAC/ENACrestic/issues/5)
* **pixmaps:** renaming ([8871098](https://github.com/EPFL-ENAC/ENACrestic/commit/8871098b6eaa71e3ffab6d07cf3ad6d231290191))
* **pre-backup hook:** run pre_backup script when present ([2f15847](https://github.com/EPFL-ENAC/ENACrestic/commit/2f158476d7beb6881fd9048dbc724914f84dea01)), closes [#15](https://github.com/EPFL-ENAC/ENACrestic/issues/15)
* **quit:** clean stop restic process if any ([0178fd6](https://github.com/EPFL-ENAC/ENACrestic/commit/0178fd6d5c372492e012640beefb146310432c37)), closes [#6](https://github.com/EPFL-ENAC/ENACrestic/issues/6)
* **repo lock:** auto-unlock when locked since 30+ minutes ([6ab6c42](https://github.com/EPFL-ENAC/ENACrestic/commit/6ab6c42532ed9d59831e43145b0fba2a514ae9a1)), closes [#6](https://github.com/EPFL-ENAC/ENACrestic/issues/6) [#10](https://github.com/EPFL-ENAC/ENACrestic/issues/10)


### Bug Fixes

* **repo lock:** add missing state message ([1311524](https://github.com/EPFL-ENAC/ENACrestic/commit/13115242ad995674ae1660a2b18adf4def57cbbc))
* **version:** fix auto-generated release-please 0.4.0 ([9c6824d](https://github.com/EPFL-ENAC/ENACrestic/commit/9c6824d018efd3ace8a025da0339eec9e0d4ede9))
* **version:** fix auto-generated release-please 0.4.0 ([ae8daf3](https://github.com/EPFL-ENAC/ENACrestic/commit/ae8daf3e464d8cfafc6bf4771fbd63225fb187c6))

## [0.4.0](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.3.0...v0.4.0) (2022-11-28)

### Features

- **pixmaps:** renaming ([8871098](https://github.com/EPFL-ENAC/ENACrestic/commit/8871098b6eaa71e3ffab6d07cf3ad6d231290191))
- **quit:** clean stop restic process if any ([0178fd6](https://github.com/EPFL-ENAC/ENACrestic/commit/0178fd6d5c372492e012640beefb146310432c37)), closes [#6](https://github.com/EPFL-ENAC/ENACrestic/issues/6)
- **repo lock:** auto-unlock when locked since 30+ minutes ([6ab6c42](https://github.com/EPFL-ENAC/ENACrestic/commit/6ab6c42532ed9d59831e43145b0fba2a514ae9a1)), closes [#6](https://github.com/EPFL-ENAC/ENACrestic/issues/6) [#10](https://github.com/EPFL-ENAC/ENACrestic/issues/10)

### Bug Fixes

- **version:** fix auto-generated release-please 0.4.0 ([ae8daf3](https://github.com/EPFL-ENAC/ENACrestic/commit/ae8daf3e464d8cfafc6bf4771fbd63225fb187c6))

## [0.3.0](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.2.0...v0.3.0) (2022-11-01)

### Refactor

- **project:** refactor ([29d6f09](https://github.com/EPFL-ENAC/ENACrestic/commit/29d6f0942677ef146edaf9c2851a71c1b6a19009))

## [0.2.0](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.1.9...v0.2.0) (2022-10-07)

### Features

- **--no-gui:** app able to run on a server with no GUI ([d8c2276](https://github.com/EPFL-ENAC/ENACrestic/commit/d8c22764021457f49ced070f6c5943cf79bc43e5)), closes [#14](https://github.com/EPFL-ENAC/ENACrestic/issues/14)
- **logging:** auto rotation every 30 days ([24e8ad7](https://github.com/EPFL-ENAC/ENACrestic/commit/24e8ad7b726afda1cf9fb570f707537130a1aafd)), closes [#5](https://github.com/EPFL-ENAC/ENACrestic/issues/5)
