#!/usr/bin/env python3
"""
Web服务器 - 为伪代码解释器提供HTTP API
使用Flask提供简单的Web服务
"""
import sys
import os
from flask import Flask, request, jsonify, send_from_directory, session
from flask_cors import CORS
import traceback
import hashlib
import secrets

# 添加父目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lexer import Lexer, preprocess_pseudocode
from parser import Parser
from interpreter import Interpreter

app = Flask(__name__, static_folder='web', static_url_path='')
app.secret_key = secrets.token_hex(32)  # 生成随机密钥用于session
CORS(app, supports_credentials=True)  # 允许跨域请求并支持credentials

# 简单的内存数据库(演示用,实际应使用真实数据库)
users_db = {}  # {username: {password_hash, ...}}
files_db = {}  # {username: {file_id: {name, content, updated_at}}}

# 生成唯一文件ID
def generate_file_id():
    import time
    return f"file_{int(time.time() * 1000)}_{secrets.token_hex(4)}"


def hash_password(password: str) -> str:
    """对密码进行哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    return hash_password(password) == password_hash


@app.route('/')
def index():
    """主页"""
    return send_from_directory('web', 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """静态文件服务"""
    return send_from_directory('web', path)


@app.route('/api/run', methods=['POST'])
def run_code():
    """运行伪代码的API端点"""
    try:
        data = request.json
        code = data.get('code', '')
        debug = data.get('debug', False)
        strict = data.get('strict', False)

        if not code:
            return jsonify({
                'success': False,
                'error': '代码为空'
            })

        # 预处理代码
        code = preprocess_pseudocode(code)

        # 词法分析
        lexer = Lexer()
        tokens = lexer.tokenize(code)

        debug_info = []
        if debug:
            debug_info.append('=== Token流 ===')
            for token in tokens[:20]:  # 限制显示前20个token
                debug_info.append(str(token))
            if len(tokens) > 20:
                debug_info.append(f'... 还有 {len(tokens) - 20} 个tokens')

        # 语法分析
        parser = Parser(tokens)
        ast = parser.parse()

        if debug:
            debug_info.append('\n=== AST ===')
            debug_info.append(f'语句数: {len(ast.statements)}')
            debug_info.append(f'严格模式: {"开启" if strict else "关闭"}')

        # 捕获输出
        from io import StringIO
        output_buffer = StringIO()

        # 重定向stdout
        old_stdout = sys.stdout
        sys.stdout = output_buffer

        try:
            # 解释执行
            interpreter = Interpreter(strict_mode=strict)
            interpreter.interpret(ast)

            # 恢复stdout
            sys.stdout = old_stdout

            # 获取输出
            output = output_buffer.getvalue()
            output_lines = output.strip().split('\n') if output.strip() else ['(无输出)']

            return jsonify({
                'status': 'success',
                'output': output_lines,
                'debug_info': '\n'.join(debug_info) if debug else None
            })

        except Exception as e:
            # 恢复stdout
            sys.stdout = old_stdout

            # 获取已有的输出
            output = output_buffer.getvalue()

            error_msg = f'{type(e).__name__}: {str(e)}'

            return jsonify({
                'status': 'error',
                'error': error_msg,
                'output': output.strip().split('\n') if output.strip() else None,
                'traceback': traceback.format_exc() if debug else None
            })

    except SyntaxError as e:
        return jsonify({
            'status': 'error',
            'error': f'语法错误: {str(e)}'
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'错误: {str(e)}',
            'traceback': traceback.format_exc() if debug else None
        })


@app.route('/api/examples', methods=['GET'])
def get_examples():
    """获取示例代码列表"""
    examples = {
        'hello': {
            'name': 'Hello World',
            'description': '基本输出示例',
            'code': '''OUTPUT "Hello, World!"
DECLARE name : STRING
name <- "Alice"
OUTPUT "Hello,", name'''
        },
        'loop': {
            'name': '循环计数',
            'description': 'FOR循环示例',
            'code': '''OUTPUT "Counting from 1 to 10:"
FOR i <- 1 TO 10
    OUTPUT i
NEXT i'''
        },
        'array': {
            'name': '数组操作',
            'description': '数组声明和访问',
            'code': '''DECLARE numbers : ARRAY[1:5] OF INTEGER
FOR i <- 1 TO 5
    numbers[i] <- i * 10
NEXT i

OUTPUT "Array contents:"
FOR i <- 1 TO 5
    OUTPUT "numbers[", i, "] =", numbers[i]
NEXT i'''
        }
    }

    return jsonify({
        'success': True,
        'examples': examples
    })


@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        'status': 'ok',
        'version': '1.0.0',
        'interpreter': 'A-level CS Pseudocode'
    })


@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            })

        if len(username) < 3:
            return jsonify({
                'success': False,
                'error': '用户名至少需要3个字符'
            })

        if len(password) < 6:
            return jsonify({
                'success': False,
                'error': '密码至少需要6个字符'
            })

        if username in users_db:
            return jsonify({
                'success': False,
                'error': '用户名已存在'
            })

        # 创建用户
        users_db[username] = {
            'password_hash': hash_password(password),
            'created_at': __import__('datetime').datetime.now().isoformat()
        }

        # 设置session
        session['username'] = username
        session['logged_in'] = True

        return jsonify({
            'success': True,
            'user': {
                'username': username
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'注册失败: {str(e)}'
        })


@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return jsonify({
                'success': False,
                'error': '用户名和密码不能为空'
            })

        if username not in users_db:
            return jsonify({
                'success': False,
                'error': '用户名或密码错误'
            })

        user = users_db[username]
        if not verify_password(password, user['password_hash']):
            return jsonify({
                'success': False,
                'error': '用户名或密码错误'
            })

        # 设置session
        session['username'] = username
        session['logged_in'] = True

        return jsonify({
            'success': True,
            'user': {
                'username': username
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'登录失败: {str(e)}'
        })


@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户登出"""
    session.clear()
    return jsonify({
        'success': True
    })


