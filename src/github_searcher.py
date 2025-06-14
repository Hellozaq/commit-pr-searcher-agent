import requests
import re
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging
from urllib.parse import quote
from github import Github
from github.GithubException import GithubException

from token_manager import TokenManager
from ai_helper import AIHelper

logger = logging.getLogger(__name__)

class GitHubSearcher:
    """GitHub搜索器"""
    
    def __init__(self, token_manager: TokenManager, ai_helper: AIHelper, 
                 max_diff_size: int = 10000):
        self.token_manager = token_manager
        self.ai_helper = ai_helper
        self.max_diff_size = max_diff_size
        self.max_file_size = 5000  # 单个文件的最大大小
        self.search_results = []
        
    def _get_github_client(self) -> Optional[Github]:
        """获取GitHub客户端"""
        token = self.token_manager.get_random_token()
        if not token:
            logger.error("没有可用的GitHub token")
            return None
        
        try:
            return Github(token)
        except Exception as e:
            logger.error(f"创建GitHub客户端失败: {e}")
            return None
    
    def _search_commits(self, query: str, start_date: str, end_date: str, 
                       per_page: int = 100) -> List[Dict[str, Any]]:
        """搜索commits"""
        try:
            g = self._get_github_client()
            if not g:
                return []
            
            # 构建搜索查询
            date_query = f"committer-date:{start_date}..{end_date}"
            full_query = f"{query} {date_query}"
            
            logger.info(f"搜索commits: {full_query}")
            
            results = []
            commits = g.search_commits(full_query)
            
            count = 0
            for commit in commits:
                if count >= per_page:
                    break
                
                try:
                    commit_data = {
                        'type': 'commit',
                        'sha': commit.sha,
                        'title': commit.commit.message.split('\n')[0],
                        'message': commit.commit.message,
                        'url': commit.html_url,
                        'date': commit.commit.committer.date.isoformat(),
                        'author': commit.commit.author.name,
                        'repository': commit.repository.full_name,
                        'files': [],
                        'checked': 0, 
                        'note': ''
                    }
                    
                    # 获取文件列表
                    try:
                        files = commit.files
                        commit_data['files'] = [f.filename for f in files]
                    except Exception as e:
                        logger.warning(f"获取commit文件列表失败: {e}")
                    
                    results.append(commit_data)
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"处理commit数据失败: {e}")
                    continue
            
            logger.info(f"找到 {len(results)} 个commits")
            return results
            
        except GithubException as e:
            logger.error(f"GitHub API错误: {e}")
            return []
        except Exception as e:
            logger.error(f"搜索commits失败: {e}")
            return []
    
    def _search_pull_requests(self, query: str, start_date: str, end_date: str,
                            per_page: int = 100) -> List[Dict[str, Any]]:
        """搜索pull requests"""
        try:
            g = self._get_github_client()
            if not g:
                return []
            
            # 构建搜索查询，添加类型和日期限制
            date_query = f"created:{start_date}..{end_date}"
            full_query = f"{query} type:pr is:merged {date_query}"
            
            logger.info(f"搜索pull requests: {full_query}")
            
            results = []
            issues = g.search_issues(full_query)  # PRs are treated as issues in GitHub API
            
            count = 0
            for issue in issues:
                if count >= per_page:
                    break
                
                if not issue.pull_request:
                    continue
                
                try:
                    # 获取PR详细信息
                    pr = issue.repository.get_pull(issue.number)
                    
                    pr_data = {
                        'type': 'pull_request',
                        'number': pr.number,
                        'title': pr.title,
                        'message': pr.body or "",
                        'url': pr.html_url,
                        'date': pr.created_at.isoformat(),
                        'author': pr.user.login,
                        'repository': pr.base.repo.full_name,
                        'state': pr.state,
                        'files': [],
                        'checked': 0,
                        'note': ''
                    }
                    
                    # 获取文件列表
                    try:
                        files = pr.get_files()
                        pr_data['files'] = [f.filename for f in files]
                    except Exception as e:
                        logger.warning(f"获取PR文件列表失败: {e}")
                    
                    results.append(pr_data)
                    count += 1
                    
                except Exception as e:
                    logger.warning(f"处理PR数据失败: {e}")
                    continue
            
            logger.info(f"找到 {len(results)} 个pull requests")
            return results
            
        except GithubException as e:
            logger.error(f"GitHub API错误: {e}")
            return []
        except Exception as e:
            logger.error(f"搜索pull requests失败: {e}")
            return []
    
    def _apply_file_filter(self, items: List[Dict[str, Any]], 
                          file_filter_regex: str) -> List[Dict[str, Any]]:
        """应用文件过滤
        
        Args:
            items: 要过滤的项目列表
            file_filter_regex: 文件过滤正则表达式，多个条件用分号(;)分隔
                             例如：".*.java;abc.txt" 表示必须同时包含.java文件和abc.txt文件
            
        Returns:
            过滤后的项目列表
        """
        if not file_filter_regex:
            return items
            
        filtered_items = []
        patterns = [pattern.strip() for pattern in file_filter_regex.split(';') if pattern.strip()]
        
        for item in items:
            # 检查文件列表
            if not item['files']:
                continue
                
            # 检查是否所有模式都有匹配的文件
            all_patterns_matched = True
            for pattern in patterns:
                # 如果任何一个模式没有匹配的文件，就跳过这个item
                if not any(re.search(pattern, f) for f in item['files']):
                    all_patterns_matched = False
                    break
            
            if all_patterns_matched:
                filtered_items.append(item)
        
        logger.info(f"文件过滤后剩余 {len(filtered_items)} 个结果")
        return filtered_items
    
    # def _check_files_match_patterns(self, files: List[str], patterns: List[re.Pattern]) -> bool:
    #     """检查文件列表是否满足所有过滤条件
        
    #     Args:
    #         files: 文件列表
    #         patterns: 正则表达式模式列表
            
    #     Returns:
    #         是否满足所有条件
    #     """
    #     # 对于每个模式，检查是否至少有一个文件匹配
    #     for pattern in patterns:
    #         if not any(pattern.search(file) for file in files):
    #             return False
    #     return True

    def _check_file_match_patterns(self, filename: str, patterns: List[str]) -> bool:
        """检查文件是否符合过滤条件"""
        for pattern in patterns:
            if re.search(pattern, filename):
                return True
        return False
    
    def _filter_diff_files(self, files: List[Any], file_filter_regex: str) -> List[Any]:
        """过滤diff文件"""
        selected_files = []
        file_count = 0
        patterns = [pattern.strip() for pattern in file_filter_regex.split(';') if pattern.strip()]
        for file in files:
            # 检查文件是否符合过滤条件
            if not self._check_file_match_patterns(file.filename, patterns):
                continue
            file_count += 1
            # 检查文件大小
            if file.patch and len(file.patch) <= self.max_file_size:
                selected_files.append(file)
        
        # 如果文件数量超过50，返回空列表
        if file_count > 50:
            logger.warning(f"跳过过多的diff文件: {file_count}个")
            return []
            
        return selected_files

    def _get_commit_diff(self, item: Dict[str, Any], file_filter_regex: str) -> str:
        """获取commit的diff信息"""
        try:
            g = self._get_github_client()
            if not g:
                return ""
            
            repo = g.get_repo(item['repository'])
            commit = repo.get_commit(item['sha'])
            
            # 过滤文件
            selected_files = self._filter_diff_files(commit.files, file_filter_regex)
            
            diff_text = ""
            for file in selected_files:
                if file.patch:
                    diff_text += f"\n--- {file.filename} ---\n"
                    diff_text += file.patch
            
            return diff_text
            
        except Exception as e:
            logger.warning(f"获取commit diff失败: {e}")
            return ""
    
    def _get_pr_diff(self, item: Dict[str, Any], file_filter_regex: str) -> str:
        """获取PR的diff信息"""
        try:
            g = self._get_github_client()
            if not g:
                return ""
            
            repo = g.get_repo(item['repository'])
            pr = repo.get_pull(item['number'])
            
            # 过滤文件
            selected_files = self._filter_diff_files(pr.get_files(), file_filter_regex)
            
            diff_text = ""
            for file in selected_files:
                if file.patch:
                    diff_text += f"\n--- {file.filename} ---\n"
                    diff_text += file.patch
            
            return diff_text
            
        except Exception as e:
            logger.warning(f"获取PR diff失败: {e}")
            return ""
    
    def _ai_filter_items(self, items: List[Dict[str, Any]], 
                        ai_prompt: str, file_filter_regex: str) -> List[Dict[str, Any]]:
        """使用AI过滤项目"""
        filtered_items = []
        
        for item in items:
            try:
                # 获取diff信息
                if item['type'] == 'commit':
                    diff_content = self._get_commit_diff(item, file_filter_regex)
                else:
                    diff_content = self._get_pr_diff(item, file_filter_regex)
                
                # 检查diff大小
                if len(diff_content) > self.max_diff_size:
                    logger.warning(f"跳过过大的diff: {item['title']} (大小: {len(diff_content)})")
                    continue
                if len(diff_content) == 0:
                    logger.warning(f"跳过不符合要求的diff: {item['title']}")
                    continue
                
                # 总结diff内容
                diff_summary = self.ai_helper.summarize_diff(diff_content)
                
                # AI判断
                if self.ai_helper.judge_commit_pr(
                    ai_prompt, 
                    item['title'], 
                    item['message'], 
                    item['files'], 
                    diff_summary,
                    item['url']
                ):
                    filtered_items.append(item)
                
                # 避免API调用过快
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"AI过滤失败: {e}")
                continue
        
        logger.info(f"AI过滤后剩余 {len(filtered_items)} 个结果")
        return filtered_items
    
    def search_by_date_range(self, keywords: List[str], language: str,
                           start_date: str, end_date: str, 
                           file_filter_regex: str, ai_prompt: str,
                           search_commits: bool = True, 
                           search_prs: bool = True) -> List[Dict[str, Any]]:
        """按日期范围搜索"""
        all_results = []
        
        # 构建基础查询
        base_query = " OR ".join(keywords)
        if language:
            base_query += f" language:{language}"
        
        for keyword in keywords:
            try:
                query = keyword
                if language:
                    query += f" language:{language}"
                
                results = []
                
                # 搜索commits
                if search_commits:
                    commits = self._search_commits(query, start_date, end_date)
                    results.extend(commits)
                
                # 搜索PRs
                if search_prs:
                    prs = self._search_pull_requests(query, start_date, end_date)
                    results.extend(prs)
                
                # 应用文件过滤
                filtered_results = self._apply_file_filter(results, file_filter_regex)
                
                # AI过滤
                if ai_prompt and filtered_results:
                    final_results = self._ai_filter_items(filtered_results, ai_prompt, file_filter_regex)
                else:
                    final_results = filtered_results
                
                all_results.extend(final_results)
                
                # 避免API调用过快
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"搜索关键词 '{keyword}' 失败: {e}")
                continue
        
        # 去除重复结果
        unique_results = []
        seen_urls = set()
        for result in all_results:
            if result['url'] not in seen_urls:
                seen_urls.add(result['url'])
                unique_results.append(result)
        
        logger.info(f"搜索完成，共找到 {len(unique_results)} 个唯一结果")
        return unique_results
    
    def search_with_date_segments(self, keywords: List[str], language: str,
                                start_date: str, end_date: str,
                                file_filter_regex: str, ai_prompt: str,
                                days_per_segment: int = 7) -> List[Dict[str, Any]]:
        """分段搜索，避免结果过多"""
        all_results = []
        
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
        
        current = start
        while current < end:
            segment_end = min(current + timedelta(days=days_per_segment), end)
            
            segment_start_str = current.strftime('%Y-%m-%d')
            segment_end_str = segment_end.strftime('%Y-%m-%d')
            
            logger.info(f"搜索时间段: {segment_start_str} 到 {segment_end_str}")
            
            segment_results = self.search_by_date_range(
                keywords, language, segment_start_str, segment_end_str,
                file_filter_regex, ai_prompt
            )
            
            all_results.extend(segment_results)
            current = segment_end
        
        return all_results 