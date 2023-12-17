import os
from app import app

# Define a custom filter in your Flask app
@app.template_filter('date_format')
def date_format(value, format='%Y-%m-%d'):
    if value is None:
        return ""
    return value.strftime(format)

# Set the secret key for the app
# You can replace this with a fixed key or use an environment variable
app.secret_key = os.urandom(16)  # or a fixed key, or use os.environ.get('SECRET_KEY')

if __name__ == "__main__":
    app.run()