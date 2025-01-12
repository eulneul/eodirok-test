import csv
from flask import Blueprint, jsonify, Response, request
from ..models.save_summary import SummaryDBManager

export_bp = Blueprint('export_routes', __name__)

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
summary_manager = SummaryDBManager(admin_config)


@export_bp.route('/export_json_to_csv', methods=['POST'])
def export_json_to_csv():
    """
    JSON 리스트를 입력받아 CSV로 출력
    """
    try:
        # JSON 데이터 요청
        input_data = request.get_json()

        if not isinstance(input_data, list):
            return jsonify({"error": "Input data must be a list of objects."}), 400

        if not input_data:
            return jsonify({"error": "Input data is empty."}), 400

        # CSV 데이터 생성
        def generate_csv():
            # Header 생성
            headers = input_data[0].keys()
            yield ",".join(headers) + "\n"

            # 데이터 행 생성
            for row in input_data:
                yield ",".join([str(row.get(header, "")) for header in headers]) + "\n"

        # Response로 CSV 반환
        return Response(generate_csv(), mimetype='text/csv', headers={"Content-Disposition": "attachment;filename=exported_data.csv"})

    except Exception as e:
        print(f"Error exporting JSON to CSV: {e}")
        return jsonify({"error": str(e)}), 500


@export_bp.route('/export_table_to_csv/<user_id>/<project_name>', methods=['GET'])
def export_table_to_csv(user_id, project_name):
    """
    특정 사용자와 프로젝트의 테이블 데이터를 CSV로 출력
    """
    try:
        # 사용자 데이터베이스 연결
        user_connection = summary_manager.connect_user_database(user_id)

        # 테이블 데이터 조회
        query = "SELECT * FROM {table}"
        results = summary_manager.execute_summary_crud(user_connection, project_name, query)

        # 연결 닫기
        summary_manager.close_connection(user_connection)

        if not results:
            return jsonify({"error": "No data found in the table."}), 404

        # CSV 데이터 생성
        def generate_csv():
            # Header 생성
            headers = ["id", "name", "topic", "project_at", "created_at", "updated_at"]
            yield ",".join(headers) + "\n"

            # 데이터 행 생성
            for row in results:
                yield ",".join([str(value) for value in row]) + "\n"

        # Response로 CSV 반환
        return Response(generate_csv(), mimetype='text/csv', headers={"Content-Disposition": f"attachment;filename={project_name}_data.csv"})

    except Exception as e:
        print(f"Error exporting table to CSV: {e}")
        return jsonify({"error": str(e)}), 500