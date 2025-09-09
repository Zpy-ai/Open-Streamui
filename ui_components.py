"""
UI组件模块
负责处理Streamlit界面组件和布局
"""

import streamlit as st
import time


class UIComponents:
    """UI组件类"""
    
    def __init__(self, config_manager):
        """
        初始化UI组件
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.search_config = config_manager.get_search_config()
    
    def render_sidebar(self):
        """
        渲染侧边栏配置界面
        
        Returns:
            tuple: (知识库名称, 语义权重, 返回结果数量, 搜索时间占位符, 结果数量占位符)
        """
        with st.sidebar:
            st.header("搜索设置")
            
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
        渲染搜索界面
        
        Returns:
            tuple: (搜索查询, 搜索按钮状态)
        """
        # 搜索界面布局
        search_query = st.text_input(
            "请输入搜索关键词", 
            value="AI", 
            help="支持关键词、短语搜索，系统会自动进行语义理解"
        )
        search_btn = st.button("搜索", type="primary")
        
        return search_query, search_btn
    
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