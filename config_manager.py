import json
import os
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class SearchConfig(BaseModel):
    """搜索配置数据模型"""
    name: str
    language: str  # 限制语言，对应github搜索中的"lang:"
    filter_description: str  # 筛选条件的自然语言描述
    search_keywords: List[str]  # AI生成的搜索关键词列表
    ai_prompt: str  # AI判断的prompt
    file_filter_regex: str  # 初筛条件，commit/pr中必须包含哪些文件修改的正则表达式
    result_file: str  # 保存结果的json文件名

class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_dir: str = "configs"):
        self.config_dir = config_dir
        self._ensure_config_dir()
    
    def _ensure_config_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def _get_config_file(self, name: str) -> str:
        """获取配置文件路径"""
        return os.path.join(self.config_dir, f"{name}.json")
    
    def create_config(self, config: SearchConfig) -> bool:
        """新建配置"""
        try:
            config_file = self._get_config_file(config.name)
            if os.path.exists(config_file):
                logger.error(f"配置 '{config.name}' 已存在")
                return False
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config.dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置 '{config.name}' 创建成功")
            return True
        except Exception as e:
            logger.error(f"创建配置失败: {e}")
            return False
    
    def load_config(self, name: str) -> Optional[SearchConfig]:
        """加载配置"""
        try:
            config_file = self._get_config_file(name)
            if not os.path.exists(config_file):
                logger.error(f"配置 '{name}' 不存在")
                return None
            
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return SearchConfig(**data)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return None
    
    def update_config(self, config: SearchConfig) -> bool:
        """修改配置"""
        try:
            config_file = self._get_config_file(config.name)
            if not os.path.exists(config_file):
                logger.error(f"配置 '{config.name}' 不存在")
                return False
            
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config.dict(), f, ensure_ascii=False, indent=2)
            
            logger.info(f"配置 '{config.name}' 更新成功")
            return True
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return False
    
    def delete_config(self, name: str) -> bool:
        """删除配置"""
        try:
            config_file = self._get_config_file(name)
            if not os.path.exists(config_file):
                logger.error(f"配置 '{name}' 不存在")
                return False
            
            os.remove(config_file)
            logger.info(f"配置 '{name}' 删除成功")
            return True
        except Exception as e:
            logger.error(f"删除配置失败: {e}")
            return False
    
    def list_configs(self) -> List[str]:
        """列出所有配置"""
        try:
            if not os.path.exists(self.config_dir):
                return []
            
            configs = []
            for file in os.listdir(self.config_dir):
                if file.endswith('.json'):
                    configs.append(file[:-5])  # 去掉.json后缀
            
            return configs
        except Exception as e:
            logger.error(f"列出配置失败: {e}")
            return [] 