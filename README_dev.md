# Dev

1. `pipenv install`
2. `pipenv shell`
3. `export PYTHONPATH="src/:$PYTHONPATH"`
4. do your changes and run it with `python src/enacrestic/__init__.py`

# Release

1. Set release number in `src/enacrestic/const.py`
2. `python -m build`
3. test built package with `pip install --user dist/ENACrestic-x.y.z.tar.gz`
3. `git commit`
4. `git tag $(python3 setup.py --version)`
5. `git push && git push --tags`
6. `python3 -m twine upload --repository ENACrestic --verbose dist/ENACrestic-x.y.z*`
