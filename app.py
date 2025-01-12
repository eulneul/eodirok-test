from flask import Flask, request, jsonify
from flask_restx import Api
from flask_cors import CORS
import os

# 네임스페이스 임포트
from routes.archive_routes import archive_ns
from routes.export_routes import export_ns
from routes.message_routes import message_ns
from services.make_json import parse_text

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 업로드 폴더 생성


def create_app():
    app = Flask(__name__)

    # CORS 설정
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Swagger API 초기화
    api = Api(
        app,
        version="1.0",
        title="API Documentation",
        description="API documentation with Swagger UI",
    )

    # 네임스페이스 등록
    api.add_namespace(archive_ns, path='/archive')
    api.add_namespace(export_ns, path='/export')
    api.add_namespace(message_ns, path='/messages')

    # 추가 엔드포인트
    @app.route('/login', methods=['POST'])
    def login():
        """
        Login API for user authentication.
        """
        data = request.json
        user_id = data.get('id')

        if not user_id:
            return jsonify({"status": "error", "message": "ID is required"}), 400

        return jsonify({"status": "success", "message": f"Hello, {user_id}!"})

    @app.route('/upload', methods=['POST'])
    def upload_file():
        """
        Upload a text file and convert its content to JSON.
        """
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"status": "error", "message": "No selected file"}), 400

        if file and file.filename.endswith('.txt'):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # 파일 내용 읽기 및 JSON 변환
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()

            json_data = parse_text(text_content)
            return jsonify(json_data), 200

        return jsonify({"status": "error", "message": "Invalid file format"}), 400

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
