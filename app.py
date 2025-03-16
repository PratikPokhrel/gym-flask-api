from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from flask_swagger_ui import get_swaggerui_blueprint
import psycopg2
import os
from flask_cors import CORS  # ✅ Import CORS
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize Flask App and API
app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

api = Api(app, version='1.0', title='Gym Membership API', description='A simple API for gym membership management')

# Database Connection
# DATABASE_URL = "postgresql://postgres:#Qji-4A9EViZFVF@db.dwqtomuxdcwtyaarjjfs.supabase.co:5432/postgres?sslmode=require"
DATABASE_URL ="postgresql://postgres.dwqtomuxdcwtyaarjjfs:#Qji-4A9EViZFVF@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

# Swagger UI Setup
SWAGGER_URL = '/swagger'  
API_URL = '/swagger.json'  
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Gym Membership API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Define the Member model
member_model = api.model('Member', {
    'id': fields.Integer(readOnly=True, description='The member unique identifier'),
    'first_name': fields.String(required=True, description='First name of the member'),
    'last_name': fields.String(required=True, description='Last name of the member'),
    'email': fields.String(required=True, description='Email address of the member')
})

@api.route('/members')
class MemberList(Resource):
    def get(self):
        """
        Get all gym members from the database
        """
        logger.info("Received GET request to fetch all members.")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, first_name, last_name, email, address, image, status FROM members")
            members = cursor.fetchall()
            cursor.close()
            conn.close()

            members_list = [
                {"id": m[0], "first_name": m[1], "last_name": m[2], "email": m[3], "address": m[4], "image": m[5], "status": m[6]}
                for m in members
            ]

            logger.info(f"Fetched {len(members_list)} members from the database.")
            print('get members')
            return jsonify({"members": members_list})

        except Exception as e:
            logger.error(f"Error fetching members: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500

# Get, Update, and Delete a Single Member
@api.route('/members/<int:member_id>')
class Member(Resource):
    def get(self, member_id):
        """
        Get details of a specific member by ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, first_name, last_name, email FROM members WHERE id = %s", (member_id,))
        member = cursor.fetchone()
        cursor.close()
        conn.close()

        if member:
            return jsonify({"id": member[0], "first_name": member[1], "last_name": member[2], "email": member[3]})
        return jsonify({"error": "Member not found"}), 404

    @api.expect(member_model)
    def put(self, member_id):
        """
        Update member details by ID
        """
        data = request.json
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE members SET first_name = %s, last_name = %s, email = %s WHERE id = %s",
            (data['first_name'], data['last_name'], data['email'], member_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": "Member updated successfully"})

    def delete(self, member_id):
        """
        Delete a gym member by ID
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM members WHERE id = %s", (member_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({"message": f"Member {member_id} deleted successfully"})


@app.route('/payments/<int:member_id>', methods=['GET'])
def get_payment_history(member_id):
    """Fetches the payment history of a given member."""
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Failed to connect to the database"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, member_id, amount, payment_date, payment_method, status FROM payments WHERE member_id = %s ORDER BY payment_date DESC",
            (member_id,)
        )
        payments = cursor.fetchall()
        cursor.close()
        conn.close()

        payment_history = [
            {
                "id": p[0],
                "member_id": p[1],
                "amount": float(p[2]),
                "payment_date": p[3].strftime('%Y-%m-%d %H:%M:%S'),
                "payment_method": p[4],
                "status": p[5]
            }
            for p in payments
        ]

        return jsonify({"payments": payment_history})

    except Exception as e:
        logging.error(f"Error fetching payment history: {e}")
        return jsonify({"error": "Failed to fetch payment history"}), 500

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
