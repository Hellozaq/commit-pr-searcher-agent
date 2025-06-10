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

import sys
import os
import logging
from github_agent import GitHubAgent

def setup_basic_logging():
    """设置基础日志配置"""
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def print_banner():
    """打印程序横幅"""
    print("=" * 60)
    print("    GitHub搜索Agent")
    print("    基于LangChain的智能GitHub搜索工具")
    print("=" * 60)

def show_main_menu():
    """显示主菜单"""
    print("\n=== 主菜单 ===")
    print("1. 配置管理")
    print("2. Token管理")
    print("3. 启动搜索")
    print("4. 退出")

def show_config_menu():
    """显示配置管理菜单"""
    print("\n=== 配置管理 ===")
    print("1. 新建配置")
    print("2. 修改配置")
    print("3. 删除配置")
    print("4. 列出所有配置")
    print("5. 返回主菜单")

def main():
    """主程序"""
    setup_basic_logging()
    print_banner()
    
    # 初始化GitHub Agent
    try:
        agent = GitHubAgent()
        print("GitHub搜索Agent初始化成功!")
    except Exception as e:
        print(f"初始化失败: {e}")
        return 1
    
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
            print(f"程序错误: {e}")
            print("请检查配置和网络连接")

if __name__ == "__main__":
    sys.exit(main()) 