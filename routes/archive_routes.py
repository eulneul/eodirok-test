from flask_restx import Namespace, Resource, fields
from flask import request, jsonify
from services.topic_modeling import TopicExtractor
from models.save_summary import *
import os

# Namespace 생성
archive_ns = Namespace('archive', description='Archive-related operations')

# 파일 경로와 DB 정보 읽기
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

summary_manager = SummaryDBManager(admin_config)
stop_words_file = os.path.join('services', 'stop_word.txt')
topic_extractor = TopicExtractor(stop_words_file)

# Swagger 모델 정의
extract_topics_model = archive_ns.model('ExtractTopics', {
    'name': fields.String(required=True, description='Name of the entity'),
    'description': fields.String(required=True, description='Description of the entity'),
    'project_at': fields.String(required=True, description='Timestamp of the project')
})

save_summary_model = archive_ns.model('SaveSummary', {
    'name': fields.String(required=True, description='Name of the entity'),
    'topic': fields.String(required=True, description='Extracted topic'),
    'project_at': fields.String(required=True, description='Timestamp of the project')
})


@archive_ns.route('/extract_topics_from_descriptions')
class ExtractTopicsFromDescriptions(Resource):
    @archive_ns.expect([extract_topics_model])
    def post(self):
        """
        Extract topics from descriptions and return the results.
        """
        try:
            input_data = request.get_json()

            if not isinstance(input_data, list):
                return {"error": "Input data must be a list of objects."}, 400

            results = []
            for item in input_data:
                if 'name' in item and 'description' in item and 'project_at' in item:
                    topics = topic_extractor.extract_topics(item['description'], num_topics=1)
                    results.append({
                        "name": item['name'],
                        "topic": topics[0],
                        "project_at": item['project_at']
                    })
                else:
                    return {"error": "Each object must contain 'name', 'description', and 'project_at'."}, 400

            return results, 200
        except Exception as e:
            return {"error": str(e)}, 500


@archive_ns.route('/save_summary/<string:user_id>/<string:project_name>')
class SaveSummary(Resource):
    @archive_ns.expect([save_summary_model])
    def post(self, user_id, project_name):
        """
        Save summary data for a user's project.
        """
        data_list = request.get_json()

        if not isinstance(data_list, list):
            return {"error": "Input data must be a list of objects."}, 400

        try:
            summary_manager.create_user_database(user_id)
            user_connection = summary_manager.connect_user_database(user_id)
            summary_manager.create_summary_table(user_connection, project_name)

            query = "INSERT INTO {table} (name, description, summary_at) VALUES (%s, %s, %s)"
            for item in data_list:
                params = (item['name'], item['topic'], item['project_at'])
                summary_manager.execute_summary_crud(user_connection, project_name, query, params)

            summary_manager.close_connection(user_connection)
            return {"message": "Messages saved successfully"}, 201
        except Exception as e:
            return {"error": str(e)}, 500


@archive_ns.route('/get_summary/<string:user_id>/<string:project_name>')
class GetSummary(Resource):
    def get(self, user_id, project_name):
        """
        Get summary data for a specific user and project.
        """
        try:
            user_connection = summary_manager.connect_user_database(user_id)
            query = "SELECT * FROM {table}"
            result = summary_manager.execute_summary_crud(user_connection, project_name, query)
            summary_manager.close_connection(user_connection)
            return result, 200
        except Exception as e:
            return {"error": str(e)}, 500


@archive_ns.route('/get_summary_tables/<string:user_id>')
class GetSummaryTables(Resource):
    def get(self, user_id):
        """
        Get a list of summary tables for a specific user.
        """
        try:
            user_connection = summary_manager.connect_user_database(user_id)
            tables = summary_manager.get_summary_tables(user_connection)
            summary_manager.close_connection(user_connection)

            if not tables:
                return {"message": "No summary tables found for the user."}, 200

            return {"summary_tables": tables}, 200
        except Exception as e:
            return {"error": str(e)}, 500
