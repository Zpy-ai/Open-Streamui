"""
网络搜索服务模块
提供联网搜索功能
"""

import requests
import json
import logging
from typing import Dict, Any, List, Optional


class WebSearchService:
    """网络搜索服务类"""
    
    def __init__(self, config_manager):
        """
        初始化网络搜索服务
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.logger = logging.getLogger(__name__)
        
        # 从配置文件中读取搜索API配置
        web_search_config = self.config_manager.get_config().get("web_search", {})
        self.search_url = web_search_config.get("url")
        self.api_key = web_search_config.get("api_key")
        self.default_tool = web_search_config.get("default_tool")
        self.timeout = web_search_config.get("timeout")
    
    def search_web(self, query: str, tool: str = None) -> Dict[str, Any]:
        """
        执行网络搜索
        
        Args:
            query (str): 搜索查询
            tool (str, optional): 搜索工具，默认使用quark_search
            
        Returns:
            Dict[str, Any]: 搜索结果
        """
        try:
            # 准备请求数据
            search_tool = tool or self.default_tool
            payload = {
                "query": query,
                "tools": search_tool
            }
            
            # 准备请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            self.logger.info(f"开始网络搜索: {query}")
            
            # 发送搜索请求
            response = requests.post(
                self.search_url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            # 检查响应状态
            if response.status_code == 200:
                result_data = response.json()
                self.logger.info(f"搜索成功，状态码: {response.status_code}")
                
                return {
                    "success": True,
                    "query": query,
                    "tool": search_tool,
                    "results": result_data,
                    "raw_response": result_data
                }
            else:
                error_msg = f"搜索请求失败，状态码: {response.status_code}"
                self.logger.error(error_msg)
                
                return {
                    "success": False,
                    "query": query,
                    "error": error_msg,
                    "status_code": response.status_code,
                    "response_text": response.text
                }
                
        except requests.exceptions.Timeout:
            error_msg = "搜索请求超时"
            self.logger.error(error_msg)
            return {
                "success": False,
                "query": query,
                "error": error_msg
            }
            
        except requests.exceptions.RequestException as e:
            error_msg = f"搜索请求异常: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "query": query,
                "error": error_msg
            }
            
        except Exception as e:
            error_msg = f"搜索过程中发生未知错误: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "query": query,
                "error": error_msg
            }
    
    def format_search_results(self, search_result: Dict[str, Any]) -> str:
        """
        格式化搜索结果为文本
        
        Args:
            search_result (Dict[str, Any]): 搜索结果
            
        Returns:
            str: 格式化后的搜索结果文本
        """
        if not search_result.get("success", False):
            return f"搜索失败: {search_result.get('error', '未知错误')}"
        
        try:
            results = search_result.get("results", {})
            
            # 如果结果是字符串，直接返回
            if isinstance(results, str):
                return results
            
            # 如果结果是字典，尝试提取有用信息
            if isinstance(results, dict):
                formatted_text = f"搜索查询: {search_result.get('query', '')}\n\n"
                
                # 尝试提取不同可能的结果字段
                if "content" in results:
                    formatted_text += f"搜索结果:\n{results['content']}\n"
                elif "answer" in results:
                    formatted_text += f"搜索结果:\n{results['answer']}\n"
                elif "text" in results:
                    formatted_text += f"搜索结果:\n{results['text']}\n"
                else:
                    # 如果没有明确的内容字段，将整个结果转为字符串
                    formatted_text += f"搜索结果:\n{json.dumps(results, ensure_ascii=False, indent=2)}\n"
                
                return formatted_text
            
            # 如果结果是列表
            if isinstance(results, list):
                formatted_text = f"搜索查询: {search_result.get('query', '')}\n\n"
                formatted_text += "搜索结果:\n"
                
                for i, item in enumerate(results[:5], 1):  # 最多显示5个结果
                    if isinstance(item, dict):
                        title = item.get("title", f"结果 {i}")
                        content = item.get("content", item.get("snippet", str(item)))
                        formatted_text += f"{i}. {title}\n{content}\n\n"
                    else:
                        formatted_text += f"{i}. {str(item)}\n\n"
                
                return formatted_text
            
            # 默认情况，直接转换为字符串
            return f"搜索查询: {search_result.get('query', '')}\n\n搜索结果:\n{str(results)}"
            
        except Exception as e:
            self.logger.error(f"格式化搜索结果时发生错误: {str(e)}")
            return f"搜索结果格式化失败: {str(e)}"