"""
话题配置加载器
支持JSON配置文件动态加载，带缓存和性能优化
"""
import json
import os
import time
from typing import List, Dict, Any, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)


class TopicsConfigLoader:
    """话题配置加载器，支持缓存和性能优化"""
    
    def __init__(self, config_path: str = None):
        """
        初始化配置加载器
        
        Args:
            config_path: 配置文件路径，默认为configs/topics_config.json
        """
        if config_path is None:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(current_dir, 'topics_config.json')
        
        self.config_path = config_path
        self._config_cache = None
        self._last_modified = 0
        self._cache_duration = 300  # 默认缓存5分钟
        
    def _load_config_from_file(self) -> Dict[str, Any]:
        """从文件加载配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.debug(f"成功加载话题配置文件: {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"话题配置文件不存在: {self.config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            logger.error(f"话题配置文件JSON格式错误: {e}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"加载话题配置文件失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "topics": [
                {
                    "id": "health_wellness",
                    "title": "健康养生",
                    "description": "我最近身体有些不适，想了解一下日常保健的方法，比如饮食调理和运动锻炼方面有什么建议？",
                    "icon": "fluent-mdl2:health",
                    "category": "health"
                },
                {
                    "id": "mental_health",
                    "title": "心理健康",
                    "description": "退休后感觉心理状态有些变化，有时候会感到孤独或者焦虑，有什么好的情绪管理方法吗？",
                    "icon": "fluent-mdl2:brain-circuit",
                    "category": "health"
                },
                {
                    "id": "chronic_disease_management",
                    "title": "慢性病管理",
                    "description": "我有高血压/糖尿病等慢性病，想了解一下日常护理和饮食注意事项，有什么好的建议？",
                    "icon": "fluent-mdl2:heart-pulse",
                    "category": "health"
                },
                {
                    "id": "sleep_health",
                    "title": "睡眠健康",
                    "description": "最近睡眠质量不太好，经常失眠或者早醒，有什么改善睡眠的方法吗？",
                    "icon": "fluent-mdl2:sleep",
                    "category": "health"
                },
                {
                    "id": "nutrition_diet",
                    "title": "营养饮食",
                    "description": "想了解一下适合我们老年人的营养搭配，有什么推荐的食谱和饮食原则吗？",
                    "icon": "fluent-mdl2:food",
                    "category": "health"
                },
                {
                    "id": "exercise_fitness",
                    "title": "运动健身",
                    "description": "退休后想保持身体健康，有什么适合我们老年人的运动方式和健身计划吗？",
                    "icon": "fluent-mdl2:exercise-tracker",
                    "category": "health"
                },
                {
                    "id": "medical_checkup",
                    "title": "体检保健",
                    "description": "想了解一下老年人应该做哪些定期体检，有什么需要注意的检查项目吗？",
                    "icon": "fluent-mdl2:medical",
                    "category": "health"
                },
                {
                    "id": "medication_management",
                    "title": "用药管理",
                    "description": "平时需要服用多种药物，担心药物相互作用，有什么安全用药的建议吗？",
                    "icon": "fluent-mdl2:pills",
                    "category": "health"
                },
                {
                    "id": "memoir_writing",
                    "title": "回忆录撰写",
                    "description": "我想把自己的工作经历和人生感悟记录下来，但不知道从何开始，能给我一些建议吗？",
                    "icon": "fluent-mdl2:edit",
                    "category": "life"
                },
                {
                    "id": "family_relationships",
                    "title": "家庭关系",
                    "description": "和子女、孙辈相处时总感觉有代沟，不知道如何更好地沟通，有什么好的建议吗？",
                    "icon": "fluent-mdl2:family",
                    "category": "life"
                },
                {
                    "id": "life_planning",
                    "title": "生活规划",
                    "description": "退休后时间比较充裕，但不知道如何合理安排，有什么好的生活规划建议吗？",
                    "icon": "fluent-mdl2:calendar",
                    "category": "life"
                },
                {
                    "id": "hobby_development",
                    "title": "兴趣爱好",
                    "description": "退休后想培养一些兴趣爱好，比如书法、绘画、园艺、音乐等，有什么好的建议吗？",
                    "icon": "fluent-mdl2:palette",
                    "category": "life"
                },
                {
                    "id": "travel_planning",
                    "title": "旅行规划",
                    "description": "想出去旅游放松一下，但担心身体和安全问题，有什么适合老年人的旅游建议吗？",
                    "icon": "fluent-mdl2:airplane",
                    "category": "life"
                },
                {
                    "id": "home_safety",
                    "title": "居家安全",
                    "description": "年纪大了，担心在家里的安全问题，有什么居家安全防护的建议吗？",
                    "icon": "fluent-mdl2:security",
                    "category": "life"
                },
                {
                    "id": "daily_routine",
                    "title": "日常作息",
                    "description": "退休后生活节奏改变了，想建立良好的日常作息习惯，有什么好的建议吗？",
                    "icon": "fluent-mdl2:clock",
                    "category": "life"
                },
                {
                    "id": "emotional_support",
                    "title": "情感支持",
                    "description": "有时候感到孤独或者情绪低落，有什么好的情感调节和寻求支持的方法吗？",
                    "icon": "fluent-mdl2:heart",
                    "category": "life"
                },
                {
                    "id": "new_skills",
                    "title": "学习新技能",
                    "description": "退休后想学一些新技能，比如使用智能手机、电脑操作，或者书法绘画，有什么适合我们老年人的学习方式？",
                    "icon": "fluent-mdl2:learning-tools",
                    "category": "learning"
                },
                {
                    "id": "technology_learning",
                    "title": "科技学习",
                    "description": "想学习使用智能手机、电脑、平板等电子设备，但觉得太复杂，有什么简单易懂的学习方法吗？",
                    "icon": "fluent-mdl2:laptop",
                    "category": "learning"
                },
                {
                    "id": "language_learning",
                    "title": "语言学习",
                    "description": "想学习一门外语，比如英语或者其他语言，有什么适合老年人的学习方法吗？",
                    "icon": "fluent-mdl2:translate",
                    "category": "learning"
                },
                {
                    "id": "art_culture",
                    "title": "文化艺术",
                    "description": "对书法、绘画、音乐、戏曲等文化艺术很感兴趣，想深入学习，有什么好的建议吗？",
                    "icon": "fluent-mdl2:paint-brush",
                    "category": "learning"
                },
                {
                    "id": "financial_management",
                    "title": "理财规划",
                    "description": "退休后的收入有限，想了解一下如何合理理财，有什么适合老年人的理财方式吗？",
                    "icon": "fluent-mdl2:money",
                    "category": "learning"
                },
                {
                    "id": "internet_safety",
                    "title": "网络安全",
                    "description": "想学习上网，但担心遇到网络诈骗，有什么网络安全防护的知识可以学习吗？",
                    "icon": "fluent-mdl2:shield",
                    "category": "learning"
                },
                {
                    "id": "health_knowledge",
                    "title": "健康知识",
                    "description": "想学习一些基本的健康知识，了解常见疾病的预防和护理，有什么好的学习资源吗？",
                    "icon": "fluent-mdl2:book",
                    "category": "learning"
                },
                {
                    "id": "digital_life",
                    "title": "数字生活",
                    "description": "想学习使用各种手机应用，比如微信、支付宝、网上购物等，有什么简单易懂的教程吗？",
                    "icon": "fluent-mdl2:smartphone",
                    "category": "learning"
                },
                {
                    "id": "social_participation",
                    "title": "社会参与",
                    "description": "退休后想参加一些社会活动，比如社区服务或者老年大学，有什么好的建议和途径？",
                    "icon": "fluent-mdl2:people",
                    "category": "social"
                },
                {
                    "id": "volunteer_work",
                    "title": "志愿服务",
                    "description": "想做一些志愿服务工作，为社会贡献自己的力量，有什么适合的志愿服务机会吗？",
                    "icon": "fluent-mdl2:handshake",
                    "category": "social"
                },
                {
                    "id": "community_activities",
                    "title": "社区活动",
                    "description": "想参加社区组织的各种活动，比如广场舞、太极拳、合唱团等，有什么好的建议吗？",
                    "icon": "fluent-mdl2:community",
                    "category": "social"
                },
                {
                    "id": "peer_communication",
                    "title": "同龄交流",
                    "description": "想多和同龄人交流，分享退休后的生活经验和感受，有什么好的交流平台或方式吗？",
                    "icon": "fluent-mdl2:chat",
                    "category": "social"
                },
                {
                    "id": "mentoring_guidance",
                    "title": "经验传承",
                    "description": "想把自己的工作经验传授给年轻人，或者指导后辈，有什么好的方式和方法吗？",
                    "icon": "fluent-mdl2:graduation-cap",
                    "category": "social"
                },
                {
                    "id": "community_leadership",
                    "title": "社区领导",
                    "description": "想在社区中发挥更多作用，参与社区管理和决策，有什么好的途径和建议吗？",
                    "icon": "fluent-mdl2:leaderboard",
                    "category": "social"
                },
                {
                    "id": "cultural_activities",
                    "title": "文化活动",
                    "description": "想参加一些文化活动，比如读书会、文化讲座、艺术展览等，有什么好的推荐吗？",
                    "icon": "fluent-mdl2:culture",
                    "category": "social"
                },
                {
                    "id": "intergenerational_exchange",
                    "title": "代际交流",
                    "description": "想和年轻人多交流，了解他们的想法，也分享我们的经验，有什么好的交流平台吗？",
                    "icon": "fluent-mdl2:conversation",
                    "category": "social"
                }
            ],
            "categories": {
                "health": {"name": "健康管理", "color": "#52c41a", "icon": "fluent-mdl2:health"},
                "life": {"name": "生活指导", "color": "#1890ff", "icon": "fluent-mdl2:home"},
                "learning": {"name": "学习成长", "color": "#fa8c16", "icon": "fluent-mdl2:learning-tools"},
                "social": {"name": "社会参与", "color": "#722ed1", "icon": "fluent-mdl2:people"}
            },
            "settings": {
                "max_topics_display": 4,
                "enable_categories": True,
                "enable_descriptions": False,
                "cache_duration": 300
            }
        }
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if self._config_cache is None:
            return False
        
        # 检查文件是否被修改
        try:
            current_modified = os.path.getmtime(self.config_path)
            if current_modified != self._last_modified:
                return False
        except OSError:
            return False
        
        # 检查缓存是否过期
        if time.time() - self._last_modified > self._cache_duration:
            return False
        
        return True
    
    def get_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        获取配置，支持缓存
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            配置字典
        """
        if force_reload or not self._is_cache_valid():
            self._config_cache = self._load_config_from_file()
            self._last_modified = time.time()
            
            # 更新缓存持续时间
            if self._config_cache and 'settings' in self._config_cache:
                self._cache_duration = self._config_cache['settings'].get('cache_duration', 300)
        
        return self._config_cache or self._get_default_config()
    
    def get_topics(self, force_reload: bool = False) -> List[Dict[str, Any]]:
        """
        获取话题列表
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            话题列表
        """
        config = self.get_config(force_reload)
        return config.get('topics', [])
    
    def get_topic_titles(self, force_reload: bool = False) -> List[str]:
        """
        获取话题标题列表（向后兼容）
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            话题标题列表
        """
        topics = self.get_topics(force_reload)
        return [topic.get('title', '') for topic in topics]
    
    def get_topic_icons(self, force_reload: bool = False) -> List[str]:
        """
        获取话题图标列表（向后兼容）
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            话题图标列表
        """
        topics = self.get_topics(force_reload)
        return [topic.get('icon', '') for topic in topics]
    
    def get_topic_by_id(self, topic_id: str, force_reload: bool = False) -> Optional[Dict[str, Any]]:
        """
        根据ID获取话题
        
        Args:
            topic_id: 话题ID
            force_reload: 是否强制重新加载
            
        Returns:
            话题字典，如果不存在返回None
        """
        topics = self.get_topics(force_reload)
        for topic in topics:
            if topic.get('id') == topic_id:
                return topic
        return None
    
    def get_topics_by_category(self, category: str, force_reload: bool = False) -> List[Dict[str, Any]]:
        """
        根据分类获取话题
        
        Args:
            category: 分类名称
            force_reload: 是否强制重新加载
            
        Returns:
            该分类下的话题列表
        """
        topics = self.get_topics(force_reload)
        return [topic for topic in topics if topic.get('category') == category]
    
    def get_categories(self, force_reload: bool = False) -> Dict[str, Dict[str, str]]:
        """
        获取分类信息
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            分类字典
        """
        config = self.get_config(force_reload)
        return config.get('categories', {})
    
    def get_settings(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        获取设置信息
        
        Args:
            force_reload: 是否强制重新加载
            
        Returns:
            设置字典
        """
        config = self.get_config(force_reload)
        return config.get('settings', {})
    
    def clear_cache(self):
        """清除缓存"""
        self._config_cache = None
        self._last_modified = 0
        logger.debug("话题配置缓存已清除")


# 全局配置加载器实例
_topics_loader = None


def get_topics_loader() -> TopicsConfigLoader:
    """获取全局话题配置加载器实例"""
    global _topics_loader
    if _topics_loader is None:
        _topics_loader = TopicsConfigLoader()
    return _topics_loader


# 便捷函数
def get_topics(force_reload: bool = False) -> List[Dict[str, Any]]:
    """获取话题列表"""
    return get_topics_loader().get_topics(force_reload)


def get_topic_titles(force_reload: bool = False) -> List[str]:
    """获取话题标题列表"""
    return get_topics_loader().get_topic_titles(force_reload)


def get_topic_icons(force_reload: bool = False) -> List[str]:
    """获取话题图标列表"""
    return get_topics_loader().get_topic_icons(force_reload)


def get_topic_descriptions(force_reload: bool = False) -> List[str]:
    """获取话题描述列表"""
    topics = get_topics_loader().get_topics(force_reload)
    return [topic.get('description', topic.get('title', '')) for topic in topics]


def get_category_topics(force_reload: bool = False) -> List[Dict[str, Any]]:
    """获取分类话题列表，每个分类显示一个代表话题"""
    categories = get_categories(force_reload)
    topics = get_topics(force_reload)
    
    category_topics = []
    for cat_id, cat_info in categories.items():
        # 从该分类下随机选择一个话题作为代表
        cat_topics = [t for t in topics if t.get('category') == cat_id]
        if cat_topics:
            import random
            representative_topic = random.choice(cat_topics)
            category_topics.append({
                'id': cat_id,
                'title': cat_info['name'],
                'description': representative_topic['description'],
                'icon': cat_info.get('icon', 'fluent-mdl2:default'),  # 使用分类的icon
                'category': cat_id
            })
    
    return category_topics


def get_random_topic_by_category(category: str, force_reload: bool = False) -> Optional[Dict[str, Any]]:
    """根据分类随机获取一个话题"""
    topics = get_topics_loader().get_topics(force_reload)
    category_topics = [t for t in topics if t.get('category') == category]
    
    if category_topics:
        import random
        return random.choice(category_topics)
    return None


def get_random_topic_description_by_category(category: str, force_reload: bool = False) -> str:
    """根据分类随机获取一个话题描述"""
    topic = get_random_topic_by_category(category, force_reload)
    if topic:
        return topic.get('description', topic.get('title', ''))
    return ""


def get_topic_by_id(topic_id: str, force_reload: bool = False) -> Optional[Dict[str, Any]]:
    """根据ID获取话题"""
    return get_topics_loader().get_topic_by_id(topic_id, force_reload)


def get_topics_by_category(category: str, force_reload: bool = False) -> List[Dict[str, Any]]:
    """根据分类获取话题"""
    return get_topics_loader().get_topics_by_category(category, force_reload)


def get_categories(force_reload: bool = False) -> Dict[str, Dict[str, str]]:
    """获取分类信息"""
    return get_topics_loader().get_categories(force_reload)


def get_settings(force_reload: bool = False) -> Dict[str, Any]:
    """获取设置信息"""
    return get_topics_loader().get_settings(force_reload)


def clear_topics_cache():
    """清除话题配置缓存"""
    get_topics_loader().clear_cache()
