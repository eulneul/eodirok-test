# 대화 내용 저장 /조회 관련 API
# 대화 내용을 DB에 저장하고, 저장된 데이터를 조회하는 API 제공.

from flask import Blueprint, request, jsonify
from ..models.save_message import *



message_bp = Blueprint('message_routes', __name__)

file_path = 'server/models/admin_info.txt'

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



@message_bp.route('/save_message/<user_id>/<project_name>', methods=['POST'])
def save_message(user_id, project_name):
    """
    특정 사용자의 프로젝트 테이블에 여러 메시지 저장
    """
    data_list = request.get_json()

    # 입력 데이터 검증
    if not isinstance(data_list, list):
        return jsonify({"error": "Input data must be a list of objects."}), 400

    for item in data_list:
        if not all(key in item for key in ['name', 'description', 'project_at']):
            return jsonify({"error": "Each object must contain 'name', 'description', and 'project_at'."}), 400

        if not isinstance(item['name'], str) or not isinstance(item['description'], str):
            return jsonify({"error": "Fields 'name' and 'description' must be strings."}), 400

        if not isinstance(item['project_at'], str):  # assuming datetime is passed as a string
            return jsonify({"error": "Field 'project_at' must be a string in datetime format."}), 400

    # 테이블 이름 검증
    if not project_name.isidentifier():
        return jsonify({"error": "Invalid project name provided."}), 400

    try:
        # 사용자 데이터베이스 생성 (처음 사용자일 경우)
        db_manager.create_user_database(user_id)

        # 사용자 데이터베이스 연결
        user_connection = db_manager.connect_user_database(user_id)

        # 프로젝트 테이블 생성 (없을 경우에만 생성)
        db_manager.create_project_table(user_connection, project_name)

        # 메시지 저장
        query = "INSERT INTO {table} (name, description, project_at) VALUES (%s, %s, %s)"
            

        for item in data_list:
            params = (item['name'], item['description'], item['project_at'])
            db_manager.execute_project_crud(user_connection, project_name, query, params)

        # 연결 닫기
        db_manager.close_connection(user_connection)

        return jsonify({"message": "Messages saved successfully"}), 201
    except Exception as e:
        print(f"Error saving messages: {e}")
        return jsonify({"error": str(e)}), 500


@message_bp.route('/get_message/<user_id>/<project_name>', methods=['GET'])
def get_messages(user_id, project_name):
    """
    특정 사용자의 프로젝트 테이블에서 메시지 조회
    """
    try:
        # 사용자 데이터베이스 연결
        user_connection = db_manager.connect_user_database(user_id)
        
        # 메시지 조회
        query = "SELECT * FROM {table}"
        results = db_manager.execute_project_crud(user_connection, project_name, query)
        
        # 연결 닫기
        db_manager.close_connection(user_connection)
        
        return jsonify(results), 200
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return jsonify({"error": str(e)}), 500
    
@message_bp.route('/get_project_tables/<user_id>', methods=['GET'])
def get_summary_tables(user_id):
    """
    user_id의 데이터베이스에서 summary_로 시작하는 테이블 리스트 반환
    """
    try:
        # 사용자 데이터베이스 연결
        user_connection = db_manager.connect_user_database(user_id)

        # summary_로 시작하는 테이블 이름 가져오기
        tables = db_manager.get_project_table(user_connection)

        # 연결 닫기
        db_manager.close_connection(user_connection)

        # 테이블이 없는 경우 메시지 반환
        if not tables:
            return jsonify({"message": "No summary tables found for the user."}), 200

        return jsonify({"summary_tables": tables}), 200
    except Exception as e:
        print(f"Error retrieving summary tables: {e}")
        return jsonify({"error": str(e)}), 500
    

@message_bp.route('/delete_user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    특정 사용자의 데이터베이스 삭제
    """
    try:
        # 사용자 데이터베이스 삭제
        db_manager.delete_user_database(user_id)
        return jsonify({"message": f"User database for user_id '{user_id}' deleted successfully."}), 200
    except Exception as e:
        print(f"Error deleting user database: {e}")
        return jsonify({"error": str(e)}), 500
    