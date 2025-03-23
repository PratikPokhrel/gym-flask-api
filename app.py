from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS  # ✅ Import CORS
import logging
from apis.membership_plans import membership_ns
from apis.members import members_ns
from apis.payments import payment_ns



# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Flask App and API
app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

# Register Blueprints
# Add the membership plans namespace

api = Api(app, version='1.0', title='Gym Membership API', description='A simple API for gym membership management')
api.add_namespace(membership_ns, path='/membership_plans')
api.add_namespace(members_ns, path='/members')
api.add_namespace(payment_ns, path='/payments')

# Swagger UI Setup
SWAGGER_URL = '/swagger'  
API_URL = '/swagger.json'  
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Gym Membership API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


if __name__ == '__main__':
    app.run(debug=True)
