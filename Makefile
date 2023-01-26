install:
	poetry install

run:
	poetry run python3 enacrestic/main.py

lint:
	poetry run pre-commit run -a

package:
	poetry run python3 -m build
