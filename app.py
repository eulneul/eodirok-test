from flask import Flask, request, jsonify
from .routes import register_routes
from .services.make_json import parse_text 
from flask_cors import CORS
import os

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 업로드 폴더 생성



def create_app():
    app = Flask(__name__)

    CORS(app, resources={r"/*": {"origins": "*"}})

    # 라우트 등록
    register_routes(app)

    @app.route('/login', methods=['POST'])
    def login():
        data = request.json
        user_id = data.get('id')

        if not user_id:
            return jsonify({"status": "error", "message": "ID is required"}), 400

        # ID 기반으로 DB 이름 설정 가능
        return jsonify({"status": "success", "message": f"Hello, {user_id}!"})
    
    @app.route('/upload', methods=['POST'])
    def upload_file():
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

            # parse_text 함수 호출
            json_data = parse_text(text_content)
            return jsonify(json_data), 200

        return jsonify({"status": "error", "message": "Invalid file format"}), 400
        
    return app



if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
