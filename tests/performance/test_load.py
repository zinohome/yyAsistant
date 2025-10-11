"""
性能测试 - 负载测试
"""
import pytest
import time
import threading
import requests
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from locust import HttpUser, task, between
import statistics


class TestLoadPerformance:
    """负载性能测试类"""
    
    def test_concurrent_users(self, test_app):
        """测试并发用户访问"""
        def make_request():
            """模拟用户请求"""
            try:
                response = test_app.get('/')
                return response.status_code
            except Exception as e:
                return f"Error: {e}"
        
        # 并发用户数
        concurrent_users = 50
        results = []
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            # 提交所有任务
            futures = [executor.submit(make_request) for _ in range(concurrent_users)]
            
            # 收集结果
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        # 验证结果
        success_count = sum(1 for r in results if r == 200)
        success_rate = success_count / len(results)
        
        assert success_rate >= 0.95, f"成功率过低: {success_rate:.2%}"
    
    def test_chat_endpoint_load(self, authenticated_client, sample_messages):
        """测试聊天端点负载"""
        def send_chat_message():
            """发送聊天消息"""
            request_data = {
                "messages": sample_messages,
                "session_id": f"test_session_{threading.current_thread().ident}",
                "personality_id": "test_personality",
                "message_id": f"test_message_{int(time.time() * 1000)}",
                "role": "assistant"
            }
            
            try:
                response = authenticated_client.post('/stream', json=request_data)
                return {
                    "status_code": response.status_code,
                    "response_time": time.time() - start_time
                }
            except Exception as e:
                return {"error": str(e)}
        
        # 并发请求数
        concurrent_requests = 20
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(send_chat_message) for _ in range(concurrent_requests)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        # 分析结果
        successful_requests = [r for r in results if "error" not in r and r["status_code"] == 200]
        response_times = [r["response_time"] for r in successful_requests]
        
        if response_times:
            avg_response_time = statistics.mean(response_times)
            max_response_time = max(response_times)
            min_response_time = min(response_times)
            
            # 性能断言
            assert avg_response_time < 5.0, f"平均响应时间过长: {avg_response_time:.2f}秒"
            assert max_response_time < 10.0, f"最大响应时间过长: {max_response_time:.2f}秒"
            assert len(successful_requests) >= concurrent_requests * 0.9, "成功率过低"
    
    def test_database_operations_load(self, sample_user_data, sample_conversation_data):
        """测试数据库操作负载"""
        def create_user_and_conversation():
            """创建用户和会话"""
            try:
                from models.users import Users
                from models.conversations import Conversations
                
                user_id = f"load_test_user_{threading.current_thread().ident}_{int(time.time() * 1000)}"
                
                # 创建用户
                user = Users.add_user(
                    user_id=user_id,
                    user_name=f"loadtest_{user_id}",
                    password="testpassword"
                )
                
                # 创建会话
                conv_id = Conversations.add_conversation(
                    user_id=user_id,
                    conv_name="负载测试会话"
                )
                
                return {"success": True, "user_id": user_id, "conv_id": conv_id}
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        # 并发数据库操作数
        concurrent_operations = 30
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_operations) as executor:
            futures = [executor.submit(create_user_and_conversation) for _ in range(concurrent_operations)]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        # 分析结果
        successful_operations = [r for r in results if r["success"]]
        operation_time = time.time() - start_time
        
        success_rate = len(successful_operations) / len(results)
        operations_per_second = len(successful_operations) / operation_time
        
        # 性能断言
        assert success_rate >= 0.95, f"数据库操作成功率过低: {success_rate:.2%}"
        assert operations_per_second >= 10, f"数据库操作速度过慢: {operations_per_second:.2f} ops/sec"
    
    def test_memory_usage_under_load(self, test_app, memory_profiler):
        """测试负载下的内存使用"""
        profiler = memory_profiler
        
        def make_requests():
            """发送请求"""
            for _ in range(10):
                try:
                    test_app.get('/')
                    time.sleep(0.1)
                except Exception:
                    pass
        
        # 创建多个线程发送请求
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=make_requests)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        # 检查内存使用
        memory_used = profiler()
        
        # 内存使用断言（根据实际情况调整）
        assert memory_used < 100 * 1024 * 1024, f"内存使用过高: {memory_used / 1024 / 1024:.2f} MB"


