from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client
from dotenv import load_dotenv
import os
import jwt  # 用于生成和解析 JWT 令牌
import datetime
import bcrypt  # 用于密码哈希加密
from algorithm.kimi_single import get_ai_response

# 加载环境变量
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = "your_secret_key"  # 你可以换成更复杂的密钥
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

app = Flask(__name__)
# 启用 CORS 支持，允许所有来源
CORS(app, resources={r"/*": {"origins": "*"}})

# 生成 JWT 令牌
def generate_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)  # 过期时间 1 天
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

# 解析 JWT 令牌
def decode_jwt(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload["user_id"]
    except jwt.ExpiredSignatureError:
        return None  # 令牌过期
    except jwt.InvalidTokenError:
        return None  # 无效令牌

# **用户注册**
@app.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email 和密码不能为空"}), 400

        # **检查邮箱是否已注册**
        existing_user = supabase.table("users").select("id").eq("email", email).execute()
        if existing_user.data:
            return jsonify({"error": "该邮箱已注册"}), 400

        # **加密存储密码**
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # **插入数据库**
        user_data = supabase.table("users").insert({"email": email, "password": hashed_password}).execute()

        return jsonify({"message": "注册成功"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# **用户登录**
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "Email 和密码不能为空"}), 400

        # **查询用户**
        user = supabase.table("users").select("*").eq("email", email).execute()
        if not user.data:
            return jsonify({"error": "用户不存在"}), 400

        # **检查密码**
        user_record = user.data[0]
        if not bcrypt.checkpw(password.encode('utf-8'), user_record["password"].encode('utf-8')):
            return jsonify({"error": "密码错误"}), 401

        # **生成 JWT 令牌**
        token = generate_jwt(user_record["id"])

        return jsonify({"token": token, "message": "登录成功"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# **提问接口（必须带 JWT 令牌）**
@app.route('/process', methods=['POST'])
def process():
    try:
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "未提供身份令牌"}), 401

        user_id = decode_jwt(token)
        if not user_id:
            return jsonify({"error": "无效或过期的身份令牌"}), 401

        data = request.get_json()
        question = data.get("question", "")

        # **模拟算法**
        answer = get_ai_response(question)

        # **插入数据库**
        db_response = supabase.table("questions").insert({
            "user_id": user_id,
            "content": question,
            "response": answer
        }).execute()

        return jsonify({
            "id": db_response.data[0]['id'],
            "answer": answer
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)