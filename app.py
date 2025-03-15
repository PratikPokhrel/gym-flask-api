from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from flask_swagger_ui import get_swaggerui_blueprint

# Initialize Flask App and API
app = Flask(__name__)
api = Api(app, version='1.0', title='Gym Membership API', description='A simple API for gym membership management')

# Swagger UI Setup
SWAGGER_URL = '/swagger'  # Swagger UI endpoint
API_URL = '/swagger.json'  # URL to your Swagger JSON file
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={'app_name': "Gym Membership API"}
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# Mock Data for Gym Members
members = [
    {"id": 1, "name": "John Doe", "email": "john@example.com", "membership": "Gold", "status": "Active"},
    {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "membership": "Silver", "status": "Active"},
    {"id": 3, "name": "Bob Brown", "email": "bob@example.com", "membership": "Platinum", "status": "Inactive"}
]

# Define the Member model
member_model = api.model('Member', {
    'id': fields.Integer(readOnly=True, description='The member unique identifier'),
    'name': fields.String(required=True, description='The name of the member'),
    'email': fields.String(required=True, description='The email address of the member'),
    'membership': fields.String(required=True, description='The membership type'),
    'status': fields.String(required=True, description='The membership status')
})

# Get All Members
@api.route('/members')
class MemberList(Resource):
    def get(self):
        """
        Get all gym members
        """
        return jsonify({"members": members})

    @api.expect(member_model)
    def post(self):
        """
        Add a new gym member
        """
        new_member = request.json
        new_member["id"] = max(m["id"] for m in members) + 1  # Auto-increment ID
        members.append(new_member)
        return jsonify({"message": "Member added successfully", "member": new_member})

# Get a Single Member
@api.route('/members/<int:member_id>')
class Member(Resource):
    def get(self, member_id):
        """
        Get details of a specific member by ID
        """
        member = next((m for m in members if m["id"] == member_id), None)
        if member:
            return jsonify(member)
        return jsonify({"error": "Member not found"}), 404

    @api.expect(member_model)
    def put(self, member_id):
        """
        Update member details by ID
        """
        member = next((m for m in members if m["id"] == member_id), None)
        if not member:
            return jsonify({"error": "Member not found"}), 404

        data = request.json
        member.update(data)  # Update member data
        return jsonify({"message": "Member updated successfully", "member": member})

    def delete(self, member_id):
        """
        Delete a gym member by ID
        """
        global members
        members = [m for m in members if m["id"] != member_id]
        return jsonify({"message": f"Member {member_id} deleted successfully"})

# Run the Flask App
if __name__ == '__main__':
    app.run(debug=True)