@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """检查登录状态"""
    if session.get('logged_in'):
        return jsonify({
            'logged_in': True,
            'user': {
                'username': session.get('username')
            }
        })
    else:
        return jsonify({
            'logged_in': False
        })


# ==================== 文件管理API ====================

@app.route('/api/files', methods=['GET'])
def get_files():
    """获取用户的文件列表"""
    if not session.get('logged_in'):
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401

    username = session.get('username')

    # 初始化用户文件列表
    if username not in files_db:
        files_db[username] = {}

    # 转换为前端需要的格式
    files = []
    for file_id, file_data in files_db[username].items():
        files.append({
            'id': file_id,
            'name': file_data['name'],
            'updated_at': file_data['updated_at']
        })

    # 按更新时间排序（最新的在前）
    files.sort(key=lambda x: x['updated_at'], reverse=True)

    return jsonify({
        'success': True,
        'files': files
    })


@app.route('/api/files', methods=['POST'])
def create_file():
    """创建新文件"""
    if not session.get('logged_in'):
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401

    username = session.get('username')
    data = request.json
    file_name = data.get('name', 'untitled.pseudo').strip()

    if not file_name:
        return jsonify({
            'success': False,
            'error': '文件名不能为空'
        })

    # 初始化用户文件列表
    if username not in files_db:
        files_db[username] = {}

    # 生成文件ID
    file_id = generate_file_id()

    # 创建文件
    files_db[username][file_id] = {
        'name': file_name,
        'content': '',
        'updated_at': __import__('datetime').datetime.now().isoformat()
    }

    return jsonify({
        'success': True,
        'file': {
            'id': file_id,
            'name': file_name,
            'content': '',
            'updated_at': files_db[username][file_id]['updated_at']
        }
    })


@app.route('/api/files/<file_id>', methods=['GET'])
def get_file(file_id):
    """获取文件内容"""
    if not session.get('logged_in'):
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401

    username = session.get('username')

    if username not in files_db or file_id not in files_db[username]:
        return jsonify({
            'success': False,
            'error': '文件不存在'
        }), 404

    file_data = files_db[username][file_id]

    return jsonify({
        'success': True,
        'file': {
            'id': file_id,
            'name': file_data['name'],
            'content': file_data['content'],
            'updated_at': file_data['updated_at']
        }
    })


@app.route('/api/files/<file_id>', methods=['PUT'])
def update_file(file_id):
    """更新文件（内容或名称）"""
    if not session.get('logged_in'):
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401

    username = session.get('username')

    if username not in files_db or file_id not in files_db[username]:
        return jsonify({
            'success': False,
            'error': '文件不存在'
        }), 404

    data = request.json

    # 更新文件内容
    if 'content' in data:
        files_db[username][file_id]['content'] = data['content']
        files_db[username][file_id]['updated_at'] = __import__('datetime').datetime.now().isoformat()

    # 更新文件名
    if 'name' in data:
        new_name = data['name'].strip()
        if not new_name:
            return jsonify({
                'success': False,
                'error': '文件名不能为空'
            })
        files_db[username][file_id]['name'] = new_name
        files_db[username][file_id]['updated_at'] = __import__('datetime').datetime.now().isoformat()

    return jsonify({
        'success': True,
        'file': {
            'id': file_id,
            'name': files_db[username][file_id]['name'],
            'content': files_db[username][file_id]['content'],
            'updated_at': files_db[username][file_id]['updated_at']
        }
    })


@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """删除文件"""
    if not session.get('logged_in'):
        return jsonify({
            'success': False,
            'error': '请先登录'
        }), 401

    username = session.get('username')

    if username not in files_db or file_id not in files_db[username]:
        return jsonify({
            'success': False,
            'error': '文件不存在'
        }), 404

    # 删除文件
    del files_db[username][file_id]

    return jsonify({
        'success': True
    })


if __name__ == '__main__':
    print('=' * 60)
    print('A-level CS 伪代码解释器 - Web服务器')
    print('=' * 60)
    print()
    print('服务器启动中...')
    print()
    print('访问地址:')
    print('  线上: https://code.i-o.autos')
    print('  网络: http://0.0.0.0:8080')
    print()
    print('按 Ctrl+C 停止服务器')
    print('=' * 60)
    print()

    try:
        app.run(host='0.0.0.0', port=8080, debug=True)
    except KeyboardInterrupt:
        print('\n服务器已停止')
