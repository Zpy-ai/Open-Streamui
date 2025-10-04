"""
UI组件模块
负责处理Streamlit界面组件和布局
"""

import streamlit as st
import time
from openai import OpenAI


class UIComponents:
    """UI组件类"""
    
    def __init__(self, config_manager, ai_service=None):
        """
        初始化UI组件
        
        Args:
            config_manager: 配置管理器实例
            ai_service: AI服务实例（可选）
        """
        self.config_manager = config_manager
        self.search_config = config_manager.get_search_config()
        self.ai_service = ai_service
    
    def render_sidebar(self):
        """
        渲染侧边栏配置界面
        
        Returns:
            tuple: (知识库名称, 语义权重, 返回结果数量, 搜索时间占位符, 结果数量占位符)
        """
        with st.sidebar:
            st.header("搜索设置")
            
            # AI模型选择
            config = self.config_manager.get_config()
            available_providers = []
            
            # 只显示真正的AI服务商配置（排除web_search、embedding、meilisearch等）
            ai_provider_keys = ["openai", "qwen", "deepseek", "claude", "gemini", "kimi", "hunyuan", "doubao"]  # 支持的AI服务商列表
            for provider_key, provider_config in config.items():
                if (isinstance(provider_config, dict) and 
                    "api_key" in provider_config and 
                    provider_key in ai_provider_keys):
                    available_providers.append(provider_key)
            
            if available_providers:
                # 默认使用配置中的默认服务商，如果没有则使用第一个
                default_provider = config.get("default_provider", available_providers[0])
                
                selected_provider = st.selectbox(
                    "🤖 AI模型",
                    options=available_providers,
                    index=available_providers.index(default_provider) if default_provider in available_providers else 0,
                    help="选择要使用的AI模型服务商"
                )
                
                # 显示当前选择的模型信息
                provider_config = config.get(selected_provider, {})
                model_name = provider_config.get("model", "未知模型")
                st.info(f"当前使用: {selected_provider} - {model_name}")
                
                # 更新AI服务配置（如果提供了AI服务实例）
                if self.ai_service and selected_provider != self.ai_service.default_provider:
                    self.ai_service.default_provider = selected_provider
                    self.ai_service.current_provider_config = config.get(selected_provider, {})
                    self.ai_service.client = OpenAI(
                        base_url=self.ai_service.current_provider_config.get("base_url", "https://api.openai.com/v1"),
                        api_key=self.ai_service.current_provider_config.get("api_key", ""),
                    )
                    st.success(f"✅ 已切换到 {selected_provider}")
            else:
                st.warning("⚠️ 未配置任何AI服务商，请前往设置页面进行配置")
            
            st.markdown("---")
            
            # 知识库选择（需与 Meilisearch 中的索引名一致）
            knowledge_base = st.selectbox(
                "知识库",
                [self.search_config["default_knowledge_base"]],
                help="选择要搜索的知识库"
            )
            
            # 语义系数滑块（控制语义搜索与关键词搜索的权重比例）
            semantic_ratio = st.slider(
                "SemanticRatio",
                min_value=0.0,
                max_value=1.0,
                value=self.search_config["default_semantic_ratio"],
                step=0.1,
                help="调整语义匹配权重，0为纯关键词搜索，1为纯语义搜索"
            )
            
            # 返回结果数量
            top_k = st.number_input(
                "返回结果数量(topK)",
                min_value=1,
                max_value=self.search_config["max_top_k"],
                value=self.search_config["default_top_k"],
                step=1,
                help="控制搜索结果条数"
            )
            
            # 状态显示（搜索后动态更新）
            st.markdown("---")
            st.markdown(f"### 当前知识库：{knowledge_base}")
            search_time_placeholder = st.empty()  # 搜索耗时
            result_count_placeholder = st.empty()  # 结果数量
            
        return knowledge_base, semantic_ratio, top_k, search_time_placeholder, result_count_placeholder
    
    def render_main_interface(self):
        """
        渲染搜索界面（已废弃，保留兼容性）
        
        Returns:
            tuple: (搜索查询, 搜索按钮状态)
        """
        # 这个方法已经被主程序中的新布局替代
        # 保留此方法仅为向后兼容
        return "", False
    
    def update_search_status(self, search_time_placeholder, result_count_placeholder, 
                           duration_ms, result_count):
        """
        更新搜索状态显示
        
        Args:
            search_time_placeholder: 搜索时间占位符
            result_count_placeholder: 结果数量占位符
            duration_ms (float): 搜索耗时（毫秒）
            result_count (int): 结果数量
        """
        search_time_placeholder.markdown(f"### 搜索耗时：{duration_ms:.2f} ms")
        result_count_placeholder.markdown(f"### 返回结果数：{result_count} 条")
    
    def render_search_result(self, hit, index, ai_service):
        """
        渲染单个搜索结果
        
        Args:
            hit (dict): 搜索结果项
            index (int): 结果索引
            ai_service: AI服务实例
        """
        # 显示文档标题和基本信息
        st.markdown(f"### {index}. {hit.get('title', '无标题')}")
        st.write(f"🆔 SHA256: {hit.get('_sha256', hit.get('file_sha256', '无'))}")
        st.write(f"👤 作者: {hit.get('author', '无')}")
        st.write(f"🏢 机构: {hit.get('organization', '无')}")
        st.write(f"📊 行业: {hit.get('industry', '无')}")
        st.write(f"📅 发布时间: {hit.get('publish_time', '无')}")
        st.write(f"🔗 来源: {hit.get('source', '无')}")
        
        # 获取文档内容并生成AI摘要和关键词
        content = hit.get('content', '') or hit.get('abstract', '')
        summary, keywords = ai_service.process_content(content)
        
        # 显示AI生成的摘要和关键词（markdown格式需要两个以上空格+\n才能换行）
        st.write(f"📝 千问摘要:  \n{summary}")
        st.write(f"🔑 千问关键词:  \n{keywords}")
        
        # 显示文档链接
        self._render_document_links(hit)
        
        st.divider()  # 分隔线
    
    def _render_document_links(self, hit):
        """
        渲染文档链接
        
        Args:
            hit (dict): 搜索结果项
        """
        pdf_link = hit.get('pdf_link')
        if pdf_link:
            st.markdown(f"[📎 PDF链接]({pdf_link})")
        
        file_url = hit.get('file_url')
        if file_url:
            st.markdown(f"[📁 文件下载]({file_url})")
    
    def render_search_results(self, results, success, ai_service):
        """
        渲染搜索结果列表
        
        Args:
            results (list): 搜索结果列表
            success (bool): 搜索是否成功
            ai_service: AI服务实例
        """
        if success and results:
            for i, hit in enumerate(results, start=1):
                self.render_search_result(hit, i, ai_service)
        elif not results:
            st.info("未找到匹配结果，请尝试其他关键词")
    
    def measure_search_time(self, search_function, *args, **kwargs):
        """
        测量搜索耗时
        
        Args:
            search_function: 搜索函数
            *args: 位置参数
            **kwargs: 关键字参数
            
        Returns:
            tuple: (搜索结果, 耗时毫秒)
        """
        start_time = time.time()
        results = search_function(*args, **kwargs)
        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000
        return results, duration_ms