class TestStressPerformance:
    """压力性能测试类"""
    
    def test_high_frequency_requests(self, test_app):
        """测试高频请求"""
        def rapid_requests():
            """快速发送请求"""
            for _ in range(100):
                try:
                    test_app.get('/')
                except Exception:
                    pass
        
        # 创建多个线程进行高频请求
        threads = []
        start_time = time.time()
        
        for _ in range(10):
            thread = threading.Thread(target=rapid_requests)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
        
        total_time = time.time() - start_time
        total_requests = 10 * 100  # 10个线程，每个100个请求
        requests_per_second = total_requests / total_time
        
        # 性能断言
        assert requests_per_second >= 100, f"请求处理速度过慢: {requests_per_second:.2f} req/sec"
    
    def test_large_message_handling(self, authenticated_client):
        """测试大消息处理"""
        # 创建大消息
        large_message = "这是一个非常大的消息。" * 1000  # 约30KB的消息
        
        request_data = {
            "messages": [{"role": "user", "content": large_message}],
            "session_id": "stress_test_session",
            "personality_id": "test_personality",
            "message_id": f"large_message_{int(time.time() * 1000)}",
            "role": "assistant"
        }
        
        start_time = time.time()
        response = authenticated_client.post('/stream', json=request_data)
        response_time = time.time() - start_time
        
        # 验证响应
        assert response.status_code == 200
        assert response_time < 10.0, f"大消息处理时间过长: {response_time:.2f}秒"
    
    def test_concurrent_sessions(self, authenticated_client, sample_messages):
        """测试并发会话处理"""
        def create_session_and_chat(session_id):
            """创建会话并发送消息"""
            try:
                # 发送聊天消息
                request_data = {
                    "messages": sample_messages,
                    "session_id": session_id,
                    "personality_id": "test_personality",
                    "message_id": f"message_{session_id}_{int(time.time() * 1000)}",
                    "role": "assistant"
                }
                
                response = authenticated_client.post('/stream', json=request_data)
                return {"session_id": session_id, "status_code": response.status_code}
            except Exception as e:
                return {"session_id": session_id, "error": str(e)}
        
        # 并发会话数
        concurrent_sessions = 50
        results = []
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_sessions) as executor:
            futures = [
                executor.submit(create_session_and_chat, f"stress_session_{i}")
                for i in range(concurrent_sessions)
            ]
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        
        # 分析结果
        successful_sessions = [r for r in results if "error" not in r and r["status_code"] == 200]
        success_rate = len(successful_sessions) / len(results)
        total_time = time.time() - start_time
        
        # 性能断言
        assert success_rate >= 0.9, f"并发会话成功率过低: {success_rate:.2%}"
        assert total_time < 30.0, f"并发会话处理时间过长: {total_time:.2f}秒"


