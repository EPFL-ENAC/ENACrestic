# Dev

1. `make install`
2. run with `make run`
3. manually run pre-commit hooks : `make lint`

# Release

1. Check version in `.release-please-manifest.json`
2. `ENACRESTIC_VERSION=$(poetry run python3 setup.py --version) && echo Working on enacrestic $ENACRESTIC_VERSION`
3. `make package`
4. test new package with `pip install --user dist/enacrestic-${ENACRESTIC_VERSION}.tar.gz`
5. `git commit`
6. `git tag $(python3 setup.py --version)`
7. `git push && git push --tags`
8. `python3 -m twine upload --repository enacrestic --verbose dist/ENACrestic-${ENACRESTIC_VERSION}*`
