# Installation

DevKit requires Python 3.11+.

Recommended setups:

- Using pipx (isolated app install):
  ```bash
  python3 -m pip install --user pipx
  pipx ensurepath
  pipx install .
  ```

- Using Poetry (development):
  ```bash
  pipx install poetry
  make dev
  poetry run devkit --help
  ```

- Using pyenv (manage Python versions):
  ```bash
  curl https://pyenv.run | bash
  pyenv install 3.11.9
  pyenv local 3.11.9
  ```

Requirements:
- Python 3.11+
- Optional for DB features: `psql`, `pg_restore` in PATH
- Optional for Rails features: `rails` in PATH
