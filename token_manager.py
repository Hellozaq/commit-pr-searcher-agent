import json
import os
import random
from typing import List
import logging

logger = logging.getLogger(__name__)

class TokenManager:
    """GitHub Token管理器"""
    
    def __init__(self, token_file: str = "github_tokens.json"):
        self.token_file = token_file
        self.tokens = []
        self.load_tokens()
    
    def load_tokens(self):
        """加载token列表"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tokens = data.get('tokens', [])
                logger.info(f"加载了 {len(self.tokens)} 个GitHub tokens")
            else:
                logger.warning(f"Token文件 {self.token_file} 不存在，将创建空的token列表")
                self.tokens = []
        except Exception as e:
            logger.error(f"加载token失败: {e}")
            self.tokens = []
    
    def save_tokens(self):
        """保存token列表"""
        try:
            data = {'tokens': self.tokens}
            with open(self.token_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.info("Token列表保存成功")
        except Exception as e:
            logger.error(f"保存token失败: {e}")
    
    def add_token(self, token: str) -> bool:
        """添加token"""
        try:
            if token in self.tokens:
                logger.warning("Token已存在")
                return False
            
            self.tokens.append(token)
            self.save_tokens()
            logger.info("Token添加成功")
            return True
        except Exception as e:
            logger.error(f"添加token失败: {e}")
            return False
    
    def remove_token(self, token: str) -> bool:
        """删除token"""
        try:
            if token not in self.tokens:
                logger.warning("Token不存在")
                return False
            
            self.tokens.remove(token)
            self.save_tokens()
            logger.info("Token删除成功")
            return True
        except Exception as e:
            logger.error(f"删除token失败: {e}")
            return False
    
    def get_random_token(self) -> str:
        """随机获取一个token"""
        if not self.tokens:
            logger.error("没有可用的token")
            return ""
        
        return random.choice(self.tokens)
    
    def get_all_tokens(self) -> List[str]:
        """获取所有token"""
        return self.tokens.copy()
    
    def set_tokens(self, tokens: List[str]):
        """设置token列表"""
        self.tokens = tokens
        self.save_tokens()
        logger.info(f"设置了 {len(tokens)} 个tokens")
    
    def has_tokens(self) -> bool:
        """检查是否有可用的token"""
        return len(self.tokens) > 0 