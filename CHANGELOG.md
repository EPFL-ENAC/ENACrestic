# Changelog

## [0.7.2](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.7.1...v0.7.2) (2023-09-26)


### Bug Fixes

* **stale locks:** fix stale locks detection ([4ebfa87](https://github.com/EPFL-ENAC/ENACrestic/commit/4ebfa87d7dcd958b34e4528e50dace51bf63b598)), closes [#107](https://github.com/EPFL-ENAC/ENACrestic/issues/107)

## [0.7.1](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.7.0...v0.7.1) (2023-02-16)


### Documentation

* **README.md:** remove space before ':' ([0773da9](https://github.com/EPFL-ENAC/ENACrestic/commit/0773da95aaea4ed13089b25d30abafbcb24f3fa3))
* **server:** doc how to run on a server as root ([025853c](https://github.com/EPFL-ENAC/ENACrestic/commit/025853c34af325f3698bbfd1c846bc0b28363ca5)), closes [#45](https://github.com/EPFL-ENAC/ENACrestic/issues/45)

## [0.7.0](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.6.1...v0.7.0) (2023-02-09)


### Features

* **1st run:** auto-init the repo if needed and no previous backup ([1b56384](https://github.com/EPFL-ENAC/ENACrestic/commit/1b5638403b637aa9dca1dc673c99b853a1531363)), closes [#12](https://github.com/EPFL-ENAC/ENACrestic/issues/12)


### Documentation

* **README.md:** reword ([9e57f7e](https://github.com/EPFL-ENAC/ENACrestic/commit/9e57f7e9ee9f05295e8a56d6152d9a6aa7733be8))

## [0.6.1](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.6.0...v0.6.1) (2023-02-09)


### Bug Fixes

* **py<3.8:** remove f-string with equal specifier ([de5e9a6](https://github.com/EPFL-ENAC/ENACrestic/commit/de5e9a6f510596cfa2dc66e732f58a149132a9e6)), closes [#97](https://github.com/EPFL-ENAC/ENACrestic/issues/97)

## [0.6.0](https://github.com/EPFL-ENAC/ENACrestic/compare/v0.5.1...v0.6.0) (2023-02-07)


### Features

* **PyPI:** release package to PyPI as CD ([a963c75](https://github.com/EPFL-ENAC/ENACrestic/commit/a963c75362b40f7941ce5b44d4633c6a711ceafb)), closes [#20](https://github.com/EPFL-ENAC/ENACrestic/issues/20)


### Bug Fixes

* **package:** add missing dependencies ([6f9442a](https://github.com/EPFL-ENAC/ENACrestic/commit/6f9442a06d7129be30caffe9f822752cdd7633b6)), closes [#90](https://github.com/EPFL-ENAC/ENACrestic/issues/90)
* **package:** fix build & fix .desktop file ([e99ec86](https://github.com/EPFL-ENAC/ENACrestic/commit/e99ec863d36b4197bad4bf8c0084a356379deedf)), closes [#20](https://github.com/EPFL-ENAC/ENACrestic/issues/20)
* **release:** fix release-please and release to PyPI workflow ([b377391](https://github.com/EPFL-ENAC/ENACrestic/commit/b377391fc2c39016a40eddc2d144265a5fc8d61e))
* **restic_backup.py:** fix error handling ([f5bb05b](https://github.com/EPFL-ENAC/ENACrestic/commit/f5bb05bc6e06c6bd76a8da7800f69b856eb0e4ad)), closes [#57](https://github.com/EPFL-ENAC/ENACrestic/issues/57)
* **typo:** fix [#53](https://github.com/EPFL-ENAC/ENACrestic/issues/53) ([34b31d3](https://github.com/EPFL-ENAC/ENACrestic/commit/34b31d3bb67660dd556e0d22bfc8e9bad09e6e8f))
* **vscode:** fix non-sense config ([c3099cb](https://github.com/EPFL-ENAC/ENACrestic/commit/c3099cb7f5be1d694deff5e81248cff53505ba3c))


### Documentation

* **for devs:** update how to publish on PyPI (manualy) ([2565808](https://github.com/EPFL-ENAC/ENACrestic/commit/256580870cce0a7848bcb640ba89d50c67bd12cd))
* **README.md:** add common project badges ([750fc07](https://github.com/EPFL-ENAC/ENACrestic/commit/750fc072298f9e82a567b4a91c3a41096ab6e802))

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
