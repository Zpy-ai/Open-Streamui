"""
AI服务模块
负责处理AI相关功能，如摘要生成和关键词提取
"""

from openai import OpenAI
import streamlit as st


class AIService:
    """AI服务类"""
    
    def __init__(self, config_manager):
        """
        初始化AI服务
        
        Args:
            config_manager: 配置管理器实例
        """
        self.config_manager = config_manager
        self.openai_config = config_manager.get_openai_config()
        
        # 初始化 OpenAI 客户端（通义千问）
        self.client = OpenAI(
            api_key=self.openai_config["api_key"],
            base_url=self.openai_config["base_url"],
        )
    
    def generate_summary(self, text, max_tokens=128):
        """
        使用通义千问生成文本摘要
        
        Args:
            text (str): 需要生成摘要的文本
            max_tokens (int): 最大生成长度
            
        Returns:
            str: 生成的摘要
        """
        prompt = f"请用中文对以下内容生成简明摘要,只需返回摘要，别的任何说明都不返回：\n{text}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.openai_config["model"],
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一个专业的中文摘要助手，只需返回摘要，别的任何说明都不返回。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 控制生成文本的随机性
                max_tokens=max_tokens  # 限制生成文本的最大长度
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"摘要生成失败: {e}"
    
    def extract_keywords(self, text, max_tokens=128):
        """
        使用通义千问生成文本关键词
        
        Args:
            text (str): 需要提取关键词的文本
            max_tokens (int): 最大生成长度
            
        Returns:
            str: 提取的关键词
        """
        prompt = f"请用中文对以下内容生成关键词,只需返回关键词，别的任何说明都不返回：\n{text}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.openai_config["model"],
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一个专业的中文关键词助手，只会返回关键词，别的任何说明都不返回。"
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # 控制生成文本的随机性
                max_tokens=max_tokens  # 限制生成文本的最大长度
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"关键词生成失败: {e}"
    
    def chat_completion(self, messages, temperature=0.7, max_tokens=1000):
        """
        支持聊天对话的AI完成接口
        
        Args:
            messages (list): 对话消息列表
            temperature (float): 生成文本的随机性控制
            max_tokens (int): 最大生成长度
            
        Returns:
            str: AI生成的回答
        """
        try:
            response = self.client.chat.completions.create(
                model=self.openai_config["model"],
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"AI回答生成失败: {e}"
    
    def generate_chat_response(self, user_message, context=None, chat_history=None):
        """
        生成聊天回答，支持上下文和历史对话
        
        Args:
            user_message (str): 用户消息
            context (str, optional): 额外的上下文信息（如搜索结果）
            chat_history (list, optional): 对话历史
            
        Returns:
            str: AI生成的回答
        """
        try:
            # 构建消息列表
            messages = []
            
            # 添加系统消息
            system_content = "你是一个有用的AI助手。请用中文回答用户的问题，提供准确、有用的信息。"
            messages.append({"role": "system", "content": system_content})
            
            # 添加历史对话（限制数量避免token过多）
            if chat_history:
                max_history = min(len(chat_history), 10)  # 最多10条历史消息
                for msg in chat_history[-max_history:]:
                    if msg.get("role") in ["user", "assistant"]:
                        messages.append({
                            "role": msg["role"],
                            "content": msg["content"]
                        })
            
            # 构建当前用户消息
            if context:
                # 有上下文时整合搜索结果
                user_content = f"""基于以下信息回答我的问题：

参考信息：
{context}

我的问题：{user_message}

请根据参考信息回答问题，如果信息不足，请结合你的知识给出最佳回答。"""
            else:
                user_content = user_message
            
            messages.append({"role": "user", "content": user_content})
            
            # 调用聊天完成接口
            return self.chat_completion(messages)
            
        except Exception as e:
            return f"生成聊天回答失败: {e}"
    
    def process_content(self, content):
        """
        处理文档内容，生成摘要和关键词
        
        Args:
            content (str): 文档内容
            
        Returns:
            tuple: (摘要, 关键词)
        """
        if not content:
            return '无内容', '无关键词'
        
        try:
            with st.spinner("正在生成摘要和关键词..."):
                summary = self.generate_summary(content)
                keywords = self.extract_keywords(content)
            return summary, keywords
        except Exception as e:
            st.error(f"处理内容失败：{str(e)}")
            return '处理失败', '处理失败'