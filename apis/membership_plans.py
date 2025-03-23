# routes/membership_plans.py
from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from db import get_db_connection
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Create a Namespace instead of a separate Api instance
membership_ns = Namespace('membership_plans', description='Operations related to membership plans')

# Define the Membership Plan model for Swagger documentation
membership_plan_model = membership_ns.model('MembershipPlan', {
    'id': fields.Integer(readOnly=True, description='Unique ID of the membership plan'),
    'name': fields.String(required=True, description='Plan Name'),
    'price': fields.Float(required=True, description='Plan Price'),
    'duration': fields.Integer(required=True, description='Duration (days)'),
    'description': fields.String(description='Plan Description')
})

@membership_ns.route('')
class MembershipPlanList(Resource):
    def get(self):
        """Get all membership plans"""
        logger.info("Fetching all membership plans")
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, EXTRACT(EPOCH FROM duration) / 86400 AS duration, description FROM membership_plans")
            plans = cursor.fetchall()
            cursor.close()
            conn.close()

            plans_list = [
                {"id": p[0], "name": p[1], "price": p[2], "duration": int(p[3]), "description": p[4]}
                for p in plans
            ]
            return jsonify({"membership_plans": plans_list})

        except Exception as e:
            logger.error(f"Error fetching membership plans: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @membership_ns.expect(membership_plan_model)
    def post(self):
        """Create a new membership plan"""
        data = request.json
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO membership_plans (name, price, duration, description) VALUES (%s, %s, %s, %s) RETURNING id",
                (data['name'], data['price'], data['duration'], data.get('description', ''))
            )
            plan_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({"message": "Membership plan created", "id": plan_id})

        except Exception as e:
            logger.error(f"Error creating membership plan: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500

@membership_ns.route('/<int:id>')
class MembershipPlan(Resource):
    def get(self, id):
        """Get a single membership plan by ID"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, price, duration, description FROM membership_plans WHERE id = %s", (id,))
            plan = cursor.fetchone()
            cursor.close()
            conn.close()

            if plan:
                return jsonify({"id": plan[0], "name": plan[1], "price": plan[2], "duration": plan[3], "description": plan[4]})
            else:
                return jsonify({"message": "Membership plan not found"}), 404

        except Exception as e:
            logger.error(f"Error fetching membership plan: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @membership_ns.expect(membership_plan_model)
    def put(self, id):
        """Update a membership plan"""
        data = request.json
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE membership_plans SET name = %s, price = %s, duration = %s, description = %s WHERE id = %s",
                (data['name'], data['price'], data['duration'], data.get('description', ''), id)
            )
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({"message": "Membership plan updated"})

        except Exception as e:
            logger.error(f"Error updating membership plan: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    def delete(self, id):
        """Delete a membership plan"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM membership_plans WHERE id = %s", (id,))
            conn.commit()
            cursor.close()
            conn.close()

            return jsonify({"message": "Membership plan deleted"})

        except Exception as e:
            logger.error(f"Error deleting membership plan: {str(e)}", exc_info=True)
            return jsonify({"error": str(e)}), 500
