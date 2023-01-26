# Dev

1. `make install`
2. run with `make run`
3. manually run pre-commit hooks : `make lint`

# Release

1. create a new branch linked to the issue you want to release
2. create a new PR and have it merged
3. release-please will create a new release PR
4. check it, and aprove it if everything is ok
5. release-to-pypi will create a new release and upload it to pypi

## Release manually (not recommended)

1. Check version in `.release-please-manifest.json`
2. `ENACRESTIC_VERSION=$(poetry run python3 setup.py --version) && echo Working on enacrestic $ENACRESTIC_VERSION`
3. `make package`
4. test new package with `pip install --user dist/enacrestic-${ENACRESTIC_VERSION}.tar.gz`
5. `poetry run python3 -m twine upload --repository pypi --verbose dist/enacrestic-${ENACRESTIC_VERSION}*`
