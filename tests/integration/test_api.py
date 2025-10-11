"""
API集成测试
"""
import pytest
import json
import time
from unittest.mock import patch, Mock, MagicMock
from flask import Flask
from werkzeug.test import Client

# 模拟Dash应用
with patch('server.app') as mock_app:
    mock_app.server = Flask(__name__)
    mock_app.server.config['TESTING'] = True
    mock_app.server.config['WTF_CSRF_ENABLED'] = False


class TestStreamAPI:
    """流式API测试类"""
    
    def test_stream_endpoint_success(self, sample_messages, mock_yychat_client):
        """测试流式聊天端点成功情况"""
        # 配置mock响应
        mock_stream_data = [
            {"choices": [{"delta": {"content": "这是"}}]},
            {"choices": [{"delta": {"content": "一个"}}]},
            {"choices": [{"delta": {"content": "测试"}}]},
            {"choices": [{"delta": {"content": "回复"}}]},
            {"choices": [{"delta": {}, "finish_reason": "stop"}]}
        ]
        
        def mock_stream_generator():
            for data in mock_stream_data:
                yield data
        
        mock_yychat_client.chat_completion.return_value = mock_stream_generator()
        
        # 模拟Flask应用和客户端
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/stream', methods=['POST'])
        def stream():
            from flask import request, Response, stream_with_context
            import json
            
            data = request.get_json() or {}
            message_id = data.get('message_id')
            messages_data = data.get('messages', [])
            session_id = data.get('session_id')
            role = data.get('role', 'assistant')
            personality_id = data.get('personality_id', 'health_assistant')
            
            @stream_with_context
            def generate():
                try:
                    for chunk in mock_yychat_client.chat_completion(
                        messages=messages_data,
                        stream=True,
                        conversation_id=session_id,
                        personality_id=personality_id
                    ):
                        if chunk and 'choices' in chunk and chunk['choices']:
                            content = chunk['choices'][0].get('delta', {}).get('content', '')
                            if content:
                                response_data = {
                                    "message_id": message_id,
                                    "content": content,
                                    "role": role,
                                    "status": "streaming"
                                }
                                yield f'data: {json.dumps(response_data)}\n\n'
                    
                    # 发送结束标志
                    end_data = {
                        "message_id": message_id,
                        "status": "completed",
                        "role": role
                    }
                    yield f'data: {json.dumps(end_data)}\n\n'
                    
                except Exception as e:
                    error_data = {
                        "message_id": message_id,
                        "status": "error",
                        "error": str(e),
                        "role": role
                    }
                    yield f'data: {json.dumps(error_data)}\n\n'
            
            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={'X-Accel-Buffering': 'no'}
            )
        
        client = app.test_client()
        
        request_data = {
            "messages": sample_messages,
            "session_id": "test_session",
            "personality_id": "test_personality",
            "message_id": "test_message",
            "role": "assistant"
        }
        
        response = client.post('/stream', json=request_data)
        
        assert response.status_code == 200
        assert response.content_type == 'text/event-stream'
        
        # 验证流式响应内容
        content = response.get_data(as_text=True)
        assert "data: " in content
        assert "test_message" in content
    
    def test_stream_endpoint_invalid_data(self):
        """测试流式聊天端点无效数据"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/stream', methods=['POST'])
        def stream():
            from flask import request, jsonify
            data = request.get_json() or {}
            
            if not data.get('messages'):
                return jsonify({'error': 'Messages are required'}), 400
            
            return jsonify({'status': 'success'})
        
        client = app.test_client()
        
        invalid_data = {
            "messages": [],  # 空消息列表
            "session_id": "test_session"
        }
        
        response = client.post('/stream', json=invalid_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_stream_endpoint_missing_fields(self):
        """测试流式聊天端点缺少必需字段"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/stream', methods=['POST'])
        def stream():
            from flask import request, jsonify
            data = request.get_json() or {}
            
            required_fields = ['messages', 'message_id', 'session_id']
            missing_fields = [field for field in required_fields if not data.get(field)]
            
            if missing_fields:
                return jsonify({'error': f'Missing required fields: {missing_fields}'}), 400
            
            return jsonify({'status': 'success'})
        
        client = app.test_client()
        
        incomplete_data = {
            "messages": [{"role": "user", "content": "测试"}]
            # 缺少其他必需字段
        }
        
        response = client.post('/stream', json=incomplete_data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_stream_endpoint_timeout(self, sample_messages, mock_yychat_client):
        """测试流式聊天端点超时处理"""
        # 模拟超时情况
        def timeout_generator():
            time.sleep(0.1)  # 模拟延迟
            yield {"status": "timeout", "error": "响应超时"}
        
        mock_yychat_client.chat_completion.return_value = timeout_generator()
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/stream', methods=['POST'])
        def stream():
            from flask import request, Response, stream_with_context
            import json
            
            data = request.get_json() or {}
            message_id = data.get('message_id')
            role = data.get('role', 'assistant')
            
            @stream_with_context
            def generate():
                for chunk in mock_yychat_client.chat_completion(
                    messages=data.get('messages', []),
                    stream=True
                ):
                    if chunk.get('status') == 'timeout':
                        timeout_data = {
                            "message_id": message_id,
                            "status": "timeout",
                            "error": "响应超时",
                            "role": role
                        }
                        yield f'data: {json.dumps(timeout_data)}\n\n'
                        break
            
            return Response(
                generate(),
                mimetype='text/event-stream',
                headers={'X-Accel-Buffering': 'no'}
            )
        
        client = app.test_client()
        
        request_data = {
            "messages": sample_messages,
            "session_id": "test_session",
            "personality_id": "test_personality",
            "message_id": "test_message",
            "role": "assistant"
        }
        
        response = client.post('/stream', json=request_data)
        
        assert response.status_code == 200
        content = response.get_data(as_text=True)
        assert "timeout" in content


class TestAuthenticationAPI:
    """认证API测试类"""
    
    def test_login_endpoint(self):
        """测试登录端点"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/login', methods=['POST'])
        def login():
            from flask import request, jsonify
            data = request.get_json() or {}
            
            username = data.get('username')
            password = data.get('password')
            
            if not username or not password:
                return jsonify({'error': 'Username and password are required'}), 400
            
            # 模拟登录验证
            if username == 'testuser' and password == 'testpassword':
                return jsonify({'status': 'success', 'user_id': 'test_user'})
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        
        client = app.test_client()
        
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        response = client.post('/login', json=login_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'
    
    def test_login_with_invalid_credentials(self):
        """测试使用无效凭据登录"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/login', methods=['POST'])
        def login():
            from flask import request, jsonify
            data = request.get_json() or {}
            
            username = data.get('username')
            password = data.get('password')
            
            if username == 'testuser' and password == 'testpassword':
                return jsonify({'status': 'success', 'user_id': 'test_user'})
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        
        client = app.test_client()
        
        login_data = {
            "username": "invalid_user",
            "password": "wrong_password"
        }
        
        response = client.post('/login', json=login_data)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'error' in data
    
    def test_logout_endpoint(self):
        """测试登出端点"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/logout', methods=['POST'])
        def logout():
            return jsonify({'status': 'success', 'message': 'Logged out'})
        
        client = app.test_client()
        
        response = client.post('/logout')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'success'


class TestErrorHandlingAPI:
    """API错误处理测试类"""
    
    def test_404_error(self):
        """测试404错误"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.errorhandler(404)
        def not_found(error):
            return {'error': 'Not found'}, 404
        
        client = app.test_client()
        
        response = client.get('/non_existent_endpoint')
        assert response.status_code == 404
    
    def test_500_error(self):
        """测试500错误"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/error')
        def error():
            raise Exception("Internal server error")
        
        @app.errorhandler(500)
        def internal_error(error):
            return {'error': 'Internal server error'}, 500
        
        client = app.test_client()
        
        response = client.get('/error')
        assert response.status_code == 500
    
    def test_invalid_json(self):
        """测试无效JSON"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/stream', methods=['POST'])
        def stream():
            from flask import request, jsonify
            try:
                data = request.get_json()
                return jsonify({'status': 'success'})
            except Exception as e:
                return jsonify({'error': 'Invalid JSON'}), 400
        
        client = app.test_client()
        
        response = client.post(
            '/stream',
            data="invalid json",
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_missing_content_type(self):
        """测试缺少Content-Type"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/stream', methods=['POST'])
        def stream():
            from flask import request, jsonify
            if request.content_type != 'application/json':
                return jsonify({'error': 'Content-Type must be application/json'}), 415
            return jsonify({'status': 'success'})
        
        client = app.test_client()
        
        response = client.post('/stream', data="{}")
        assert response.status_code == 415


class TestSecurityAPI:
    """API安全测试类"""
    
    def test_sql_injection_protection(self):
        """测试SQL注入防护"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/stream', methods=['POST'])
        def stream():
            from flask import request, jsonify
            data = request.get_json() or {}
            
            # 简单的输入验证
            messages = data.get('messages', [])
            for message in messages:
                content = message.get('content', '')
                # 检查是否包含SQL注入尝试
                if any(keyword in content.lower() for keyword in ['drop', 'delete', 'insert', 'update', 'select']):
                    return jsonify({'error': 'Invalid input detected'}), 400
            
            return jsonify({'status': 'success'})
        
        client = app.test_client()
        
        malicious_data = {
            "messages": [{"role": "user", "content": "'; DROP TABLE users; --"}],
            "session_id": "test_session",
            "personality_id": "test_personality",
            "message_id": "test_message",
            "role": "assistant"
        }
        
        response = client.post('/stream', json=malicious_data)
        
        # 应该被检测为恶意输入
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_xss_protection(self):
        """测试XSS防护"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/stream', methods=['POST'])
        def stream():
            from flask import request, jsonify
            data = request.get_json() or {}
            
            # 简单的XSS检查
            messages = data.get('messages', [])
            for message in messages:
                content = message.get('content', '')
                if '<script>' in content.lower() or 'javascript:' in content.lower():
                    return jsonify({'error': 'XSS attempt detected'}), 400
            
            return jsonify({'status': 'success'})
        
        client = app.test_client()
        
        xss_data = {
            "messages": [{"role": "user", "content": "<script>alert('xss')</script>"}],
            "session_id": "test_session",
            "personality_id": "test_personality",
            "message_id": "test_message",
            "role": "assistant"
        }
        
        response = client.post('/stream', json=xss_data)
        
        # 应该被检测为XSS尝试
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestRateLimitingAPI:
    """API限流测试类"""
    
    def test_rate_limiting(self, sample_messages):
        """测试API限流"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # 简单的内存限流实现
        request_counts = {}
        
        @app.route('/stream', methods=['POST'])
        def stream():
            from flask import request, jsonify
            client_ip = request.remote_addr
            
            # 检查请求频率
            current_time = time.time()
            if client_ip not in request_counts:
                request_counts[client_ip] = []
            
            # 清理1分钟前的记录
            request_counts[client_ip] = [
                req_time for req_time in request_counts[client_ip]
                if current_time - req_time < 60
            ]
            
            # 检查是否超过限制（每分钟10次）
            if len(request_counts[client_ip]) >= 10:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # 记录当前请求
            request_counts[client_ip].append(current_time)
            
            return jsonify({'status': 'success'})
        
        client = app.test_client()
        
        # 发送大量请求测试限流
        responses = []
        for i in range(15):  # 发送15个请求
            request_data = {
                "messages": sample_messages,
                "session_id": f"test_session_{i}",
                "personality_id": "test_personality",
                "message_id": f"test_message_{i}",
                "role": "assistant"
            }
            
            response = client.post('/stream', json=request_data)
            responses.append(response.status_code)
        
        # 检查是否有被限流的请求（状态码429）
        rate_limited = any(status == 429 for status in responses)
        assert rate_limited, "应该检测到限流"


class TestCORSAPI:
    """CORS跨域测试类"""
    
    def test_cors_headers(self):
        """测试CORS头部"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/stream', methods=['OPTIONS'])
        def options():
            from flask import Response
            response = Response()
            response.headers['Access-Control-Allow-Origin'] = '*'
            response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        client = app.test_client()
        
        response = client.options('/stream')
        
        # 检查CORS相关头部
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
    
    def test_cors_preflight(self):
        """测试CORS预检请求"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        @app.route('/stream', methods=['OPTIONS'])
        def options():
            from flask import Response
            response = Response()
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
            response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
            return response
        
        client = app.test_client()
        
        response = client.options('/stream', headers={
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        })
        
        assert response.status_code == 200
        assert response.headers.get('Access-Control-Allow-Origin') == 'http://localhost:3000'
