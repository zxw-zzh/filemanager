from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import jwt
import datetime
from functools import wraps
import shutil
import urllib.parse
from dotenv import load_dotenv

app = Flask(__name__)
# 配置CORS，允许所有来源的请求
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

load_dotenv()  # 读取 .env 文件

# 配置
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key')
UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', os.path.abspath("app"))
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin@01')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # 处理 OPTIONS 请求
        if request.method == 'OPTIONS':
            return '', 200

        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少token'}), 401
        try:
            token = token.split(' ')[1]  # Bearer token
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': '无效的token'}), 401
        return f(*args, **kwargs)
    return decorated

def safe_path_join(base_path, *paths):
    """安全地拼接路径，防止目录遍历攻击"""
    # 解码 URL 编码的路径
    decoded_paths = [urllib.parse.unquote(p) for p in paths]
    # 移除路径中的 .. 和 .
    clean_paths = []
    for p in decoded_paths:
        if '..' in p or p.startswith('/'):
            continue
        clean_paths.append(p)

    # 拼接路径
    full_path = os.path.join(base_path, *clean_paths)
    # 确保最终路径在基础目录内
    if not os.path.abspath(full_path).startswith(os.path.abspath(base_path)):
        return None
    return full_path

@app.route('/api/login', methods=['POST', 'OPTIONS'])
def login():
    # 处理 OPTIONS 请求
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        token = jwt.encode({
            'user': username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY)
        return jsonify({'token': token})
    return jsonify({'message': '用户名或密码错误'}), 401

@app.route('/api/files', methods=['GET'])
@token_required
def list_files():
    path = request.args.get('path', '')
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
    except ValueError:
        page = 1
        per_page = 10

    full_path = safe_path_join(app.config['UPLOAD_FOLDER'], path)

    if not full_path:
        return jsonify({'message': '无效的路径'}), 400

    if not os.path.exists(full_path):
        return jsonify({'message': '目录不存在'}), 404

    items = []
    for item in os.listdir(full_path):
        item_path = os.path.join(full_path, item)
        is_dir = os.path.isdir(item_path)

        # 获取文件信息
        stat = os.stat(item_path)
        size = 0 if is_dir else stat.st_size
        modified = int(stat.st_mtime)

        items.append({
            'name': item,
            'is_dir': is_dir,
            'size': size,
            'date': modified
        })

    # 计算分页
    total = len(items)
    total_pages = (total + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page

    # 返回分页后的数据
    return jsonify({
        'items': items[start:end],
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages
    })

@app.route('/api/files', methods=['POST'])
@token_required
def upload_file():
    # 支持批量上传：遍历所有request.files
    if not request.files:
        # 检查是否是创建文件夹请求
        folder_name = request.form.get('folder_name')
        if folder_name:
            path = request.form.get('path', '')
            full_path = safe_path_join(app.config['UPLOAD_FOLDER'], path)
            if not full_path:
                return jsonify({'message': '无效的路径'}), 400

            new_folder_path = os.path.join(full_path, folder_name)
            if os.path.exists(new_folder_path):
                return jsonify({'message': '文件夹已存在'}), 400

            try:
                os.makedirs(new_folder_path)
                return jsonify({'message': '文件夹创建成功'})
            except Exception as e:
                return jsonify({'message': f'创建文件夹失败: {str(e)}'}), 500

        return jsonify({'message': '没有文件'}), 400

    path = request.form.get('path', '')
    base_path = safe_path_join(app.config['UPLOAD_FOLDER'], path)
    if not base_path:
        return jsonify({'message': '无效的路径'}), 400
    os.makedirs(base_path, exist_ok=True)

    results = []
    for file_key in request.files:
        file = request.files[file_key]
        if file.filename == '':
            results.append({'filename': '', 'message': '没有选择文件'})
            continue
        # 支持相对路径还原文件夹结构
        relative_path = request.form.get('relative_path', file.filename)
        # 只取文件名时兼容老前端
        save_path = os.path.join(base_path, relative_path) if relative_path else os.path.join(base_path, file.filename)
        save_dir = os.path.dirname(save_path)
        try:
            os.makedirs(save_dir, exist_ok=True)
            file.save(save_path)
            results.append({'filename': relative_path, 'message': '文件上传成功'})
        except Exception as e:
            results.append({'filename': relative_path, 'message': f'上传失败: {str(e)}'})
    if len(results) == 1:
        return jsonify({'message': results[0]['message']})
    return jsonify({'results': results})

@app.route('/api/files', methods=['DELETE'])
@token_required
def delete_file():
    path = request.args.get('path', '')
    full_path = safe_path_join(app.config['UPLOAD_FOLDER'], path)

    if not full_path:
        return jsonify({'message': '无效的路径'}), 400

    if not os.path.exists(full_path):
        return jsonify({'message': '文件不存在'}), 404

    try:
        if os.path.isdir(full_path):
            # 检查文件夹是否为空
            if os.listdir(full_path):
                return jsonify({'message': '文件夹不为空，无法删除'}), 400
            os.rmdir(full_path)  # 删除空文件夹
        else:
            os.remove(full_path)  # 删除文件
        return jsonify({'message': '删除成功'})
    except Exception as e:
        return jsonify({'message': f'删除失败: {str(e)}'}), 500

@app.route('/api/files/download', methods=['GET'])
@token_required
def download_file():
    path = request.args.get('path', '')
    full_path = safe_path_join(app.config['UPLOAD_FOLDER'], path)

    if not full_path:
        return jsonify({'message': '无效的路径'}), 400

    if not os.path.exists(full_path):
        return jsonify({'message': '文件不存在'}), 404

    if os.path.isdir(full_path):
        return jsonify({'message': '不能下载文件夹'}), 400

    try:
        return send_file(
            full_path,
            as_attachment=True,
            download_name=os.path.basename(full_path),
            mimetype='application/octet-stream'
        )
    except Exception as e:
        return jsonify({'message': f'下载失败: {str(e)}'}), 500

@app.route('/api/files/rename', methods=['POST'])
@token_required
def rename_file():
    data = request.get_json()
    path = data.get('path', '')
    new_name = data.get('new_name')

    if not new_name:
        return jsonify({'message': '新名称不能为空'}), 400

    full_path = safe_path_join(app.config['UPLOAD_FOLDER'], path)
    if not full_path:
        return jsonify({'message': '无效的路径'}), 400

    if not os.path.exists(full_path):
        return jsonify({'message': '文件不存在'}), 404

    new_path = os.path.join(os.path.dirname(full_path), new_name)
    if os.path.exists(new_path):
        return jsonify({'message': '目标文件已存在'}), 400

    try:
        os.rename(full_path, new_path)
        return jsonify({'message': '重命名成功'})
    except Exception as e:
        return jsonify({'message': f'重命名失败: {str(e)}'}), 500

@app.route('/api/files/search', methods=['GET'])
@token_required
def search_files():
    query = request.args.get('query', '').lower()
    if not query:
        return jsonify({'message': '搜索关键词不能为空'}), 400

    results = []

    def search_in_directory(directory):
        try:
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                relative_path = os.path.relpath(item_path, app.config['UPLOAD_FOLDER'])

                # 检查文件名是否匹配
                if query in item.lower():
                    is_dir = os.path.isdir(item_path)
                    stat = os.stat(item_path)
                    size = 0 if is_dir else stat.st_size
                    modified = int(stat.st_mtime)

                    results.append({
                        'name': item,
                        'path': relative_path,
                        'is_dir': is_dir,
                        'size': size,
                        'date': modified
                    })

                # 如果是目录，递归搜索
                if os.path.isdir(item_path):
                    search_in_directory(item_path)
        except Exception as e:
            print(f"搜索错误: {str(e)}")

    search_in_directory(app.config['UPLOAD_FOLDER'])
    return jsonify(results)

@app.route('/api/files/move', methods=['POST'])
@token_required
def move_file():
    data = request.get_json()
    src = data.get('src', '')
    dst = data.get('dst', '')
    if not src or not dst:
        return jsonify({'message': '源路径和目标路径不能为空'}), 400
    src_path = safe_path_join(app.config['UPLOAD_FOLDER'], src)
    dst_dir = safe_path_join(app.config['UPLOAD_FOLDER'], dst)
    if not src_path or not dst_dir:
        return jsonify({'message': '无效的路径'}), 400
    if not os.path.exists(src_path):
        return jsonify({'message': '源文件不存在'}), 404
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir, exist_ok=True)
    new_path = os.path.join(dst_dir, os.path.basename(src_path))
    abs_src = os.path.abspath(src_path)
    abs_new = os.path.abspath(new_path)
    # 禁止移动到自身或子目录
    if abs_new == abs_src or abs_new.startswith(abs_src + os.sep):
        return jsonify({'message': '不能将文件或文件夹移动到自身或子目录下'}), 400
    if os.path.exists(new_path):
        return jsonify({'message': '目标已存在同名文件或文件夹'}), 400
    try:
        shutil.move(src_path, new_path)
        return jsonify({'message': '移动成功'})
    except Exception as e:
        return jsonify({'message': '移动失败: ' + str(e)}), 500

if __name__ == '__main__':
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5002))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host=host, port=port, debug=debug)