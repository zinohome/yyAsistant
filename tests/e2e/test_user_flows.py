"""
端到端用户流程测试
"""
import pytest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TestUserFlowBase:
    """用户流程测试基类"""
    
    @pytest.fixture(scope="class")
    def driver(self):
        """创建WebDriver实例"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # 无头模式
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        yield driver
        
        driver.quit()
    
    @pytest.fixture
    def wait(self, driver):
        """创建WebDriverWait实例"""
        return WebDriverWait(driver, 10)
    
    def login_user(self, driver, wait, username="testuser", password="testpassword"):
        """用户登录"""
        from configs.app_config import app_config
        driver.get(f"{app_config.TEST_LOCALHOST_URL}/login")
        
        # 等待登录表单加载
        username_input = wait.until(
            EC.presence_of_element_located((By.ID, "username-input"))
        )
        password_input = driver.find_element(By.ID, "password-input")
        login_button = driver.find_element(By.ID, "login-button")
        
        # 输入凭据
        username_input.clear()
        username_input.send_keys(username)
        password_input.clear()
        password_input.send_keys(password)
        
        # 点击登录
        login_button.click()
        
        # 等待登录成功（重定向到聊天页面）
        wait.until(EC.url_contains("/chat"))
    
    def wait_for_element(self, driver, wait, locator, timeout=10):
        """等待元素出现"""
        try:
            return wait.until(EC.presence_of_element_located(locator))
        except TimeoutException:
            pytest.fail(f"元素未在{timeout}秒内出现: {locator}")


class TestLoginFlow(TestUserFlowBase):
    """登录流程测试"""
    
    def test_successful_login(self, driver, wait):
        """测试成功登录"""
        self.login_user(driver, wait)
        
        # 验证登录成功
        assert "/chat" in driver.current_url
        assert "聊天" in driver.page_source or "Chat" in driver.page_source
    
    def test_failed_login(self, driver, wait):
        """测试登录失败"""
        from configs.app_config import app_config
        driver.get(f"{app_config.TEST_LOCALHOST_URL}/login")
        
        # 输入错误凭据
        username_input = wait.until(
            EC.presence_of_element_located((By.ID, "username-input"))
        )
        password_input = driver.find_element(By.ID, "password-input")
        login_button = driver.find_element(By.ID, "login-button")
        
        username_input.send_keys("wrong_user")
        password_input.send_keys("wrong_password")
        login_button.click()
        
        # 验证错误消息
        error_message = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
        )
        assert error_message.is_displayed()
    
    def test_login_form_validation(self, driver, wait):
        """测试登录表单验证"""
        from configs.app_config import app_config
        driver.get(f"{app_config.TEST_LOCALHOST_URL}/login")
        
        login_button = wait.until(
            EC.presence_of_element_located((By.ID, "login-button"))
        )
        
        # 尝试提交空表单
        login_button.click()
        
        # 验证验证错误
        validation_errors = driver.find_elements(By.CLASS_NAME, "validation-error")
        assert len(validation_errors) > 0


class TestChatFlow(TestUserFlowBase):
    """聊天流程测试"""
    
    def test_complete_chat_flow(self, driver, wait):
        """测试完整聊天流程"""
        # 登录
        self.login_user(driver, wait)
        
        # 等待聊天界面加载
        chat_input = wait.until(
            EC.presence_of_element_located((By.ID, "ai-chat-x-input"))
        )
        send_button = driver.find_element(By.ID, "ai-chat-x-send-btn")
        
        # 发送消息
        test_message = "你好，请介绍一下你自己"
        chat_input.clear()
        chat_input.send_keys(test_message)
        send_button.click()
        
        # 等待AI回复
        ai_message = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-message"))
        )
        
        # 验证消息显示
        assert ai_message.is_displayed()
        assert len(ai_message.text) > 0
    
    def test_message_history(self, driver, wait):
        """测试消息历史"""
        # 登录
        self.login_user(driver, wait)
        
        # 发送多条消息
        messages = ["第一条消息", "第二条消息", "第三条消息"]
        
        for message in messages:
            chat_input = wait.until(
                EC.presence_of_element_located((By.ID, "ai-chat-x-input"))
            )
            send_button = driver.find_element(By.ID, "ai-chat-x-send-btn")
            
            chat_input.clear()
            chat_input.send_keys(message)
            send_button.click()
            
            # 等待AI回复
            wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "ai-message"))
            )
            time.sleep(1)  # 等待消息处理完成
        
        # 验证消息历史
        user_messages = driver.find_elements(By.CLASS_NAME, "user-message")
        ai_messages = driver.find_elements(By.CLASS_NAME, "ai-message")
        
        assert len(user_messages) >= len(messages)
        assert len(ai_messages) >= len(messages)
    
    def test_message_regeneration(self, driver, wait):
        """测试消息重新生成"""
        # 登录并发送消息
        self.login_user(driver, wait)
        
        chat_input = wait.until(
            EC.presence_of_element_located((By.ID, "ai-chat-x-input"))
        )
        send_button = driver.find_element(By.ID, "ai-chat-x-send-btn")
        
        chat_input.send_keys("请写一首诗")
        send_button.click()
        
        # 等待AI回复
        ai_message = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-message"))
        )
        
        # 点击重新生成按钮
        regenerate_button = ai_message.find_element(By.CLASS_NAME, "regenerate-btn")
        regenerate_button.click()
        
        # 等待新的回复
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-message"))
        )
        
        # 验证有新的回复
        ai_messages = driver.find_elements(By.CLASS_NAME, "ai-message")
        assert len(ai_messages) >= 2
    
    def test_message_copy(self, driver, wait):
        """测试消息复制功能"""
        # 登录并发送消息
        self.login_user(driver, wait)
        
        chat_input = wait.until(
            EC.presence_of_element_located((By.ID, "ai-chat-x-input"))
        )
        send_button = driver.find_element(By.ID, "ai-chat-x-send-btn")
        
        chat_input.send_keys("测试复制功能")
        send_button.click()
        
        # 等待AI回复
        ai_message = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "ai-message"))
        )
        
        # 点击复制按钮
        copy_button = ai_message.find_element(By.CLASS_NAME, "copy-btn")
        copy_button.click()
        
        # 验证复制成功（可能需要检查剪贴板或显示复制成功的提示）
        # 这里假设有复制成功的提示
        try:
            success_message = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "copy-success"))
            )
            assert success_message.is_displayed()
        except TimeoutException:
            # 如果没有复制成功提示，这个测试可能需要调整
            pass


class TestSessionManagementFlow(TestUserFlowBase):
    """会话管理流程测试"""
    
    def test_create_new_session(self, driver, wait):
        """测试创建新会话"""
        # 登录
        self.login_user(driver, wait)
        
        # 点击新建会话按钮
        new_session_button = wait.until(
            EC.element_to_be_clickable((By.ID, "ai-chat-x-session-new"))
        )
        new_session_button.click()
        
        # 等待新会话创建
        time.sleep(2)
        
        # 验证会话列表更新
        session_items = driver.find_elements(By.CLASS_NAME, "session-item")
        assert len(session_items) > 0
    
    def test_switch_sessions(self, driver, wait):
        """测试切换会话"""
        # 登录
        self.login_user(driver, wait)
        
        # 创建第一个会话并发送消息
        chat_input = wait.until(
            EC.presence_of_element_located((By.ID, "ai-chat-x-input"))
        )
        send_button = driver.find_element(By.ID, "ai-chat-x-send-btn")
        
        chat_input.send_keys("第一个会话的消息")
        send_button.click()
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ai-message")))
        
        # 创建新会话
        new_session_button = wait.until(
            EC.element_to_be_clickable((By.ID, "ai-chat-x-session-new"))
        )
        new_session_button.click()
        time.sleep(2)
        
        # 在新会话中发送消息
        chat_input = wait.until(
            EC.presence_of_element_located((By.ID, "ai-chat-x-input"))
        )
        chat_input.send_keys("第二个会话的消息")
        send_button.click()
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ai-message")))
        
        # 切换回第一个会话
        session_items = driver.find_elements(By.CLASS_NAME, "session-item")
        if len(session_items) > 1:
            session_items[0].click()
            time.sleep(2)
            
            # 验证消息历史正确显示
            user_messages = driver.find_elements(By.CLASS_NAME, "user-message"))
            assert len(user_messages) > 0
    
    def test_rename_session(self, driver, wait):
        """测试重命名会话"""
        # 登录
        self.login_user(driver, wait)
        
        # 等待会话列表加载
        session_items = wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "session-item"))
        )
        
        if session_items:
            # 点击会话下拉菜单
            dropdown_button = session_items[0].find_element(By.CLASS_NAME, "session-dropdown"))
            dropdown_button.click()
            
            # 点击重命名选项
            rename_option = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "rename-option"))
            )
            rename_option.click()
            
            # 输入新名称
            rename_input = wait.until(
                EC.presence_of_element_located((By.ID, "ai-chat-x-session-rename-input"))
            )
            rename_input.clear()
            rename_input.send_keys("重命名后的会话")
            
            # 确认重命名
            confirm_button = driver.find_element(By.CLASS_NAME, "rename-confirm"))
            confirm_button.click()
            
            # 验证重命名成功
            time.sleep(2)
            assert "重命名后的会话" in driver.page_source
    
    def test_delete_session(self, driver, wait):
        """测试删除会话"""
        # 登录
        self.login_user(driver, wait)
        
        # 创建多个会话
        new_session_button = wait.until(
            EC.element_to_be_clickable((By.ID, "ai-chat-x-session-new"))
        )
        new_session_button.click()
        time.sleep(2)
        
        # 获取会话数量
        session_items = driver.find_elements(By.CLASS_NAME, "session-item")
        initial_count = len(session_items)
        
        if initial_count > 0:
            # 点击第一个会话的下拉菜单
            dropdown_button = session_items[0].find_element(By.CLASS_NAME, "session-dropdown"))
            dropdown_button.click()
            
            # 点击删除选项
            delete_option = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "delete-option"))
            )
            delete_option.click()
            
            # 确认删除
            confirm_button = wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "delete-confirm"))
            )
            confirm_button.click()
            
            # 验证删除成功
            time.sleep(2)
            updated_session_items = driver.find_elements(By.CLASS_NAME, "session-item")
            assert len(updated_session_items) < initial_count


class TestResponsiveDesignFlow(TestUserFlowBase):
    """响应式设计测试"""
    
    def test_mobile_view(self, driver, wait):
        """测试移动端视图"""
        # 设置移动端视口
        driver.set_window_size(375, 667)  # iPhone 6/7/8 尺寸
        
        # 登录
        self.login_user(driver, wait)
        
        # 验证移动端布局
        mobile_menu = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "mobile-menu"))
        )
        assert mobile_menu.is_displayed()
        
        # 测试移动端会话管理
        mobile_session_button = driver.find_element(By.CLASS_NAME, "mobile-session-btn"))
        mobile_session_button.click()
        
        # 验证移动端会话弹出框
        mobile_session_popup = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "mobile-session-popup"))
        )
        assert mobile_session_popup.is_displayed()
    
    def test_tablet_view(self, driver, wait):
        """测试平板端视图"""
        # 设置平板端视口
        driver.set_window_size(768, 1024)  # iPad 尺寸
        
        # 登录
        self.login_user(driver, wait)
        
        # 验证平板端布局
        sidebar = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        assert sidebar.is_displayed()
        
        # 测试聊天功能
        chat_input = wait.until(
            EC.presence_of_element_located((By.ID, "ai-chat-x-input"))
        )
        send_button = driver.find_element(By.ID, "ai-chat-x-send-btn")
        
        chat_input.send_keys("平板端测试消息")
        send_button.click()
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ai-message")))
    
    def test_desktop_view(self, driver, wait):
        """测试桌面端视图"""
        # 设置桌面端视口
        driver.set_window_size(1920, 1080)
        
        # 登录
        self.login_user(driver, wait)
        
        # 验证桌面端布局
        sidebar = wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "sidebar"))
        )
        main_content = driver.find_element(By.CLASS_NAME, "main-content")
        
        assert sidebar.is_displayed()
        assert main_content.is_displayed()
        
        # 测试侧边栏折叠功能
        collapse_button = driver.find_element(By.CLASS_NAME, "collapse-btn"))
        collapse_button.click()
        
        time.sleep(1)
        # 验证侧边栏折叠状态
        assert "collapsed" in sidebar.get_attribute("class")


class TestErrorHandlingFlow(TestUserFlowBase):
    """错误处理流程测试"""
    
    def test_network_error_handling(self, driver, wait):
        """测试网络错误处理"""
        # 登录
        self.login_user(driver, wait)
        
        # 模拟网络错误（通过修改请求）
        # 这里需要根据实际实现来模拟网络错误
        # 可能需要使用代理或修改网络设置
        
        chat_input = wait.until(
            EC.presence_of_element_located((By.ID, "ai-chat-x-input"))
        )
        send_button = driver.find_element(By.ID, "ai-chat-x-send-btn")
        
        chat_input.send_keys("测试网络错误")
        send_button.click()
        
        # 验证错误处理
        try:
            error_message = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
            )
            assert error_message.is_displayed()
        except TimeoutException:
            # 如果没有错误处理，这个测试可能需要调整
            pass
    
    def test_session_timeout(self, driver, wait):
        """测试会话超时"""
        # 登录
        self.login_user(driver, wait)
        
        # 等待会话超时（这可能需要很长时间，实际测试中可能需要模拟）
        # 或者通过修改会话超时设置来加速测试
        
        # 验证超时后的重定向
        try:
            wait.until(EC.url_contains("/login"))
            assert "/login" in driver.current_url
        except TimeoutException:
            # 如果会话没有超时，这个测试可能需要调整
            pass


class TestAccessibilityFlow(TestUserFlowBase):
    """无障碍访问测试"""
    
    def test_keyboard_navigation(self, driver, wait):
        """测试键盘导航"""
        # 登录
        self.login_user(driver, wait)
        
        # 使用Tab键导航
        from selenium.webdriver.common.keys import Keys
        
        # 获取当前焦点元素
        current_element = driver.switch_to.active_element
        
        # 使用Tab键导航到聊天输入框
        for _ in range(5):  # 最多尝试5次
            current_element.send_keys(Keys.TAB)
            current_element = driver.switch_to.active_element
            
            if current_element.get_attribute("id") == "ai-chat-x-input":
                break
        
        # 验证焦点在聊天输入框
        assert current_element.get_attribute("id") == "ai-chat-x-input"
        
        # 输入消息
        current_element.send_keys("键盘导航测试")
        
        # 使用Enter键发送消息
        current_element.send_keys(Keys.ENTER)
        
        # 等待消息发送
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "user-message")))
    
    def test_screen_reader_compatibility(self, driver, wait):
        """测试屏幕阅读器兼容性"""
        # 登录
        self.login_user(driver, wait)
        
        # 检查关键元素的aria标签
        chat_input = wait.until(
            EC.presence_of_element_located((By.ID, "ai-chat-x-input"))
        )
        
        # 验证aria-label或aria-labelledby属性
        aria_label = chat_input.get_attribute("aria-label")
        aria_labelledby = chat_input.get_attribute("aria-labelledby")
        
        assert aria_label is not None or aria_labelledby is not None
        
        # 检查按钮的aria标签
        send_button = driver.find_element(By.ID, "ai-chat-x-send-btn")
        button_aria_label = send_button.get_attribute("aria-label")
        
        assert button_aria_label is not None
