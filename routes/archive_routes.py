# archiving data creation / 조회

from flask import Blueprint, request, jsonify
from ..services.topic_modeling import TopicExtractor
from ..models.save_summary import *
import os



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

archive_bp = Blueprint('archive_routes', __name__)
summary_manager = SummaryDBManager(admin_config)

stop_words_file = os.path.join('server', 'services', 'stop_word.txt')
topic_extractor = TopicExtractor(stop_words_file)

@archive_bp.route('/extract_topics_from_descriptions', methods=['POST'])
def extract_topics_from_descriptions():
    """
    각 description에 대해 주제를 추출하고 결과 반환
    """
    try:
        # JSON 데이터 요청
        input_data = request.get_json()

        if not isinstance(input_data, list):
            return jsonify({"error": "Input data must be a list of objects."}), 400

        # 결과를 저장할 리스트
        results = []
        
        # 각 항목에 대해 주제 추출 수행
        for item in input_data:
            if 'name' in item and 'description' in item and 'project_at' in item:
                # Description에서 주제 추출
                topics = topic_extractor.extract_topics(item['description'], num_topics=1)

                # 결과 저장
                results.append({
                    "name": item['name'],
                    "topic": topics[0],
                    "project_at": item['project_at']
                })
            else:
                return jsonify({"error": "Each object must contain 'name', 'description', and 'project_at'."}), 400

        return jsonify(results), 200

    except Exception as e:
        print(f"Error extracting topics: {e}")
        return jsonify({"error": str(e)}), 500
    
@archive_bp.route('/save_summary/<user_id>/<project_name>', methods=['POST'])
def save_message(user_id, project_name):
    """
    특정 사용자의 프로젝트 테이블에 여러 메시지 저장
    """
    data_list = request.get_json()

    # 입력 데이터 검증
    if not isinstance(data_list, list):
        return jsonify({"error": "Input data must be a list of objects."}), 400

    for item in data_list:
        if not all(key in item for key in ['name', 'topic', 'project_at']):
            return jsonify({"error": "Each object must contain 'name', 'topic', and 'project_at'."}), 400

        if not isinstance(item['name'], str) or not isinstance(item['topic'], str):
            return jsonify({"error": "Fields 'name' and 'topic' must be strings."}), 400

        if not isinstance(item['project_at'], str):  # assuming datetime is passed as a string
            return jsonify({"error": "Field 'project_at' must be a string in datetime format."}), 400

    # 테이블 이름 검증
    if not project_name.isidentifier():
        return jsonify({"error": "Invalid project name provided."}), 400

    try:
        # 사용자 데이터베이스 생성 (처음 사용자일 경우)
        summary_manager.create_user_database(user_id)

        # 사용자 데이터베이스 연결
        user_connection = summary_manager.connect_user_database(user_id)

        # 프로젝트 테이블 생성 (없을 경우에만 생성)
        summary_manager.create_summary_table(user_connection, project_name)

        # 메시지 저장
        for item in data_list:
            query = "INSERT INTO {table} (name, description, summary_at) VALUES (%s, %s, %s)"
            params = (item['name'], item['topic'], item['project_at'])
            summary_manager.execute_summary_crud(user_connection, project_name, query, params)

        # 연결 닫기
        summary_manager.close_connection(user_connection)

        return jsonify({"message": "Messages saved successfully"}), 201
    except Exception as e:
        print(f"Error saving messages: {e}")
        return jsonify({"error": str(e)}), 500


    
@archive_bp.route('/get_summary/<user_id>/<project_name>', methods = ['GET'])
def get_summary(user_id, project_name):
    try:
        user_connection = summary_manager.connect_user_database(user_id)

        query = "SELECT * FROM {table}"
        result = summary_manager.execute_summary_crud(user_connection, project_name, query)

        summary_manager.close_connection(user_connection)
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return jsonify({"error": str(e)}) , 500
    

@archive_bp.route('/get_summary_tables/<user_id>', methods=['GET'])
def get_summary_tables(user_id):
    """
    user_id의 데이터베이스에서 summary_로 시작하는 테이블 리스트 반환
    """
    try:
        # 사용자 데이터베이스 연결
        user_connection = summary_manager.connect_user_database(user_id)

        # summary_로 시작하는 테이블 이름 가져오기
        tables = summary_manager.get_summary_tables(user_connection)

        # 연결 닫기
        summary_manager.close_connection(user_connection)

        # 테이블이 없는 경우 메시지 반환
        if not tables:
            return jsonify({"message": "No summary tables found for the user."}), 200

        return jsonify({"summary_tables": tables}), 200
    except Exception as e:
        print(f"Error retrieving summary tables: {e}")
        return jsonify({"error": str(e)}), 500
