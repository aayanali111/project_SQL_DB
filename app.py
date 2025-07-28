from flask import Flask
from routes import register_routes
import logging


logging.basicConfig(
    filename='app.log',  # Log file
    level=logging.INFO,  # Log level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Format
)


app = Flask(__name__)
app.config["SECRET_KEY"] = "myverysecretkey"

register_routes(app)

if __name__ == "__main__":
    logging.info("Running in debug mode.")
    app.run(host="192.168.137.1", port=5000, debug=True)


