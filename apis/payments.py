# routes/mempayments.py
from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from db import get_db_connection
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create a Namespace instead of a separate Api instance
payment_ns = Namespace("payments", description="Operations related to payment")


@payment_ns.route("/<int:member_id>")
class Payments(Resource):
    def get(self, member_id):
        """
        Get payment details of a specific member by ID
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Fix: Query the correct payments table
            cursor.execute("SELECT id, amount, payment_date, payment_method, status, transaction_id FROM payments WHERE member_id = %s",(member_id,),)
            payments = cursor.fetchall()
            cursor.close()
            conn.close()

            # Fix: Adjust dictionary to match fetched columns
            payments_list = [
                {
                    "id": p[0],
                    "amount": p[1],
                    "payment_date": p[2],
                    "payment_method": p[3],
                    "status": p[4],
                }
                for p in payments
            ]

            logger.info(f"Fetched {len(payments_list)} payments from the database.")
            print("Fetched payments successfully")

            return jsonify({"payments": payments_list})  
        except Exception as e:
            logger.error(f"Error fetching payments: {str(e)}")
            return (
                jsonify({"error": "Failed to fetch payments", "details": str(e), "code": 500}))
