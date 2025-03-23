# routes/membership_plans.py
from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from db import get_db_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create a Namespace instead of a separate Api instance
members_ns = Namespace('members', description='Operations related to members')
# Define the Member model
member_model = members_ns.model('Member', {
    'id': fields.Integer(readOnly=True, description='The member unique identifier'),
    'first_name': fields.String(required=True, description='First name of the member'),
    'last_name': fields.String(required=True, description='Last name of the member'),
    'email': fields.String(required=True, description='Email address of the member'),
    'address': fields.String(required=True, description=' Address of the member'),
    'Phone': fields.String(required=True, description='Phone number of the member', max=10),
})

@members_ns.route('')
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
@members_ns.route('/members/<int:member_id>')
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

    @members_ns.expect(member_model)
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


# Add a new member (POST)
@members_ns.route('')
class Members(Resource):
    @members_ns.expect(member_model)
    def post(self):
        """
        Add a new member
        """
        try:
            # Get data from request
            data = request.json

            # Check if required data is present
            if not data.get('first_name') or not data.get('last_name') or not data.get('email') or not data.get('phone') or not data.get('address'):
                return jsonify({"error": "All fields are required"}), 400  # Ensure the response is returned only as a dictionary

            # Database connection
            conn = get_db_connection()
            cursor = conn.cursor()

            # Insert new member into the database
            cursor.execute(
                "INSERT INTO members (first_name, last_name, email, phone_number, address) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (data['first_name'], data['last_name'], data['email'], data['phone'], data['address'])
            )

          
            # Commit changes and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            # Return success response as a dictionary
            return jsonify({"message": "Member added successfully", "code":201})  # Ensure proper return type here

        except Exception as e:
            # Log the exception
            logger.error(f"Error while adding member: {str(e)}")

            # Return a response with the error message
            # return jsonify({"error": "Failed to add member", "details": str(e)}), 500  # Ensure proper return type here
            return jsonify({"error": "Failed to add member","details": str(e), "code": 500})