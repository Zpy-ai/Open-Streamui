"""
知识库搜索应用主程序
整合所有模块，提供完整的搜索功能和AI聊天功能
"""

import streamlit as st
from datetime import datetime
from openai import OpenAI
from config_manager import ConfigManager
from search_service import SearchService
from ai_service import AIService
from ui_components import UIComponents
from web_search_service import WebSearchService


class KnowledgeSearchApp:
    """知识库搜索应用类"""
    
    def __init__(self):
        """初始化应用"""
        # 初始化各模块
        self.config_manager = ConfigManager()
        self.search_service = SearchService(self.config_manager)
        self.ai_service = AIService(self.config_manager)
        self.ui_components = UIComponents(self.config_manager, self.ai_service)
        self.web_search_service = WebSearchService(self.config_manager)
        
        # 初始化会话状态
        self._init_session_state()
    
    def _init_session_state(self):
        """初始化会话状态"""
        if 'current_page' not in st.session_state:
            st.session_state.current_page = "AI问答"
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        if 'use_web_search' not in st.session_state:
            st.session_state.use_web_search = False
        # 初始化复制状态字典
        if 'copy_states' not in st.session_state:
            st.session_state.copy_states = {}
        # 初始化对话会话管理
        if 'chat_sessions' not in st.session_state:
            st.session_state.chat_sessions = {"默认对话": []}
        if 'current_chat_session' not in st.session_state:
            st.session_state.current_chat_session = "默认对话"
    
    def run(self):
        """运行应用主程序"""
        # 设置页面配置
        st.set_page_config(
            page_title="Open-Streamui",
            page_icon="",
            layout="wide",
            initial_sidebar_state="expanded"  # 展开侧边栏，与知识库搜索保持一致
        )
        
        # 渲染页面导航
        self._render_navigation()
        
        # 根据当前页面渲染对应内容
        if st.session_state.current_page == "知识库搜索":
            self._render_search_page()
        elif st.session_state.current_page == "AI问答":
            self._render_chat_page()
        elif st.session_state.current_page == "设置":
            self._render_settings_page()
    
    def _render_navigation(self):
        """渲染页面导航"""
        # 使用容器和CSS实现右上角标题
        st.markdown(
            """
            <style>
            .title-container {
                display: flex;
                justify-content: flex-end;
                margin-top: -50px;
                margin-bottom: 10px;
                position: relative;
                z-index: 100;
            }
            .app-title {
                color: #1f77b4;
                font-size: 24px;
                font-weight: bold;
                margin: 0;
                padding: 5px 10px;
            }
            </style>
            <div class="title-container">
                <h2 class="app-title">Open-Streamui</h2>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    def _render_search_page(self):
        """渲染知识库搜索页面"""
        # 添加页面标题
        st.markdown(
            "<h2 style='text-align: center; color: #2e8b57; margin-bottom: 1.5rem;'>🔍 知识库搜索</h2>", 
            unsafe_allow_html=True
        )
        
        # 在侧边栏添加页面选择（如果从AI问答页面切换过来）
        with st.sidebar:
            # 页面模式选择
            st.markdown("### 🔍 功能选择")
            page_options = ["AI问答", "知识库搜索", "设置"]
            selected_page = st.radio(
                "选择功能",
                page_options,
                index=page_options.index(st.session_state.current_page),
                key="search_sidebar_page_selector"
            )
            
            # 更新当前页面状态
            if selected_page != st.session_state.current_page:
                st.session_state.current_page = selected_page
                st.rerun()
            
            st.divider()
        
        # 渲染侧边栏
        knowledge_base, semantic_ratio, top_k, search_time_placeholder, result_count_placeholder = (
            self.ui_components.render_sidebar()
        )
        
        # 创建搜索结果容器
        results_container = st.container()
        
        # 在搜索结果容器中显示欢迎信息
        with results_container:
            st.markdown("""
            <div style='text-align: center; padding: 3rem; color: #666; background-color: #f8f9fa; 
                        border-radius: 10px; margin: 2rem 0;'>
                <h3>👋 欢迎使用知识库搜索</h3>
                <p>请在下方输入搜索关键词，我会为您在知识库中查找相关内容</p>
                <p>💡 您可以在侧边栏调整搜索参数来获得更精准的结果</p>
                <p>🔍 支持关键词搜索和语义搜索，系统会自动进行智能匹配</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 将搜索输入框放在最下面
        st.markdown("---")
        st.markdown("### 搜索")
        
        # 搜索输入框和按钮在同一行
        col1, col2 = st.columns([4, 1])
        with col1:
            search_query = st.text_input(
                "请输入搜索关键词", 
                value="AI", 
                help="支持关键词、短语搜索，系统会自动进行语义理解",
                label_visibility="collapsed"
            )
        with col2:
            search_btn = st.button("搜索", type="primary", use_container_width=True)
        
        # 处理搜索逻辑并在结果容器中显示
        if search_btn:
            # 清空容器并显示搜索结果
            results_container.empty()
            with results_container:
                self._handle_search(
                    search_query, knowledge_base, top_k, semantic_ratio,
                    search_time_placeholder, result_count_placeholder
                )
    
    def _render_chat_page(self):
        """渲染AI问答页面"""
        # 添加页面标题
        st.markdown(
            "<h2 style='text-align: center; color: #2e8b57; margin-bottom: 1.5rem;'>💬 AI智能问答</h2>", 
            unsafe_allow_html=True
        )
        
        # 渲染侧边栏
        self._render_chat_sidebar()
        
        # 获取当前对话历史
        current_session = st.session_state.current_chat_session
        current_history = st.session_state.chat_sessions.get(current_session, [])
        
        # 创建对话历史容器
        chat_container = st.container()
        
        # 显示对话历史
        with chat_container:
            # 如果没有对话历史，显示欢迎信息
            if not current_history:
                st.markdown("""
                <div style='text-align: center; padding: 3rem; color: #666; background-color: #f8f9fa; 
                            border-radius: 10px; margin: 2rem 0;'>
                    <h3>👋 欢迎使用AI智能问答</h3>
                    <p>请在下方输入您的问题，我会尽力为您解答</p>
                    <p>💡 您可以在侧边栏选择启用联网搜索来获得更准确的答案</p>
                    <p>🆕 您也可以创建新的对话会话来组织不同的话题</p>
                </div>
                """, unsafe_allow_html=True)
            
            # 显示对话消息
            for i, message in enumerate(current_history):
                if message["role"] == "user":
                    with st.chat_message("user"):
                        st.write(message["content"])
                else:
                    with st.chat_message("assistant"):
                        # 显示AI回答
                        st.write(message["content"])
                        
                        # 创建操作按钮行
                        button_col1, button_col2, button_col3, button_col4 = st.columns([1, 1, 1, 5])
                        
                        with button_col1:
                            # 重新回答按钮
                            if st.button("🔄 重新回答", key=f"regenerate_{current_session}_{i}", help="重新生成这个回答"):
                                # 找到对应的用户问题
                                if i > 0 and current_history[i-1]["role"] == "user":
                                    user_question = current_history[i-1]["content"]
                                    
                                    # 重新生成回答
                                    with st.spinner("正在重新生成回答..."):
                                        response_data = self._generate_ai_response(user_question, st.session_state.use_web_search)
                                    
                                    # 更新历史记录中的回答
                                    st.session_state.chat_sessions[current_session][i] = {
                                        "role": "assistant",
                                        "content": response_data["response"],
                                        "timestamp": datetime.now(),
                                        "search_info": response_data.get("search_info")
                                    }
                                    
                                    st.rerun()
                        
                        with button_col2:
                            # 复制按钮
                            copy_key = f"show_copy_{current_session}_{i}"
                            if st.button("📋 复制", key=f"copy_{current_session}_{i}", help="点击显示可复制的文本"):
                                st.session_state[copy_key] = not st.session_state.get(copy_key, False)
                        
                        with button_col3:
                            # 显示时间戳
                            if message.get("timestamp"):
                                timestamp = message["timestamp"].strftime("%H:%M:%S")
                                st.caption(f"⏰ {timestamp}")
                        
                        # 如果用户点击了复制按钮，显示可复制的文本区域
                        if st.session_state.get(copy_key, False):
                            with st.expander("📋 可复制内容", expanded=True):
                                st.code(message["content"], language="text")
                                st.caption("💡 提示：点击代码框右上角的复制按钮，或选中文本使用 Ctrl+C 复制")
                        
                        # 显示搜索信息
                        if message.get("search_info"):
                            search_info = message["search_info"]
                            if search_info.get("used_search"):
                                st.caption(f"🌐 已使用网络搜索: {search_info.get('query', '')}")
                            elif search_info.get("search_failed"):
                                st.caption("⚠️ 网络搜索失败，使用AI基础知识回答")
        
        # 将用户输入框放在最下面
        st.markdown("---")
        user_input = st.chat_input("请输入您的问题...")
        
        if user_input:
            # 添加用户消息到当前会话
            st.session_state.chat_sessions[current_session].append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now()
            })
            
            # 在对话容器中显示用户消息
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_input)
                
                # 生成AI回答
                with st.chat_message("assistant"):
                    with st.spinner("AI正在思考中..."):
                        response_data = self._generate_ai_response(user_input, st.session_state.use_web_search)
                    
                    # 显示AI回答
                    st.write(response_data["response"])
                    
                    # 显示搜索信息
                    if response_data.get("search_info"):
                        search_info = response_data["search_info"]
                        if search_info.get("used_search"):
                            st.caption(f"🌐 已使用网络搜索: {search_info.get('query', '')}")
                        elif search_info.get("search_failed"):
                            st.caption("⚠️ 网络搜索失败，使用AI基础知识回答")
            
            # 添加AI回答到当前会话
            st.session_state.chat_sessions[current_session].append({
                "role": "assistant",
                "content": response_data["response"],
                "timestamp": datetime.now(),
                "search_info": response_data.get("search_info")
            })
            
            # 刷新页面显示新消息
            st.rerun()
    
    def _render_chat_sidebar(self):
        """渲染AI问答侧边栏"""
        with st.sidebar:
            # 页面模式选择
            st.markdown("### 🔍 功能选择")
            page_options = ["AI问答", "知识库搜索", "设置"]
            selected_page = st.radio(
                "选择功能",
                page_options,
                index=page_options.index(st.session_state.current_page),
                key="sidebar_page_selector"
            )
            
            # 更新当前页面状态
            if selected_page != st.session_state.current_page:
                st.session_state.current_page = selected_page
                st.rerun()
            
            st.divider()
            
            # 对话管理
            st.markdown("### 💬 对话管理")
            
            # 新建对话按钮
            col1, col2 = st.columns([3, 1])
            with col1:
                new_chat_name = st.text_input("新对话名称", placeholder="输入对话名称...", label_visibility="collapsed")
            with col2:
                if st.button("➕", help="新建对话", use_container_width=True):
                    if new_chat_name and new_chat_name not in st.session_state.chat_sessions:
                        st.session_state.chat_sessions[new_chat_name] = []
                        st.session_state.current_chat_session = new_chat_name
                        st.rerun()
                    elif new_chat_name in st.session_state.chat_sessions:
                        st.error("对话名称已存在！")
                    else:
                        # 自动生成对话名称
                        session_count = len(st.session_state.chat_sessions)
                        auto_name = f"对话 {session_count + 1}"
                        while auto_name in st.session_state.chat_sessions:
                            session_count += 1
                            auto_name = f"对话 {session_count + 1}"
                        st.session_state.chat_sessions[auto_name] = []
                        st.session_state.current_chat_session = auto_name
                        st.rerun()
            
            # 对话会话列表
            st.markdown("### 📋 对话列表")
            for session_name in st.session_state.chat_sessions.keys():
                col1, col2 = st.columns([4, 1])
                with col1:
                    # 显示会话名称和消息数量
                    message_count = len(st.session_state.chat_sessions[session_name])
                    is_current = session_name == st.session_state.current_chat_session
                    
                    if st.button(
                        f"{'🔸' if is_current else '🔹'} {session_name} ({message_count})",
                        key=f"session_{session_name}",
                        help=f"切换到 {session_name}",
                        use_container_width=True,
                        type="primary" if is_current else "secondary"
                    ):
                        st.session_state.current_chat_session = session_name
                        st.rerun()
                
                with col2:
                    # 删除对话按钮
                    if session_name != "默认对话":  # 保护默认对话不被删除
                        if st.button("🗑️", key=f"delete_{session_name}", help=f"删除 {session_name}"):
                            del st.session_state.chat_sessions[session_name]
                            if st.session_state.current_chat_session == session_name:
                                st.session_state.current_chat_session = "默认对话"
                            st.rerun()
            
            st.divider()
            
            # AI设置
            st.markdown("### ⚙️ AI设置")
            
            # 模型选择
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
                
                # 更新AI服务配置
                if hasattr(self, 'ai_service') and selected_provider != self.ai_service.default_provider:
                    self.ai_service.default_provider = selected_provider
                    self.ai_service.current_provider_config = config.get(selected_provider, {})
                    self.ai_service.client = OpenAI(
                        base_url=self.ai_service.current_provider_config.get("base_url", "https://api.openai.com/v1"),
                        api_key=self.ai_service.current_provider_config.get("api_key", ""),
                    )
                    st.success(f"✅ 已切换到 {selected_provider}")
            else:
                st.warning("⚠️ 未配置任何AI服务商，请前往设置页面进行配置")
            
            # 联网搜索开关
            use_web_search = st.checkbox(
                "🌐 启用联网搜索",
                value=st.session_state.use_web_search,
                help="开启后将使用网络搜索增强AI回答"
            )
            st.session_state.use_web_search = use_web_search
            
            # 状态显示
            if use_web_search:
                st.success("🌐 联网搜索模式")
            else:
                st.info("🤖 基础AI模式")
            
            # 清空当前对话按钮
            current_session = st.session_state.current_chat_session
            if st.button("🗑️ 清空当前对话", help=f"清空 {current_session} 的所有消息", use_container_width=True):
                st.session_state.chat_sessions[current_session] = []
                st.rerun()
    
    def _handle_search(self, search_query, knowledge_base, top_k, semantic_ratio,
                      search_time_placeholder, result_count_placeholder):
        """
        处理搜索请求
        
        Args:
            search_query (str): 搜索查询
            knowledge_base (str): 知识库名称
            top_k (int): 返回结果数量
            semantic_ratio (float): 语义搜索权重
            search_time_placeholder: 搜索时间占位符
            result_count_placeholder: 结果数量占位符
        """
        # 执行搜索并测量耗时
        (results, success), duration_ms = self.ui_components.measure_search_time(
            self.search_service.search_hybrid,
            search_query, knowledge_base, top_k, semantic_ratio
        )
        
        # 更新搜索状态显示
        self.ui_components.update_search_status(
            search_time_placeholder, result_count_placeholder,
            duration_ms, len(results)
        )
        
        # 渲染搜索结果
        self.ui_components.render_search_results(results, success, self.ai_service)
    
    def _generate_ai_response(self, user_message: str, use_web_search: bool = False) -> dict:
        """
        生成AI回答
        
        Args:
            user_message (str): 用户消息
            use_web_search (bool): 是否使用网络搜索
            
        Returns:
            dict: 包含回答和搜索信息的字典
        """
        search_info = {"used_search": False, "search_failed": False}
        search_context = None
        
        # 如果启用网络搜索
        if use_web_search:
            try:
                search_result = self.web_search_service.search_web(user_message)
                if search_result.get("success", False):
                    search_context = self.web_search_service.format_search_results(search_result)
                    search_info = {
                        "used_search": True,
                        "search_failed": False,
                        "query": user_message
                    }
                else:
                    search_info = {
                        "used_search": False,
                        "search_failed": True,
                        "query": user_message,
                        "error": search_result.get("error", "搜索失败")
                    }
            except Exception as e:
                search_info = {
                    "used_search": False,
                    "search_failed": True,
                    "query": user_message,
                    "error": f"搜索异常: {str(e)}"
                }
        
        # 生成AI回答
        try:
            if search_context:
                # 有搜索上下文时的提示词
                prompt = f"""基于以下网络搜索结果和用户问题，请提供准确、有用的回答。

搜索结果：
{search_context}

用户问题：{user_message}

请根据搜索结果回答用户问题，如果搜索结果不足以回答问题，请结合你的知识给出最佳回答。回答要准确、简洁、有用。"""
            else:
                # 无搜索上下文时直接回答
                prompt = user_message
            
            # 构建消息历史
            messages = [
                {
                    "role": "system",
                    "content": "你是一个有用的AI助手。请用中文回答用户的问题，提供准确、有用的信息。"
                }
            ]
            
            # 添加最近的对话历史（最多10轮）
            current_session = st.session_state.current_chat_session
            current_history = st.session_state.chat_sessions.get(current_session, [])
            recent_history = current_history[-20:] if len(current_history) > 20 else current_history
            for msg in recent_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": prompt})
            
            # 调用AI服务生成回答
            response = self.ai_service.client.chat.completions.create(
                model=self.ai_service.current_provider_config.get("model", "gpt-3.5-turbo"),
                messages=messages,
                temperature=0.7,
                max_tokens=1500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            return {
                "response": ai_response,
                "search_info": search_info,
                "success": True
            }
        
        except Exception as e:
            return {
                "response": f"抱歉，生成回答时发生错误: {str(e)}",
                "search_info": search_info,
                "success": False
            }

    def _render_settings_page(self):
        """渲染设置页面"""
        # 添加页面标题
        st.markdown(
            "<h2 style='text-align: center; color: #2e8b57; margin-bottom: 1.5rem;'>⚙️ 系统设置</h2>", 
            unsafe_allow_html=True
        )
        
        # 在侧边栏添加页面选择
        with st.sidebar:
            # 页面模式选择
            st.markdown("### 🔍 功能选择")
            page_options = ["AI问答", "知识库搜索", "设置"]
            selected_page = st.radio(
                "选择功能",
                page_options,
                index=page_options.index(st.session_state.current_page),
                key="settings_sidebar_page_selector"
            )
            
            # 更新当前页面状态
            if selected_page != st.session_state.current_page:
                st.session_state.current_page = selected_page
                st.rerun()
            
            st.divider()
        
        # 设置页面内容
        st.markdown("### 🔧 AI服务商配置")
        
        # 获取当前配置
        config = self.config_manager.config
        
        # 创建表单用于配置AI服务商
        with st.form("ai_provider_config"):
            st.markdown("#### OpenAI配置")
            
            # OpenAI配置
            openai_base_url = st.text_input(
                "OpenAI Base URL",
                value=config.get("openai", {}).get("base_url", ""),
                help="OpenAI API的基础URL，留空使用默认值"
            )
            
            openai_api_key = st.text_input(
                "OpenAI API Key",
                value=config.get("openai", {}).get("api_key", ""),
                type="password",
                help="OpenAI API密钥"
            )
            
            openai_model = st.text_input(
                "OpenAI模型",
                value=config.get("openai", {}).get("model", "gpt-3.5-turbo"),
                help="使用的OpenAI模型名称"
            )
            
            st.markdown("---")
            st.markdown("#### 其他AI服务商配置")
            
            # 添加新服务商配置
            st.markdown("##### 添加新服务商")
            
            new_provider_name = st.text_input(
                "服务商名称",
                placeholder="例如：DeepSeek、Claude等",
                help="新AI服务商的名称"
            )
            
            new_provider_base_url = st.text_input(
                "Base URL",
                placeholder="例如：https://api.deepseek.com/v1",
                help="新服务商的API基础URL"
            )
            
            new_provider_api_key = st.text_input(
                "API Key",
                placeholder="输入API密钥",
                type="password",
                help="新服务商的API密钥"
            )
            
            new_provider_model = st.text_input(
                "模型名称",
                placeholder="例如：deepseek-chat",
                help="新服务商的模型名称"
            )
            
            # 提交按钮
            submit_button = st.form_submit_button("💾 保存配置")
            
            if submit_button:
                # 更新配置
                updated_config = config.copy()
                
                # 更新OpenAI配置
                if "openai" not in updated_config:
                    updated_config["openai"] = {}
                
                updated_config["openai"]["base_url"] = openai_base_url
                updated_config["openai"]["api_key"] = openai_api_key
                updated_config["openai"]["model"] = openai_model
                
                # 添加新服务商配置
                if new_provider_name and new_provider_base_url and new_provider_api_key and new_provider_model:
                    provider_key = new_provider_name.lower().replace(" ", "_")
                    if provider_key not in updated_config:
                        updated_config[provider_key] = {}
                    
                    updated_config[provider_key]["base_url"] = new_provider_base_url
                    updated_config[provider_key]["api_key"] = new_provider_api_key
                    updated_config[provider_key]["model"] = new_provider_model
                    
                    st.success(f"✅ 已添加 {new_provider_name} 服务商配置")
                
                # 保存配置
                try:
                    self.config_manager.save_config(updated_config)
                    st.success("✅ 配置保存成功！")
                    
                    # 重新初始化AI服务以应用新配置
                    self.ai_service = AIService(self.config_manager)
                    st.info("🔄 AI服务已重新初始化，新配置已生效")
                    
                except Exception as e:
                    st.error(f"❌ 保存配置时发生错误: {str(e)}")
        
        # 显示当前已配置的服务商
        st.markdown("### 📋 已配置的服务商")
        
        provider_count = 0
        for provider_key, provider_config in config.items():
            if isinstance(provider_config, dict) and "api_key" in provider_config:
                provider_count += 1
                with st.expander(f"🔧 {provider_key.upper()} 配置", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.text_input(
                            f"{provider_key} Base URL",
                            value=provider_config.get("base_url", ""),
                            key=f"view_{provider_key}_base_url",
                            disabled=True
                        )
                        st.text_input(
                            f"{provider_key} 模型",
                            value=provider_config.get("model", ""),
                            key=f"view_{provider_key}_model",
                            disabled=True
                        )
                    
                    with col2:
                        st.text_input(
                            f"{provider_key} API Key",
                            value="*" * 20 if provider_config.get("api_key") else "",
                            key=f"view_{provider_key}_api_key",
                            disabled=True
                        )
                        
                        # 删除按钮
                        if provider_key != "openai":  # 保护OpenAI配置不被删除
                            if st.button(f"🗑️ 删除 {provider_key}", key=f"delete_{provider_key}"):
                                updated_config = config.copy()
                                del updated_config[provider_key]
                                try:
                                    self.config_manager.save_config(updated_config)
                                    st.success(f"✅ 已删除 {provider_key} 配置")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ 删除配置时发生错误: {str(e)}")
        
        if provider_count == 0:
            st.info("ℹ️ 当前没有配置任何AI服务商")
        
        # 配置使用说明
        st.markdown("---")
        st.markdown("### 📖 使用说明")
        
        st.markdown("""
        **配置说明：**
        
        1. **OpenAI配置** - 系统默认使用的AI服务商
        2. **添加新服务商** - 支持配置其他兼容OpenAI API的AI服务商
        3. **保存配置** - 点击保存按钮后配置将立即生效
        
        **支持的AI服务商：**
        - OpenAI (默认)
        - DeepSeek
        - Claude (需要兼容OpenAI API)
        - 智谱AI
        - 百度文心一言
        - 阿里通义千问
        - 其他兼容OpenAI API的服务
        
        **注意事项：**
        - API密钥将安全保存到本地配置文件
        - 修改配置后需要重新初始化AI服务
        - 确保Base URL格式正确（如：https://api.deepseek.com/v1）
        """)


def main():
    """主函数"""
    app = KnowledgeSearchApp()
    app.run()


if __name__ == "__main__":
    main()