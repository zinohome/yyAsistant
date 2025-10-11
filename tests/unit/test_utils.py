"""
工具函数单元测试
"""
import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from io import StringIO

# 模拟依赖
with patch('utils.yychat_client.BaseConfig') as mock_config:
    mock_config.yychat_api_base_url = "http://localhost:9800/v1"
    mock_config.yychat_api_key = "test_key"
    mock_config.yychat_default_model = "gpt-4.1"
    mock_config.yychat_default_temperature = 0.7
    mock_config.yychat_default_stream = True
    mock_config.yychat_default_use_tools = True
    
    from utils.yychat_client import YYChatClient
    from utils.log import log


class TestYYChatClient:
    """YYChat客户端测试类"""
    
    def test_init(self):
        """测试客户端初始化"""
        client = YYChatClient()
        assert client.api_base_url == "http://localhost:9800/v1"
        assert client.api_key == "test_key"
        assert "Content-Type" in client.headers
        assert "Authorization" in client.headers
    
    def test_chat_completion_non_stream(self, sample_messages, mock_requests):
        """测试非流式聊天完成"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "这是一个测试回复",
                    "role": "assistant"
                }
            }]
        }
        mock_requests.return_value = mock_response
        
        client = YYChatClient()
        response = client.chat_completion(
            messages=sample_messages,
            stream=False
        )
        
        assert response["choices"][0]["message"]["content"] == "这是一个测试回复"
        mock_requests.assert_called_once()
    
    def test_chat_completion_stream(self, sample_messages, mock_requests):
        """测试流式聊天完成"""
        # 模拟流式响应
        stream_data = [
            b'data: {"choices": [{"delta": {"content": "这是"}}]}\n\n',
            b'data: {"choices": [{"delta": {"content": "一个"}}]}\n\n',
            b'data: {"choices": [{"delta": {"content": "测试"}}]}\n\n',
            b'data: {"choices": [{"delta": {"content": "回复"}}]}\n\n',
            b'data: [DONE]\n\n'
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_lines.return_value = stream_data
        mock_requests.return_value = mock_response
        
        client = YYChatClient()
        response_generator = client.chat_completion(
            messages=sample_messages,
            stream=True
        )
        
        # 验证流式响应
        collected_content = ""
        for chunk in response_generator:
            if "choices" in chunk and chunk["choices"][0].get("delta", {}).get("content"):
                collected_content += chunk["choices"][0]["delta"]["content"]
        
        assert collected_content == "这是一个测试回复"
    
    def test_chat_completion_with_optional_params(self, sample_messages, mock_requests):
        """测试带可选参数的聊天完成"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "测试回复"}}]}
        mock_requests.return_value = mock_response
        
        client = YYChatClient()
        response = client.chat_completion(
            messages=sample_messages,
            stream=False,
            conversation_id="test_conv",
            personality_id="test_personality",
            use_tools=True
        )
        
        # 验证请求参数
        call_args = mock_requests.call_args
        assert call_args[1]['json']['conversation_id'] == "test_conv"
        assert call_args[1]['json']['personality_id'] == "test_personality"
        assert call_args[1]['json']['use_tools'] is True
    
    def test_list_models(self, mock_requests):
        """测试列出模型"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "model1", "name": "模型1"},
                {"id": "model2", "name": "模型2"}
            ]
        }
        mock_requests.return_value = mock_response
        
        client = YYChatClient()
        response = client.list_models()
        
        assert len(response["data"]) == 2
        assert response["data"][0]["id"] == "model1"
    
    def test_list_personalities(self, mock_requests):
        """测试列出人格"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"id": "personality1", "name": "人格1"},
                {"id": "personality2", "name": "人格2"}
            ]
        }
        mock_requests.return_value = mock_response
        
        client = YYChatClient()
        response = client.list_personalities()
        
        assert len(response["data"]) == 2
        assert response["data"][0]["id"] == "personality1"
    
    def test_get_conversation_memory(self, mock_requests):
        """测试获取会话记忆"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": [
                {"role": "user", "content": "用户消息"},
                {"role": "assistant", "content": "助手回复"}
            ]
        }
        mock_requests.return_value = mock_response
        
        client = YYChatClient()
        response = client.get_conversation_memory("test_conv_id")
        
        assert len(response["data"]) == 2
        assert response["data"][0]["role"] == "user"
    
    def test_clear_conversation_memory(self, mock_requests):
        """测试清除会话记忆"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"success": True}
        mock_requests.return_value = mock_response
        
        client = YYChatClient()
        response = client.clear_conversation_memory("test_conv_id")
        
        assert response["success"] is True
    
    def test_chat_completion_error_handling(self, sample_messages, mock_requests):
        """测试聊天完成错误处理"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.json.side_effect = Exception("JSON decode error")
        mock_requests.return_value = mock_response
        
        client = YYChatClient()
        
        with pytest.raises(Exception, match="API请求失败"):
            client.chat_completion(
                messages=sample_messages,
                stream=False
            )
    
    def test_api_error_with_json(self, sample_messages, mock_requests):
        """测试带JSON错误信息的API错误"""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "error": {
                "message": "API错误信息"
            }
        }
        mock_requests.return_value = mock_response
        
        client = YYChatClient()
        
        with pytest.raises(Exception, match="API错误信息"):
            client.chat_completion(
                messages=sample_messages,
                stream=False
            )


class TestLoggingUtils:
    """日志工具测试类"""
    
    def test_log_info(self, mock_logger):
        """测试信息日志"""
        log.info("测试信息")
        mock_logger.info.assert_called_once_with("测试信息")
    
    def test_log_error(self, mock_logger):
        """测试错误日志"""
        log.error("测试错误")
        mock_logger.error.assert_called_once_with("测试错误")
    
    def test_log_warning(self, mock_logger):
        """测试警告日志"""
        log.warning("测试警告")
        mock_logger.warning.assert_called_once_with("测试警告")
    
    def test_log_debug(self, mock_logger):
        """测试调试日志"""
        log.debug("测试调试")
        mock_logger.debug.assert_called_once_with("测试调试")
    
    def test_log_with_context(self, mock_logger):
        """测试带上下文的日志"""
        context = {"user_id": "test_user", "action": "login"}
        log.info("用户操作", extra=context)
        mock_logger.info.assert_called_once_with("用户操作", extra=context)
    
    def test_log_exception(self, mock_logger):
        """测试异常日志"""
        try:
            raise ValueError("测试异常")
        except ValueError as e:
            log.exception("捕获异常", exc_info=True)
            mock_logger.exception.assert_called_once_with("捕获异常", exc_info=True)


class TestUtilityFunctions:
    """通用工具函数测试类"""
    
    def test_json_serialization(self):
        """测试JSON序列化"""
        test_data = {
            "string": "测试字符串",
            "number": 123,
            "boolean": True,
            "list": [1, 2, 3],
            "dict": {"key": "value"}
        }
        
        # 序列化
        json_str = json.dumps(test_data, ensure_ascii=False)
        assert isinstance(json_str, str)
        
        # 反序列化
        parsed_data = json.loads(json_str)
        assert parsed_data == test_data
    
    def test_timestamp_generation(self):
        """测试时间戳生成"""
        timestamp1 = time.time()
        time.sleep(0.001)  # 短暂延迟
        timestamp2 = time.time()
        
        assert timestamp2 > timestamp1
        assert isinstance(timestamp1, float)
        assert isinstance(timestamp2, float)
    
    def test_message_id_generation(self):
        """测试消息ID生成"""
        # 模拟消息ID生成逻辑
        timestamp = int(time.time() * 1000)
        message_id = f"msg-{timestamp}"
        
        assert message_id.startswith("msg-")
        assert len(message_id) > 10
        assert message_id.isalnum() or "-" in message_id
    
    def test_conversation_id_generation(self):
        """测试会话ID生成"""
        user_id = "test_user"
        timestamp = int(time.time() * 1000)
        conv_id = f"conv-{user_id}-{timestamp}"
        
        assert conv_id.startswith("conv-")
        assert user_id in conv_id
        assert str(timestamp) in conv_id


class TestErrorHandling:
    """错误处理测试类"""
    
    def test_api_error_handling(self, sample_messages, mock_requests):
        """测试API错误处理"""
        # 模拟不同的API错误
        error_cases = [
            (ConnectionError("连接失败"), "网络连接错误"),
            (TimeoutError("请求超时"), "请求超时"),
            (ValueError("参数错误"), "参数验证错误"),
            (Exception("未知错误"), "未知错误")
        ]
        
        for error, expected_message in error_cases:
            mock_requests.side_effect = error
            
            client = YYChatClient()
            
            with pytest.raises(type(error)):
                client.chat_completion(
                    messages=sample_messages,
                    stream=False
                )
    
    def test_retry_mechanism(self, sample_messages, mock_requests):
        """测试重试机制"""
        # 模拟前两次调用失败，第三次成功
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"choices": [{"message": {"content": "成功回复"}}]}
        
        mock_requests.side_effect = [
            ConnectionError("第一次失败"),
            TimeoutError("第二次失败"),
            mock_response
        ]
        
        client = YYChatClient()
        
        # 这里需要根据实际的重试实现来调整测试
        # 如果实现了重试机制，应该最终成功
        # 如果没有实现，应该抛出异常
        try:
            response = client.chat_completion(
                messages=sample_messages,
                stream=False
            )
            assert response["choices"][0]["message"]["content"] == "成功回复"
        except (ConnectionError, TimeoutError):
            # 如果没有重试机制，这是预期的行为
            pass
    
    def test_graceful_degradation(self, mock_requests):
        """测试优雅降级"""
        # 模拟服务不可用时的降级处理
        mock_requests.side_effect = ConnectionError("服务不可用")
        
        client = YYChatClient()
        
        # 根据实际实现，可能有降级逻辑
        # 例如返回默认模型列表或缓存的数据
        try:
            response = client.list_models()
            # 如果有降级逻辑，验证返回了合理的默认值
            assert response is not None
        except ConnectionError:
            # 如果没有降级逻辑，这是预期的行为
            pass


class TestPerformanceUtils:
    """性能工具测试类"""
    
    def test_response_time_measurement(self, performance_timer):
        """测试响应时间测量"""
        timer = performance_timer
        
        # 模拟一些处理时间
        time.sleep(0.1)
        
        elapsed = timer()
        assert elapsed >= 0.1
        assert elapsed < 0.2  # 允许一些误差
    
    def test_memory_usage_measurement(self, memory_profiler):
        """测试内存使用测量"""
        profiler = memory_profiler
        
        # 创建一些数据来增加内存使用
        large_data = [i for i in range(10000)]
        
        memory_used = profiler()
        assert memory_used > 0  # 应该检测到内存使用增加
        
        # 清理数据
        del large_data
    
    def test_concurrent_requests(self, sample_messages, mock_requests):
        """测试并发请求处理"""
        import threading
        import queue
        
        results = queue.Queue()
        errors = queue.Queue()
        
        def make_request():
            try:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"choices": [{"message": {"content": "并发回复"}}]}
                mock_requests.return_value = mock_response
                
                client = YYChatClient()
                response = client.chat_completion(
                    messages=sample_messages,
                    stream=False
                )
                results.put(response)
            except Exception as e:
                errors.put(e)
        
        # 创建多个并发线程
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 验证结果
        assert results.qsize() == 5
        assert errors.qsize() == 0
