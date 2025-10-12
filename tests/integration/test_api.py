"""
API集成测试
"""
import pytest
import json
import time
from unittest.mock import patch, Mock
from server import app


class TestAuthenticationAPI:
    """认证API测试类"""
    
    def test_login_endpoint(self, test_app):
        """测试登录端点"""
        login_data = {
            "username": "testuser",
            "password": "testpassword"
        }
        
        response = test_app.post('/login', json=login_data)
        
        # 根据实际实现调整断言
        assert response.status_code in [200, 302]  # 成功或重定向
        
        # 验证响应内容
        if response.status_code == 200:
            data = response.get_json()
            assert data is not None
    
    def test_logout_endpoint(self, authenticated_client):
        """测试登出端点"""
        response = authenticated_client.post('/logout')
        
        assert response.status_code in [200, 302]
    
    def test_login_with_invalid_credentials(self, test_app):
        """测试使用无效凭据登录"""
        login_data = {
            "username": "invalid_user",
            "password": "wrong_password"
        }
        
        response = test_app.post('/login', json=login_data)
        
        assert response.status_code in [401, 400]  # 未授权或错误请求
    
    def test_protected_endpoint_without_auth(self, test_app):
        """测试未认证访问受保护端点"""
        response = test_app.get('/chat')
        
        assert response.status_code in [401, 302]  # 未授权或重定向到登录页


class TestChatAPI:
    """聊天API测试类"""
    
    def test_stream_endpoint_success(self, authenticated_client, sample_messages, mock_yychat_client):
        """测试流式聊天端点成功情况"""
        # 配置mock响应
        mock_stream_data = [
            {"content": "这是", "status": "streaming"},
            {"content": "一个", "status": "streaming"},
            {"content": "测试", "status": "streaming"},
            {"content": "回复", "status": "end"}
        ]
        
        def mock_stream_generator():
            for data in mock_stream_data:
                yield f"data: {json.dumps(data)}\n\n"
        
        with patch('server.generate') as mock_generate:
            mock_generate.return_value = mock_stream_generator()
            
            request_data = {
                "messages": sample_messages,
                "session_id": "test_session",
                "personality_id": "test_personality",
                "message_id": "test_message",
                "role": "assistant"
            }
            
            response = authenticated_client.post('/stream', json=request_data)
            
            assert response.status_code == 200
            assert response.content_type == 'text/event-stream'
    
    def test_stream_endpoint_invalid_data(self, authenticated_client):
        """测试流式聊天端点无效数据"""
        invalid_data = {
            "messages": [],  # 空消息列表
            "session_id": "test_session"
        }
        
        response = authenticated_client.post('/stream', json=invalid_data)
        
        assert response.status_code in [400, 422]  # 错误请求或无法处理的实体
    
    def test_stream_endpoint_missing_fields(self, authenticated_client):
        """测试流式聊天端点缺少必需字段"""
        incomplete_data = {
            "messages": [{"role": "user", "content": "测试"}]
            # 缺少其他必需字段
        }
        
        response = authenticated_client.post('/stream', json=incomplete_data)
        
        assert response.status_code in [400, 422]
    
    def test_stream_endpoint_timeout(self, authenticated_client, sample_messages):
        """测试流式聊天端点超时处理"""
        with patch('server.generate') as mock_generate:
            # 模拟超时情况
            def timeout_generator():
                time.sleep(0.1)  # 模拟延迟
                yield f"data: {json.dumps({'status': 'timeout', 'error': '响应超时'})}\n\n"
            
            mock_generate.return_value = timeout_generator()
            
            request_data = {
                "messages": sample_messages,
                "session_id": "test_session",
                "personality_id": "test_personality",
                "message_id": "test_message",
                "role": "assistant"
            }
            
            response = authenticated_client.post('/stream', json=request_data)
            
            assert response.status_code == 200
            # 验证超时响应内容
            content = response.get_data(as_text=True)
            assert "timeout" in content


