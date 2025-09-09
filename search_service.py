"""
搜索服务模块
负责处理文档搜索和向量嵌入相关功能
"""

import requests
import streamlit as st
from meilisearch import Client


class SearchService:
    """搜索服务类"""
    
    def __init__(self, config_manager):
        """
        初始化搜索服务
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.embedding_config = config_manager.get_embedding_config()
        self.meilisearch_config = config_manager.get_meilisearch_config()
        
        # 初始化 Meilisearch 客户端
        self.meili_client = Client(
            self.meilisearch_config["url"],
            self.meilisearch_config["api_key"]
        )
    
    def get_embedding(self, query):
        """
        获取文本的向量嵌入表示
        
        Args:
            query (str): 查询文本
            
        Returns:
            list: 向量嵌入
        """
        url = self.embedding_config["url"]
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.embedding_config['api_key']}"
        }
        payload = {
            "texts": [query],
            "model": self.embedding_config["model"]
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except Exception as e:
            st.error(f"获取向量嵌入失败：{str(e)}")
            return None
    
    def search_hybrid(self, query, knowledge_base, top_k, semantic_ratio):
        """
        使用混合搜索（关键词+语义）在 Meilisearch 中搜索文档
        
        Args:
            query (str): 搜索查询
            knowledge_base (str): 知识库名称
            top_k (int): 返回结果数量
            semantic_ratio (float): 语义搜索权重
            
        Returns:
            tuple: (搜索结果列表, 是否成功)
        """
        try:
            # 获取指定知识库的索引
            index = self.meili_client.index(knowledge_base)
            
            # 获取查询文本的向量嵌入
            embedding = self.get_embedding(query)
            if embedding is None:
                return [], False
            
            # 执行混合搜索
            results = index.search(
                query,
                {
                    "vector": embedding,
                    "hybrid": {
                        "semanticRatio": 1 - semantic_ratio,  # 语义搜索权重
                        "embedder": "bge_m3"  # 嵌入模型名称
                    },
                    "limit": top_k  # 返回结果数量限制
                }
            )
            return results.get("hits", []), True
            
        except Exception as e:
            st.error(f"连接 Meilisearch 失败：{str(e)}")
            return [], False
    
    def get_available_indexes(self):
        """
        获取可用的索引列表
        
        Returns:
            list: 索引名称列表
        """
        try:
            indexes = self.meili_client.get_indexes()
            return [index.uid for index in indexes['results']]
        except Exception as e:
            st.error(f"获取索引列表失败：{str(e)}")
            return []