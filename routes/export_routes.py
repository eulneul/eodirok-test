import csv
from flask import Response, request, jsonify
from flask_restx import Namespace, Resource, fields
from models.save_summary import SummaryDBManager

# Namespace 생성
export_ns = Namespace('export', description='Export-related operations')

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

# DB 매니저 초기화
summary_manager = SummaryDBManager(admin_config)

# Swagger 모델 정의
export_json_model = export_ns.model('ExportJSON', {
    'name': fields.String(required=True, description='Name of the entity'),
    'topic': fields.String(required=True, description='Topic of the entity'),
    'project_at': fields.String(required=True, description='Timestamp of the project')
})


@export_ns.route('/export_json_to_csv')
class ExportJSONToCSV(Resource):
    @export_ns.expect([export_json_model])
    def post(self):
        """
        Export JSON data to CSV.
        """
        try:
            input_data = request.get_json()

            if not isinstance(input_data, list):
                return {"error": "Input data must be a list of objects."}, 400

            if not input_data:
                return {"error": "Input data is empty."}, 400

            # CSV 데이터 생성
            def generate_csv():
                headers = input_data[0].keys()
                yield ",".join(headers) + "\n"
                for row in input_data:
                    yield ",".join([str(row.get(header, "")) for header in headers]) + "\n"

            return Response(
                generate_csv(),
                mimetype='text/csv',
                headers={"Content-Disposition": "attachment;filename=exported_data.csv"}
            )

        except Exception as e:
            print(f"Error exporting JSON to CSV: {e}")
            return {"error": str(e)}, 500


@export_ns.route('/export_table_to_csv/<string:user_id>/<string:project_name>')
class ExportTableToCSV(Resource):
    def get(self, user_id, project_name):
        """
        Export a specific user's project table data to CSV.
        """
        try:
            user_connection = summary_manager.connect_user_database(user_id)

            # 테이블 데이터 조회
            query = "SELECT * FROM {table}"
            results = summary_manager.execute_summary_crud(user_connection, project_name, query)

            # 연결 닫기
            summary_manager.close_connection(user_connection)

            if not results:
                return {"error": "No data found in the table."}, 404

            # CSV 데이터 생성
            def generate_csv():
                headers = ["id", "name", "topic", "project_at", "created_at", "updated_at"]
                yield ",".join(headers) + "\n"
                for row in results:
                    yield ",".join([str(value) for value in row]) + "\n"

            return Response(
                generate_csv(),
                mimetype='text/csv',
                headers={"Content-Disposition": f"attachment;filename={project_name}_data.csv"}
            )

        except Exception as e:
            print(f"Error exporting table to CSV: {e}")
            return {"error": str(e)}, 500
