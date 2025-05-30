from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from typing import List, Dict, Any
import logging
import json
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class AIHelper:
    """AI助手，用于生成搜索关键词和判断搜索结果"""
    
    def __init__(self, model_name: str = "gpt-3.5-turbo", temperature: float = 0.1):
        self.llm = ChatOpenAI(
            model_name=model_name,
            temperature=temperature,
            openai_api_key=os.getenv('OPENAI_API_KEY')
        )
    
    def generate_search_keywords(self, description: str, language: str = "") -> Dict[str, Any]:
        """
        根据自然语言描述生成搜索关键词和AI判断prompt
        
        Args:
            description: 用户的筛选条件描述
            language: 编程语言限制
            
        Returns:
            包含keywords和ai_prompt的字典
        """
        try:
            system_prompt = """你是一个GitHub搜索专家。根据用户的描述，生成适合的GitHub搜索关键词列表和AI判断prompt。

请返回JSON格式的结果，包含以下字段：
- keywords: 字符串数组，包含3-5个搜索关键词
- ai_prompt: 字符串，用于后续AI判断commit/PR是否符合要求的prompt

关键词要求：
1. 关键词应该是英文，适合GitHub搜索
2. 关键词要具体明确，避免过于宽泛
3. 可以包含技术术语、框架名称、功能描述等

AI判断prompt要求：
1. 明确说明判断标准
2. 要求AI返回明确的"是"或"否"
3. 包含对commit/PR内容的具体要求"""

            language_info = f"\n编程语言限制: {language}" if language else ""
            
            user_prompt = f"""用户描述: {description}{language_info}

请生成相应的搜索关键词和AI判断prompt。"""

            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]
            
            response = self.llm(messages)
            result = json.loads(response.content)
            
            logger.info(f"成功生成搜索关键词: {result.get('keywords', [])}")
            return result
            
        except Exception as e:
            logger.error(f"生成搜索关键词失败: {e}")
            # 返回默认值
            return {
                "keywords": ["bug fix", "enhancement", "feature"],
                "ai_prompt": "请判断这个commit/PR是否符合用户的要求，返回'是'或'否'。"
            }
    
    def judge_commit_pr(self, prompt: str, title: str, message: str, 
                       files: List[str], diff_summary: str) -> bool:
        """
        使用AI判断commit/PR是否符合要求
        
        Args:
            prompt: AI判断的prompt
            title: commit/PR标题
            message: commit/PR消息
            files: 修改的文件列表
            diff_summary: diff摘要
            
        Returns:
            是否符合要求
        """
        try:
            system_message = f"""你是一个代码审查专家。{prompt}

请仔细分析以下commit/PR信息，严格按照要求判断是否符合条件。

你必须返回"是"或"否"，不要返回其他内容。"""

            content = f"""标题: {title}

消息: {message}

修改的文件:
{chr(10).join(files)}

代码变更摘要:
{diff_summary}"""

            messages = [
                SystemMessage(content=system_message),
                HumanMessage(content=content)
            ]
            
            response = self.llm(messages)
            result = response.content.strip().lower()
            
            # 判断结果
            if "是" in result or "yes" in result:
                logger.info(f"AI判断通过: {title}")
                return True
            else:
                logger.info(f"AI判断未通过: {title}")
                return False
                
        except Exception as e:
            logger.error(f"AI判断失败: {e}")
            return False
    
    def summarize_diff(self, diff_content: str, max_length: int = 1000) -> str:
        """
        总结diff内容，避免内容过长
        
        Args:
            diff_content: diff内容
            max_length: 最大长度
            
        Returns:
            diff摘要
        """
        if len(diff_content) <= max_length:
            return diff_content
        
        try:
            system_prompt = """你是一个代码审查专家。请总结以下代码变更的主要内容，重点关注：
1. 修改的功能
2. 新增的特性
3. 修复的问题
4. 关键的代码变更

请用简洁的中文总结，不超过200字。"""

            # 截取部分diff内容
            truncated_diff = diff_content[:max_length] + "...(内容过长，已截断)"
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"代码变更:\n{truncated_diff}")
            ]
            
            response = self.llm(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"总结diff失败: {e}")
            return diff_content[:max_length] + "...(总结失败，显示原始内容)" 