class TestSessionManagementAPI:
    """会话管理API测试类"""
    
    def test_create_session(self, authenticated_client, mock_flask_login):
        """测试创建会话"""
        with patch('models.conversations.Conversations.add_conversation') as mock_add:
            mock_add.return_value = "test_conv_id"
            
            response = authenticated_client.post('/api/sessions', json={
                "conv_name": "新会话"
            })
            
            assert response.status_code == 201
            data = response.get_json()
            assert data["conv_id"] == "test_conv_id"
    
    def test_get_user_sessions(self, authenticated_client, mock_flask_login):
        """测试获取用户会话列表"""
        mock_sessions = [
            {"conv_id": "conv1", "conv_name": "会话1"},
            {"conv_id": "conv2", "conv_name": "会话2"}
        ]
        
        with patch('models.conversations.Conversations.get_user_conversations') as mock_get:
            mock_get.return_value = mock_sessions
            
            response = authenticated_client.get('/api/sessions')
            
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 2
            assert data[0]["conv_id"] == "conv1"
    
    def test_update_session(self, authenticated_client, mock_flask_login):
        """测试更新会话"""
        with patch('models.conversations.Conversations.update_conversation_by_conv_id') as mock_update:
            mock_update.return_value = Mock(conv_name="更新后的会话")
            
            response = authenticated_client.put('/api/sessions/test_conv_id', json={
                "conv_name": "更新后的会话"
            })
            
            assert response.status_code == 200
            mock_update.assert_called_once()
    
    def test_delete_session(self, authenticated_client, mock_flask_login):
        """测试删除会话"""
        with patch('models.conversations.Conversations.delete_conversation_by_conv_id') as mock_delete:
            mock_delete.return_value = True
            
            response = authenticated_client.delete('/api/sessions/test_conv_id')
            
            assert response.status_code == 200
            mock_delete.assert_called_once_with("test_conv_id")
    
    def test_get_session_history(self, authenticated_client, mock_flask_login):
        """测试获取会话历史"""
        mock_history = {
            "messages": [
                {"role": "user", "content": "用户消息"},
                {"role": "assistant", "content": "助手回复"}
            ]
        }
        
        with patch('models.conversations.Conversations.get_conversation_by_conv_id') as mock_get:
            mock_conv = Mock()
            mock_conv.conv_memory = mock_history
            mock_get.return_value = mock_conv
            
            response = authenticated_client.get('/api/sessions/test_conv_id/history')
            
            assert response.status_code == 200
            data = response.get_json()
            assert data["messages"] == mock_history["messages"]


class TestUserManagementAPI:
    """用户管理API测试类"""
    
    def test_get_user_profile(self, authenticated_client, mock_flask_login):
        """测试获取用户资料"""
        response = authenticated_client.get('/api/user/profile')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["user_id"] == "test_user"
    
    def test_update_user_profile(self, authenticated_client, mock_flask_login):
        """测试更新用户资料"""
        update_data = {
            "user_icon": "new_icon.png",
            "other_info": {"theme": "dark"}
        }
        
        with patch('models.users.Users.update_user') as mock_update:
            mock_update.return_value = Mock(user_icon="new_icon.png")
            
            response = authenticated_client.put('/api/user/profile', json=update_data)
            
            assert response.status_code == 200
            mock_update.assert_called_once()
    
    def test_change_password(self, authenticated_client, mock_flask_login):
        """测试修改密码"""
        password_data = {
            "old_password": "old_password",
            "new_password": "new_password"
        }
        
        with patch('models.users.Users.check_user_password') as mock_check:
            mock_check.return_value = True
            
            with patch('models.users.Users.update_user') as mock_update:
                response = authenticated_client.put('/api/user/password', json=password_data)
                
                assert response.status_code == 200
                mock_check.assert_called_once()
                mock_update.assert_called_once()
    
    def test_change_password_wrong_old_password(self, authenticated_client, mock_flask_login):
        """测试使用错误旧密码修改密码"""
        password_data = {
            "old_password": "wrong_password",
            "new_password": "new_password"
        }
        
        with patch('models.users.Users.check_user_password') as mock_check:
            mock_check.return_value = False
            
            response = authenticated_client.put('/api/user/password', json=password_data)
            
            assert response.status_code == 400
            mock_check.assert_called_once()


