from app import create_app, db
from flask_migrate import upgrade

app = create_app()

import logging
logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a')

if __name__ == "__main__":
    with app.app_context():
        upgrade()
    app.run(host="0.0.0.0", port=5000, debug=True, ssl_context="adhoc")