install:
	poetry install

run:
	poetry run python3 src/enacrestic/main.py

lint:
	poetry run pre-commit run -a

package:
	poetry run python3 utils/fix_version.py
	poetry run python3 -m build
