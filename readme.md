# Dev Instructions
Tutorial: https://dev.to/sasicodes/flask-and-env-22am

## Setup
py -m venv env
.\env\Scripts\activate
pip install flask flask-sqlalchemy gunicorn

HTMX 1.5.0
https://unpkg.com/htmx.org@1.5.0

Bootstrap 5.0.0-beta1
https://cdn.jsdelivr.net/npm/bootstrap@5.0.0-beta1/dist/css/bootstrap.min.css

## Notes

Werkzeug==2.3.0

Anytime you add a new flask package, you may need to update the Werkzeug to the correct version.

pip uninstall Werkzeug
pip install Werkzeug==2.3.0

## Run
py run.py

