import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from config_manager import ConfigManager, SearchConfig
from token_manager import TokenManager
from ai_helper import AIHelper
from github_searcher import GitHubSearcher

logger = logging.getLogger(__name__)

class GitHubAgent:
    """GitHub搜索Agent主类"""
    
    def __init__(self, config_dir: str = "configs", token_file: str = "github_tokens.json",
                 result_dir: str = "results", log_dir: str = "logs"):
        self.config_manager = ConfigManager(config_dir)
        self.token_manager = TokenManager(token_file)
        self.ai_helper = AIHelper()
        self.github_searcher = GitHubSearcher(self.token_manager, self.ai_helper)
        
        self.result_dir = result_dir
        self.log_dir = log_dir
        
        # 确保目录存在
        for directory in [result_dir, log_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def setup_logging(self, config_name: str):
        """设置日志记录"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = os.path.join(self.log_dir, f"{config_name}_{timestamp}.log")
        
        # 配置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
        
        # 配置根日志记录器
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.INFO)
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        logger.info(f"日志文件: {log_file}")
    
    def create_config_interactive(self) -> bool:
        """交互式创建配置"""
        try:
            print("\n=== 创建新配置 ===")
            
            # 获取配置名称
            name = input("请输入配置名称: ").strip()
            if not name:
                print("配置名称不能为空")
                return False
            
            # 检查配置是否已存在
            if name in self.config_manager.list_configs():
                print(f"配置 '{name}' 已存在")
                return False
            
            # 获取语言限制
            language = input("请输入限制语言 (如: python, javascript, 留空不限制): ").strip()
            
            # 获取筛选条件描述
            description = input("请输入筛选条件的自然语言描述: ").strip()
            if not description:
                print("筛选条件描述不能为空")
                return False
            
            # 使用AI生成搜索关键词和判断prompt
            print("正在生成搜索关键词和AI判断prompt...")
            ai_result = self.ai_helper.generate_search_keywords(description, language)
            
            keywords = ai_result.get('keywords', [])
            ai_prompt = ai_result.get('ai_prompt', '')
            
            print(f"生成的搜索关键词: {keywords}")
            print(f"生成的AI判断prompt: {ai_prompt}")
            
            # 用户确认或修改
            modify = input("是否修改关键词? (y/n): ").strip().lower()
            if modify == 'y':
                keywords_str = input(f"请输入关键词 (用逗号分隔, 当前: {', '.join(keywords)}): ").strip()
                if keywords_str:
                    keywords = [k.strip() for k in keywords_str.split(',')]
            
            modify_prompt = input("是否修改AI判断prompt? (y/n): ").strip().lower()
            if modify_prompt == 'y':
                new_prompt = input(f"请输入新的AI判断prompt: ").strip()
                if new_prompt:
                    ai_prompt = new_prompt
            
            # 获取文件过滤正则表达式
            file_filter = input("请输入文件过滤正则表达式（留空不过滤，若有多个表达式请用英文分号分隔，例如：\\.java$;\\.xml$ 表示匹配Java和XML文件）: ").strip()
            
            # 获取结果文件名
            result_file = input(f"请输入结果文件名 (默认: {name}_results.json): ").strip()
            if not result_file:
                result_file = f"{name}_results.json"
            
            # 创建配置
            config = SearchConfig(
                name=name,
                language=language,
                filter_description=description,
                search_keywords=keywords,
                ai_prompt=ai_prompt,
                file_filter_regex=file_filter,
                result_file=result_file
            )
            
            if self.config_manager.create_config(config):
                print(f"配置 '{name}' 创建成功!")
                return True
            else:
                print("配置创建失败")
                return False
                
        except KeyboardInterrupt:
            print("\n用户取消操作")
            return False
        except Exception as e:
            logger.error(f"创建配置失败: {e}")
            print(f"创建配置失败: {e}")
            return False
    
    def modify_config_interactive(self) -> bool:
        """交互式修改配置"""
        try:
            # 列出所有配置
            configs = self.config_manager.list_configs()
            if not configs:
                print("没有可用的配置")
                return False
            
            print("\n=== 修改配置 ===")
            print("可用配置:")
            for i, config_name in enumerate(configs, 1):
                print(f"{i}. {config_name}")
            
            # 选择配置
            choice = input("请选择要修改的配置 (输入编号或名称): ").strip()
            
            config_name = None
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(configs):
                    config_name = configs[idx]
            else:
                if choice in configs:
                    config_name = choice
            
            if not config_name:
                print("无效的选择")
                return False
            
            # 加载配置
            config = self.config_manager.load_config(config_name)
            if not config:
                print("加载配置失败")
                return False
            
            # 显示当前配置
            print(f"\n当前配置 '{config_name}':")
            print(f"语言限制: {config.language}")
            print(f"关键词: {', '.join(config.search_keywords)}")
            print(f"文件过滤正则表达式: {config.file_filter_regex}")
            print(f"AI判断提示词: {config.ai_prompt}")
            print(f"结果文件: {config.result_file}")
            
            # 选择要修改的字段
            print("\n可修改的字段:")
            print("1. 关键词")
            print("2. 语言")
            print("3. 文件过滤正则表达式")
            print("4. AI判断提示词")
            print("5. 取消修改")
            
            choice = input("\n请选择要修改的字段 (1-5): ").strip()
            
            if choice == '1':
                keywords = input("请输入新的关键词（多个关键词请用英文逗号分隔，例如：bug fix, enhancement, feature）: ").strip()
                config.search_keywords = [k.strip() for k in keywords.split(',')]
            elif choice == '2':
                language = input("请输入新的语言（例如：java, python, javascript）: ").strip()
                config.language = language
            elif choice == '3':
                file_filter = input("请输入新的文件过滤正则表达式（留空不过滤，若有多个表达式请用英文分号分隔，例如：\\.java$;\\.xml$ 表示匹配Java和XML文件）: ").strip()
                config.file_filter_regex = file_filter
            elif choice == '4':
                ai_prompt = input("请输入新的AI判断提示词（用于判断commit/PR是否符合要求）: ").strip()
                config.ai_prompt = ai_prompt
            elif choice == '5':
                print("取消修改")
                return True
            else:
                print("无效的选择")
                return False
            
            # 保存配置
            if self.config_manager.update_config(config):
                print(f"配置 '{config_name}' 修改成功!")
                return True
            else:
                print("配置修改失败")
                return False
                
        except KeyboardInterrupt:
            print("\n用户取消操作")
            return False
        except Exception as e:
            logger.error(f"修改配置失败: {e}")
            print(f"修改配置失败: {e}")
            return False
    
    def delete_config_interactive(self) -> bool:
        """交互式删除配置"""
        try:
            configs = self.config_manager.list_configs()
            if not configs:
                print("没有可用的配置")
                return False
            
            print("\n=== 删除配置 ===")
            print("可用配置:")
            for i, config_name in enumerate(configs, 1):
                print(f"{i}. {config_name}")
            
            choice = input("请选择要删除的配置 (输入编号或名称): ").strip()
            
            config_name = None
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(configs):
                    config_name = configs[idx]
            else:
                if choice in configs:
                    config_name = choice
            
            if not config_name:
                print("无效的选择")
                return False
            
            # 确认删除
            confirm = input(f"确认删除配置 '{config_name}'? (y/n): ").strip().lower()
            if confirm != 'y':
                print("取消删除")
                return False
            
            if self.config_manager.delete_config(config_name):
                print(f"配置 '{config_name}' 删除成功!")
                return True
            else:
                print("配置删除失败")
                return False
                
        except KeyboardInterrupt:
            print("\n用户取消操作")
            return False
        except Exception as e:
            logger.error(f"删除配置失败: {e}")
            print(f"删除配置失败: {e}")
            return False
    
    def manage_tokens_interactive(self) -> bool:
        """交互式管理tokens"""
        try:
            while True:
                print("\n=== Token管理 ===")
                print("1. 查看当前tokens")
                print("2. 添加token")
                print("3. 删除token")
                print("4. 批量设置tokens")
                print("5. 返回主菜单")
                
                choice = input("请选择操作 (1-5): ").strip()
                
                if choice == '1':
                    tokens = self.token_manager.get_all_tokens()
                    if tokens:
                        print(f"当前有 {len(tokens)} 个tokens:")
                        for i, token in enumerate(tokens, 1):
                            # 只显示token的前8位和后8位
                            masked = f"{token[:8]}...{token[-8:]}" if len(token) > 16 else token
                            print(f"{i}. {masked}")
                    else:
                        print("没有配置任何token")
                
                elif choice == '2':
                    token = input("请输入要添加的GitHub token: ").strip()
                    if token:
                        if self.token_manager.add_token(token):
                            print("Token添加成功!")
                        else:
                            print("Token添加失败 (可能已存在)")
                    else:
                        print("Token不能为空")
                
                elif choice == '3':
                    tokens = self.token_manager.get_all_tokens()
                    if not tokens:
                        print("没有可删除的token")
                        continue
                    
                    print("当前tokens:")
                    for i, token in enumerate(tokens, 1):
                        masked = f"{token[:8]}...{token[-8:]}" if len(token) > 16 else token
                        print(f"{i}. {masked}")
                    
                    choice_del = input("请选择要删除的token (输入编号): ").strip()
                    if choice_del.isdigit():
                        idx = int(choice_del) - 1
                        if 0 <= idx < len(tokens):
                            if self.token_manager.remove_token(tokens[idx]):
                                print("Token删除成功!")
                            else:
                                print("Token删除失败")
                        else:
                            print("无效的编号")
                    else:
                        print("请输入有效的编号")
                
                elif choice == '4':
                    print("请输入tokens，每行一个 (输入空行结束):")
                    new_tokens = []
                    while True:
                        token = input().strip()
                        if not token:
                            break
                        new_tokens.append(token)
                    
                    if new_tokens:
                        self.token_manager.set_tokens(new_tokens)
                        print(f"已设置 {len(new_tokens)} 个tokens")
                    else:
                        print("没有输入任何token")
                
                elif choice == '5':
                    break
                
                else:
                    print("无效的选择")
                    
        except KeyboardInterrupt:
            print("\n用户取消操作")
            return False
        except Exception as e:
            logger.error(f"管理tokens失败: {e}")
            print(f"管理tokens失败: {e}")
            return False
        
        return True
    
    def search_interactive(self) -> bool:
        """交互式启动搜索"""
        try:
            # 检查是否有tokens
            if not self.token_manager.has_tokens():
                print("请先配置GitHub tokens")
                return False
            
            # 选择配置
            configs = self.config_manager.list_configs()
            if not configs:
                print("没有可用的配置，请先创建配置")
                return False
            
            print("\n=== 启动搜索 ===")
            print("可用配置:")
            for i, config_name in enumerate(configs, 1):
                print(f"{i}. {config_name}")
            
            choice = input("请选择要使用的配置 (输入编号或名称): ").strip()
            
            config_name = None
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(configs):
                    config_name = configs[idx]
            else:
                if choice in configs:
                    config_name = choice
            
            if not config_name:
                print("无效的选择")
                return False
            
            # 加载配置
            config = self.config_manager.load_config(config_name)
            if not config:
                print("加载配置失败")
                return False
            
            # 设置日志
            self.setup_logging(config_name)
            
            # 获取搜索日期范围
            start_date = input("请输入开始日期 (格式: YYYY-MM-DD): ").strip()
            end_date = input("请输入结束日期 (格式: YYYY-MM-DD): ").strip()
            
            try:
                # 验证日期格式
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                print("日期格式错误，请使用 YYYY-MM-DD 格式")
                return False
            
            print(f"\n开始搜索...")
            print(f"配置: {config_name}")
            print(f"关键词: {config.search_keywords}")
            print(f"语言: {config.language}")
            print(f"日期范围: {start_date} 到 {end_date}")
            
            # 执行搜索
            results = self.github_searcher.search_with_date_segments(
                keywords=config.search_keywords,
                language=config.language,
                start_date=start_date,
                end_date=end_date,
                file_filter_regex=config.file_filter_regex,
                ai_prompt=config.ai_prompt
            )
            
            # 保存结果
            if results:
                result_file = self._save_results(results, config.result_file, start_date, end_date)
                print(f"\n搜索完成! 找到 {len(results)} 个结果")
                print(f"结果已保存到: {result_file}")
                
                # 显示前几个结果
                print("\n前5个结果:")
                for i, result in enumerate(results[:5], 1):
                    print(f"{i}. {result['title']}")
                    print(f"   类型: {result['type']}")
                    print(f"   链接: {result['url']}")
                    print(f"   仓库: {result['repository']}")
                    print()
            else:
                print("没有找到符合条件的结果")
            
            return True
            
        except KeyboardInterrupt:
            print("\n用户取消操作")
            return False
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            print(f"搜索失败: {e}")
            return False
    
    def _save_results(self, results: List[Dict[str, Any]], base_filename: str, 
                     start_date: str, end_date: str) -> str:
        """保存搜索结果"""
        # 生成文件名
        date_suffix = f"{start_date}_to_{end_date}".replace('-', '')
        filename_parts = base_filename.split('.')
        if len(filename_parts) > 1:
            filename = f"{'.'.join(filename_parts[:-1])}_{date_suffix}.{filename_parts[-1]}"
        else:
            filename = f"{base_filename}_{date_suffix}.json"
        
        filepath = os.path.join(self.result_dir, filename)
        
        # 转换为指定格式
        formatted_results = []
        for i, result in enumerate(results, 1):
            formatted_result = {
                'id': i,
                'title': result['title'],
                'url': result['url'],
                'type': result['type'],
                'repository': result['repository'],
                'date': result['date'],
                'author': result['author']
            }
            formatted_results.append(formatted_result)
        
        # 保存到文件
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(formatted_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"结果已保存到: {filepath}")
        return filepath
    
    def list_configs(self):
        """列出所有配置"""
        configs = self.config_manager.list_configs()
        if configs:
            print("可用配置:")
            for config_name in configs:
                print(f"- {config_name}")
        else:
            print("没有可用的配置") 