class TestScalabilityPerformance:
    """可扩展性性能测试类"""
    
    def test_user_growth_simulation(self, test_app):
        """测试用户增长模拟"""
        def simulate_user_activity(user_id):
            """模拟用户活动"""
            activities = []
            
            # 模拟用户登录
            try:
                response = test_app.get('/')
                activities.append({"action": "login", "status": response.status_code})
            except Exception as e:
                activities.append({"action": "login", "error": str(e)})
            
            # 模拟用户浏览
            time.sleep(0.1)
            
            return {"user_id": user_id, "activities": activities}
        
        # 模拟用户增长：从10个用户增长到100个用户
        user_counts = [10, 25, 50, 75, 100]
        results = {}
        
        for user_count in user_counts:
            start_time = time.time()
            
            with ThreadPoolExecutor(max_workers=user_count) as executor:
                futures = [
                    executor.submit(simulate_user_activity, f"user_{i}")
                    for i in range(user_count)
                ]
                
                user_results = []
                for future in as_completed(futures):
                    result = future.result()
                    user_results.append(result)
            
            total_time = time.time() - start_time
            results[user_count] = {
                "total_time": total_time,
                "users_per_second": user_count / total_time,
                "successful_users": len([r for r in user_results if not any("error" in a for a in r["activities"])])
            }
        
        # 验证可扩展性
        for user_count, result in results.items():
            success_rate = result["successful_users"] / user_count
            assert success_rate >= 0.95, f"用户数{user_count}时成功率过低: {success_rate:.2%}"
    
    def test_data_volume_scalability(self, sample_user_data):
        """测试数据量可扩展性"""
        def create_large_dataset():
            """创建大数据集"""
            from models.users import Users
            from models.conversations import Conversations
            
            # 创建大量用户和会话
            users_created = 0
            conversations_created = 0
            
            try:
                for i in range(100):  # 创建100个用户
                    user_id = f"scale_test_user_{i}_{int(time.time() * 1000)}"
                    Users.add_user(
                        user_id=user_id,
                        user_name=f"scaletest_{user_id}",
                        password="testpassword"
                    )
                    users_created += 1
                    
                    # 每个用户创建5个会话
                    for j in range(5):
                        conv_id = Conversations.add_conversation(
                            user_id=user_id,
                            conv_name=f"会话_{j}"
                        )
                        conversations_created += 1
                
                return {
                    "success": True,
                    "users_created": users_created,
                    "conversations_created": conversations_created
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        start_time = time.time()
        result = create_large_dataset()
        total_time = time.time() - start_time
        
        # 验证大数据集创建
        assert result["success"], f"大数据集创建失败: {result.get('error', 'Unknown error')}"
        assert result["users_created"] == 100, f"用户创建数量不正确: {result['users_created']}"
        assert result["conversations_created"] == 500, f"会话创建数量不正确: {result['conversations_created']}"
        assert total_time < 60.0, f"大数据集创建时间过长: {total_time:.2f}秒"


# Locust性能测试类
class ChatUser(HttpUser):
    """Locust用户类 - 模拟聊天用户行为"""
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户开始时的操作"""
        # 模拟登录
        self.client.get("/login")
    
    @task(3)
    def send_chat_message(self):
        """发送聊天消息 - 权重3"""
        message_data = {
            "messages": [
                {"role": "user", "content": "这是一个性能测试消息"}
            ],
            "session_id": f"locust_session_{self.user_id}",
            "personality_id": "test_personality",
            "message_id": f"locust_message_{int(time.time() * 1000)}",
            "role": "assistant"
        }
        
        with self.client.post("/stream", json=message_data, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")
    
    @task(1)
    def create_session(self):
        """创建新会话 - 权重1"""
        session_data = {"conv_name": f"Locust会话_{int(time.time())}"}
        
        with self.client.post("/api/sessions", json=session_data, catch_response=True) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Session creation failed: {response.status_code}")
    
    @task(1)
    def get_sessions(self):
        """获取会话列表 - 权重1"""
        with self.client.get("/api/sessions", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Get sessions failed: {response.status_code}")


class TestPerformanceBenchmarks:
    """性能基准测试类"""
    
    def test_response_time_benchmark(self, test_app):
        """响应时间基准测试"""
        response_times = []
        
        # 发送100个请求测量响应时间
        for _ in range(100):
            start_time = time.time()
            response = test_app.get('/')
            response_time = time.time() - start_time
            response_times.append(response_time)
        
        # 计算统计信息
        avg_response_time = statistics.mean(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        p99_response_time = sorted(response_times)[int(len(response_times) * 0.99)]
        
        # 基准断言
        assert avg_response_time < 0.5, f"平均响应时间超过基准: {avg_response_time:.3f}秒"
        assert p95_response_time < 1.0, f"95%响应时间超过基准: {p95_response_time:.3f}秒"
        assert p99_response_time < 2.0, f"99%响应时间超过基准: {p99_response_time:.3f}秒"
    
    def test_throughput_benchmark(self, test_app):
        """吞吐量基准测试"""
        start_time = time.time()
        request_count = 1000
        
        # 发送大量请求
        for _ in range(request_count):
            test_app.get('/')
        
        total_time = time.time() - start_time
        throughput = request_count / total_time
        
        # 吞吐量基准断言
        assert throughput >= 100, f"吞吐量低于基准: {throughput:.2f} req/sec"
    
    def test_memory_usage_benchmark(self, test_app, memory_profiler):
        """内存使用基准测试"""
        profiler = memory_profiler
        
        # 执行一些操作
        for _ in range(100):
            test_app.get('/')
        
        memory_used = profiler()
        
        # 内存使用基准断言
        assert memory_used < 50 * 1024 * 1024, f"内存使用超过基准: {memory_used / 1024 / 1024:.2f} MB"