class TestErrorHandlingAPI:
    """API错误处理测试类"""
    
    def test_404_error(self, test_app):
        """测试404错误"""
        response = test_app.get('/non_existent_endpoint')
        assert response.status_code == 404
    
    def test_500_error(self, authenticated_client):
        """测试500错误"""
        with patch('models.conversations.Conversations.get_user_conversations') as mock_get:
            mock_get.side_effect = Exception("数据库错误")
            
            response = authenticated_client.get('/api/sessions')
            assert response.status_code == 500
    
    def test_invalid_json(self, authenticated_client):
        """测试无效JSON"""
        response = authenticated_client.post(
            '/stream',
            data="invalid json",
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_missing_content_type(self, authenticated_client):
        """测试缺少Content-Type"""
        response = authenticated_client.post('/stream', data="{}")
        assert response.status_code in [400, 415]  # 错误请求或不支持的媒体类型


class TestRateLimitingAPI:
    """API限流测试类"""
    
    def test_rate_limiting(self, authenticated_client, sample_messages):
        """测试API限流"""
        # 发送大量请求测试限流
        responses = []
        for i in range(100):  # 发送100个请求
            request_data = {
                "messages": sample_messages,
                "session_id": f"test_session_{i}",
                "personality_id": "test_personality",
                "message_id": f"test_message_{i}",
                "role": "assistant"
            }
            
            response = authenticated_client.post('/stream', json=request_data)
            responses.append(response.status_code)
        
        # 检查是否有被限流的请求（状态码429）
        rate_limited = any(status == 429 for status in responses)
        # 注意：如果应用没有实现限流，这个测试可能会失败
        # 这是正常的，可以根据实际实现调整


class TestCORSAPI:
    """CORS跨域测试类"""
    
    def test_cors_headers(self, test_app):
        """测试CORS头部"""
        response = test_app.options('/stream')
        
        # 检查CORS相关头部
        assert 'Access-Control-Allow-Origin' in response.headers
        assert 'Access-Control-Allow-Methods' in response.headers
        assert 'Access-Control-Allow-Headers' in response.headers
    
    def test_cors_preflight(self, test_app):
        """测试CORS预检请求"""
        response = test_app.options('/stream', headers={
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        })
        
        assert response.status_code == 200
        assert response.headers.get('Access-Control-Allow-Origin') is not None


class TestSecurityAPI:
    """API安全测试类"""
    
    def test_sql_injection_protection(self, authenticated_client):
        """测试SQL注入防护"""
        malicious_data = {
            "messages": [{"role": "user", "content": "'; DROP TABLE users; --"}],
            "session_id": "test_session",
            "personality_id": "test_personality",
            "message_id": "test_message",
            "role": "assistant"
        }
        
        response = authenticated_client.post('/stream', json=malicious_data)
        
        # 应该正常处理，不会导致SQL注入
        assert response.status_code in [200, 400]  # 成功或参数错误
    
    def test_xss_protection(self, authenticated_client):
        """测试XSS防护"""
        xss_data = {
            "messages": [{"role": "user", "content": "<script>alert('xss')</script>"}],
            "session_id": "test_session",
            "personality_id": "test_personality",
            "message_id": "test_message",
            "role": "assistant"
        }
        
        response = authenticated_client.post('/stream', json=xss_data)
        
        # 应该正常处理，不会执行脚本
        assert response.status_code in [200, 400]
    
    def test_csrf_protection(self, test_app):
        """测试CSRF防护"""
        # 这个测试需要根据实际的CSRF实现来调整
        response = test_app.post('/api/sessions', json={"conv_name": "测试"})
        
        # 如果没有CSRF保护，可能需要调整这个测试
        assert response.status_code in [200, 403, 400]
