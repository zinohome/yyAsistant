"""
话题配置管理工具
提供话题配置的增删改查功能
"""
import json
import os
from typing import List, Dict, Any, Optional
from configs.topics_loader import get_topics_loader, clear_topics_cache


class TopicsManager:
    """话题配置管理器"""
    
    def __init__(self):
        self.loader = get_topics_loader()
        self.config_path = self.loader.config_path
    
    def add_topic(self, topic: Dict[str, Any]) -> bool:
        """
        添加新话题
        
        Args:
            topic: 话题字典，必须包含id, title, icon等字段
            
        Returns:
            是否添加成功
        """
        try:
            config = self.loader.get_config(force_reload=True)
            topics = config.get('topics', [])
            
            # 检查ID是否已存在
            if any(t.get('id') == topic.get('id') for t in topics):
                print(f"话题ID '{topic.get('id')}' 已存在")
                return False
            
            # 添加新话题
            topics.append(topic)
            config['topics'] = topics
            
            # 保存到文件
            self._save_config(config)
            clear_topics_cache()
            print(f"成功添加话题: {topic.get('title')}")
            return True
            
        except Exception as e:
            print(f"添加话题失败: {e}")
            return False
    
    def update_topic(self, topic_id: str, updates: Dict[str, Any]) -> bool:
        """
        更新话题
        
        Args:
            topic_id: 话题ID
            updates: 要更新的字段
            
        Returns:
            是否更新成功
        """
        try:
            config = self.loader.get_config(force_reload=True)
            topics = config.get('topics', [])
            
            # 查找话题
            for i, topic in enumerate(topics):
                if topic.get('id') == topic_id:
                    # 更新话题
                    topics[i].update(updates)
                    config['topics'] = topics
                    
                    # 保存到文件
                    self._save_config(config)
                    clear_topics_cache()
                    print(f"成功更新话题: {topic_id}")
                    return True
            
            print(f"未找到话题ID: {topic_id}")
            return False
            
        except Exception as e:
            print(f"更新话题失败: {e}")
            return False
    
    def delete_topic(self, topic_id: str) -> bool:
        """
        删除话题
        
        Args:
            topic_id: 话题ID
            
        Returns:
            是否删除成功
        """
        try:
            config = self.loader.get_config(force_reload=True)
            topics = config.get('topics', [])
            
            # 查找并删除话题
            original_length = len(topics)
            topics = [t for t in topics if t.get('id') != topic_id]
            
            if len(topics) == original_length:
                print(f"未找到话题ID: {topic_id}")
                return False
            
            config['topics'] = topics
            
            # 保存到文件
            self._save_config(config)
            clear_topics_cache()
            print(f"成功删除话题: {topic_id}")
            return True
            
        except Exception as e:
            print(f"删除话题失败: {e}")
            return False
    
    def reorder_topics(self, topic_ids: List[str]) -> bool:
        """
        重新排序话题
        
        Args:
            topic_ids: 按新顺序排列的话题ID列表
            
        Returns:
            是否重排序成功
        """
        try:
            config = self.loader.get_config(force_reload=True)
            topics = config.get('topics', [])
            
            # 创建ID到话题的映射
            topic_map = {t.get('id'): t for t in topics}
            
            # 按新顺序重新排列
            new_topics = []
            for topic_id in topic_ids:
                if topic_id in topic_map:
                    new_topics.append(topic_map[topic_id])
            
            # 添加未在列表中的话题（保持原有顺序）
            for topic in topics:
                if topic.get('id') not in topic_ids:
                    new_topics.append(topic)
            
            config['topics'] = new_topics
            
            # 保存到文件
            self._save_config(config)
            clear_topics_cache()
            print("成功重新排序话题")
            return True
            
        except Exception as e:
            print(f"重新排序话题失败: {e}")
            return False
    
    def get_topic(self, topic_id: str) -> Optional[Dict[str, Any]]:
        """
        获取话题详情
        
        Args:
            topic_id: 话题ID
            
        Returns:
            话题字典，如果不存在返回None
        """
        return self.loader.get_topic_by_id(topic_id)
    
    def list_topics(self) -> List[Dict[str, Any]]:
        """
        获取所有话题列表
        
        Returns:
            话题列表
        """
        return self.loader.get_topics()
    
    def export_config(self, export_path: str) -> bool:
        """
        导出配置到文件
        
        Args:
            export_path: 导出文件路径
            
        Returns:
            是否导出成功
        """
        try:
            config = self.loader.get_config(force_reload=True)
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            print(f"配置已导出到: {export_path}")
            return True
        except Exception as e:
            print(f"导出配置失败: {e}")
            return False
    
    def import_config(self, import_path: str) -> bool:
        """
        从文件导入配置
        
        Args:
            import_path: 导入文件路径
            
        Returns:
            是否导入成功
        """
        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 验证配置格式
            if not self._validate_config(config):
                print("配置格式验证失败")
                return False
            
            # 备份原配置
            backup_path = self.config_path + '.backup'
            if os.path.exists(self.config_path):
                import shutil
                shutil.copy2(self.config_path, backup_path)
                print(f"原配置已备份到: {backup_path}")
            
            # 保存新配置
            self._save_config(config)
            clear_topics_cache()
            print(f"配置已从 {import_path} 导入")
            return True
            
        except Exception as e:
            print(f"导入配置失败: {e}")
            return False
    
    def _save_config(self, config: Dict[str, Any]) -> None:
        """保存配置到文件"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """验证配置格式"""
        required_keys = ['topics', 'categories', 'settings']
        if not all(key in config for key in required_keys):
            return False
        
        # 验证topics格式
        topics = config.get('topics', [])
        if not isinstance(topics, list):
            return False
        
        for topic in topics:
            if not isinstance(topic, dict):
                return False
            if not all(key in topic for key in ['id', 'title', 'icon']):
                return False
        
        return True


# 便捷函数
def add_topic(topic: Dict[str, Any]) -> bool:
    """添加话题"""
    manager = TopicsManager()
    return manager.add_topic(topic)


def update_topic(topic_id: str, updates: Dict[str, Any]) -> bool:
    """更新话题"""
    manager = TopicsManager()
    return manager.update_topic(topic_id, updates)


def delete_topic(topic_id: str) -> bool:
    """删除话题"""
    manager = TopicsManager()
    return manager.delete_topic(topic_id)


def list_topics() -> List[Dict[str, Any]]:
    """获取话题列表"""
    manager = TopicsManager()
    return manager.list_topics()


def get_topic(topic_id: str) -> Optional[Dict[str, Any]]:
    """获取话题详情"""
    manager = TopicsManager()
    return manager.get_topic(topic_id)


if __name__ == "__main__":
    # 示例用法
    manager = TopicsManager()
    
    # 列出所有话题
    print("当前话题列表:")
    for topic in manager.list_topics():
        print(f"- {topic['id']}: {topic['title']}")
    
    # 添加新话题示例
    # new_topic = {
    #     "id": "new_topic",
    #     "title": "新话题",
    #     "description": "这是一个新话题",
    #     "icon": "fluent-mdl2:new-item",
    #     "category": "other"
    # }
    # manager.add_topic(new_topic)
