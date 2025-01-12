from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from models.save_message import PjDBManager

# Namespace 생성
message_ns = Namespace('messages', description='Message-related operations')

# DB 설정 읽기
file_path = 'models/admin_info.txt'

with open(file_path, 'r') as file:
    lines = file.readlines()

localhost = lines[0].strip()
dbname = lines[1].strip()
user = lines[2].strip()
password = lines[3].strip()
port = int(lines[4].strip())

admin_config = {
    'host': localhost,
    'dbname': dbname,
    'user': user,
    'password': password,
    'port': port
}

# DB 매니저 초기화
db_manager = PjDBManager(admin_config)

# Swagger 모델 정의
save_message_model = message_ns.model('SaveMessage', {
    'name': fields.String(required=True, description='Message name'),
    'description': fields.String(required=True, description='Message description'),
    'project_at': fields.String(required=True, description='Timestamp of the project')
})

get_message_response_model = message_ns.model('MessageResponse', {
    'id': fields.Integer(description='Message ID'),
    'name': fields.String(description='Message name'),
    'description': fields.String(description='Message description'),
    'project_at': fields.String(description='Timestamp of the project'),
    'created_at': fields.String(description='Created timestamp'),
    'updated_at': fields.String(description='Updated timestamp'),
})

@message_ns.route('/save_message/<string:user_id>/<string:project_name>')
class SaveMessage(Resource):
    @message_ns.expect([save_message_model])
    def post(self, user_id, project_name):
        """
        Save multiple messages for a user's project table.
        """
        data_list = request.get_json()

        if not isinstance(data_list, list):
            return {"error": "Input data must be a list of objects."}, 400

        for item in data_list:
            if not all(key in item for key in ['name', 'description', 'project_at']):
                return {"error": "Each object must contain 'name', 'description', and 'project_at'."}, 400

        try:
            db_manager.create_user_database(user_id)
            user_connection = db_manager.connect_user_database(user_id)
            db_manager.create_project_table(user_connection, project_name)

            query = "INSERT INTO {table} (name, description, project_at) VALUES (%s, %s, %s)"
            for item in data_list:
                params = (item['name'], item['description'], item['project_at'])
                db_manager.execute_project_crud(user_connection, project_name, query, params)

            db_manager.close_connection(user_connection)
            return {"message": "Messages saved successfully"}, 201
        except Exception as e:
            return {"error": str(e)}, 500


@message_ns.route('/get_message/<string:user_id>/<string:project_name>')
class GetMessages(Resource):
    @message_ns.marshal_with(get_message_response_model, as_list=True)
    def get(self, user_id, project_name):
        """
        Get messages for a specific user's project table.
        """
        try:
            user_connection = db_manager.connect_user_database(user_id)

            query = "SELECT * FROM {table}"
            results = db_manager.execute_project_crud(user_connection, project_name, query)

            db_manager.close_connection(user_connection)
            return results, 200
        except Exception as e:
            return {"error": str(e)}, 500


@message_ns.route('/get_project_tables/<string:user_id>')
class GetProjectTables(Resource):
    def get(self, user_id):
        """
        Get a list of project tables for a specific user.
        """
        try:
            user_connection = db_manager.connect_user_database(user_id)

            tables = db_manager.get_project_table(user_connection)

            db_manager.close_connection(user_connection)

            if not tables:
                return {"message": "No project tables found for the user."}, 200

            return {"project_tables": tables}, 200
        except Exception as e:
            return {"error": str(e)}, 500


@message_ns.route('/delete_user/<string:user_id>')
class DeleteUser(Resource):
    def delete(self, user_id):
        """
        Delete the database for a specific user.
        """
        try:
            db_manager.delete_user_database(user_id)
            return {"message": f"User database for user_id '{user_id}' deleted successfully."}, 200
        except Exception as e:
            return {"error": str(e)}, 500
