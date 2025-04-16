import os
import datetime
import firebase_admin
from firebase_admin import credentials, storage, firestore
from flask import Flask, request, jsonify
import uuid
import base64

# ✅ firebase-key.json 직접 불러오기
cred = credentials.Certificate("firebase-key.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': f"{cred.project_id}.appspot.com"
})
db = firestore.client()

# 🚀 Flask 앱 생성
app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_audio():
    try:
        data = request.get_json()
        audio_base64 = data.get("audio")
        if not audio_base64:
            return jsonify({'error': 'Missing audio data'}), 400

        filename = f"{uuid.uuid4()}.m4a"
        folder = "recordings"
        blob_path = f"{folder}/{filename}"

        # Storage 업로드
        bucket = storage.bucket()
        blob = bucket.blob(blob_path)
        blob.upload_from_string(base64.b64decode(audio_base64), content_type="audio/m4a")

        # Firestore 저장
        upload_time = datetime.datetime.utcnow()
        db.collection("tk_cough_logs").add({
            "filename": filename,
            "path": blob_path,
            "timestamp": upload_time,
            "downloadURL": blob.generate_signed_url(datetime.timedelta(days=7))
        })

        return jsonify({'message': '✅ Upload success!', 'filename': filename}), 200

    except Exception as e:
        print("🔥 서버 오류:", str(e))
        return jsonify({'error': str(e)}), 500

# 🔊 Render용 포트 설정
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)