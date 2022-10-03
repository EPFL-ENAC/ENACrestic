# Dev

1. `poetry install`
2. run with `poetry run python3 src/enacrestic/main.py`
3. manually run pre-commit hooks : `poetry run pre-commit run -a`

# Release

1. Set release number in `src/enacrestic/const.py`
2. `python -m build`
3. test built package with `pip install --user dist/ENACrestic-x.y.z.tar.gz`
4. `git commit`
5. `git tag $(python3 setup.py --version)`
6. `git push && git push --tags`
7. `python3 -m twine upload --repository ENACrestic --verbose dist/ENACrestic-x.y.z*`
