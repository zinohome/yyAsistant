from models.conversations import Conversations
from models.exceptions import InvalidConversationError, ExistingConversationError


def main():
    """主函数：创建几个用户id为zhangjun的会话"""
    try:
        # 创建第一个会话，使用默认名称
        conv_id1 = Conversations.add_conversation(user_id="zhangjun")
        print(f"创建会话成功，会话ID: {conv_id1}")
        
        # 创建第二个会话，指定名称
        conv_id2 = Conversations.add_conversation(
            user_id="zhangjun", 
            conv_name="工作会话"
        )
        print(f"创建会话成功，会话ID: {conv_id2}")
        
        # 创建第三个会话，指定名称和记忆内容
        conv_id3 = Conversations.add_conversation(
            user_id="zhangjun",
            conv_name="学习笔记",
            conv_memory={"tags": ["学习", "笔记"], "priority": "high"}
        )
        print(f"创建会话成功，会话ID: {conv_id3}")
        
        # 查询并显示已创建的会话
        user_convs = Conversations.get_user_conversations(user_id="zhangjun")
        print(f"\n用户zhangjun的会话列表: {user_convs}")
        
        # 可选：测试更新会话功能
        updated_conv = Conversations.update_conversation_by_conv_id(
            conv_id=conv_id2,
            conv_name="重要工作会话",
            conv_memory={"project": "AI助手开发"}
        )
        print(f"\n更新后的会话信息: {updated_conv}")
        
    except InvalidConversationError as e:
        print(f"无效的会话数据: {e}")
    except ExistingConversationError as e:
        print(f"会话已存在: {e}")
    except Exception as e:
        print(f"创建会话时发生错误: {e}")


if __name__ == "__main__":
    main()