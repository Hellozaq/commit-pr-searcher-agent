#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GitHub搜索Agent主程序

使用LangChain构建的GitHub搜索Agent，用于在GitHub中搜索特定的commit或pull request。

功能包括：
1. 配置管理 - 新建/修改/删除配置
2. Token管理 - 管理GitHub API tokens
3. 启动搜索 - 根据配置搜索并保存结果
"""

import os
import sys
import logging
from datetime import datetime
from src.github_agent import GitHubAgent

# 配置日志
log_dir = 'logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f'github_search_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """打印程序横幅"""
    banner = """
============================================================
    GitHub搜索Agent
    基于LangChain的智能GitHub搜索工具
============================================================
"""
    print(banner)

def show_main_menu():
    """显示主菜单"""
    menu = """
1. 配置管理
2. Token管理
3. 启动搜索
4. 退出
"""
    print(menu)

def show_config_menu():
    """显示配置管理菜单"""
    menu = """
1. 创建新配置
2. 修改配置
3. 删除配置
4. 查看配置列表
5. 返回主菜单
"""
    print(menu)

def main():
    """主函数"""
    try:
        print_banner()
        
        # 创建GitHub搜索代理
        agent = GitHubAgent()
        logger.info("GitHub搜索Agent初始化成功!")
        
        while True:
            try:
                show_main_menu()
                choice = input("\n请选择操作 (1-4): ").strip()
                
                if choice == '1':
                    # 配置管理
                    while True:
                        show_config_menu()
                        config_choice = input("\n请选择操作 (1-5): ").strip()
                        
                        if config_choice == '1':
                            agent.create_config_interactive()
                        elif config_choice == '2':
                            agent.modify_config_interactive()
                        elif config_choice == '3':
                            agent.delete_config_interactive()
                        elif config_choice == '4':
                            agent.list_configs()
                        elif config_choice == '5':
                            break
                        else:
                            print("无效的选择，请重新输入")
                
                elif choice == '2':
                    # Token管理
                    agent.manage_tokens_interactive()
                
                elif choice == '3':
                    # 启动搜索
                    agent.search_interactive()
                
                elif choice == '4':
                    # 退出
                    print("感谢使用GitHub搜索Agent！")
                    break
                
                else:
                    print("无效的选择，请重新输入")
                    
            except KeyboardInterrupt:
                print("\n\n用户中断操作")
                confirm = input("确认退出程序? (y/n): ").strip().lower()
                if confirm == 'y':
                    print("感谢使用GitHub搜索Agent！")
                    break
            except Exception as e:
                logger.error(f"程序错误: {e}")
                print("请检查配置和网络连接")
                
    except Exception as e:
        logger.error(f"程序运行出错: {str(e)}", exc_info=True)
    finally:
        logger.info("程序结束")

if __name__ == "__main__":
    main() 