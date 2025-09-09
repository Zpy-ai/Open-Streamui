"""
配置管理模块
负责加载和管理应用程序配置
"""

import json
import os
import streamlit as st


class ConfigManager:
    """配置管理器类"""
    
    def __init__(self, config_path="config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path (str): 配置文件路径
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """
        加载配置文件
        
        Returns:
            dict: 配置字典
        """
        if not os.path.exists(self.config_path):
            st.error(f"配置文件 {self.config_path} 不存在！")
            st.stop()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"读取配置文件失败：{str(e)}")
            st.stop()
    
    def get_openai_config(self):
        """获取OpenAI配置"""
        return self.config.get("openai", {})
    
    def get_meilisearch_config(self):
        """获取Meilisearch配置"""
        return self.config.get("meilisearch", {})
    
    def get_embedding_config(self):
        """获取向量嵌入配置"""
        return self.config.get("embedding", {})
    
    def get_search_config(self):
        """获取搜索配置"""
        return self.config.get("search", {})
    
    def get_web_search_config(self):
        """获取网络搜索配置"""
        return self.config.get("web_search", {})
    
    def get_chat_config(self):
        """获取聊天配置"""
        return self.config.get("chat", {})
    
    def get_config(self, key=None):
        """
        获取配置项
        
        Args:
            key (str, optional): 配置键名，如果为None则返回全部配置
            
        Returns:
            dict or any: 配置值
        """
        if key is None:
            return self.config
        return self.config.get(key, {})