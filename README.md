# 知识库搜索系统

这是一个基于 Streamlit 的模块化知识库搜索系统，支持混合搜索（关键词+语义搜索）、AI摘要生成和智能问答功能。  
![ai-chat](https://github.com/Zpy-ai/Open-Streamui/blob/main/images/ai-chat.png)
## 功能特性

- 🔍 **混合搜索**：结合关键词搜索和语义搜索
- 💬 **AI智能问答**：支持基础AI问答和联网搜索增强
- 🌐 **联网搜索**：可选择启用网络搜索增强AI回答
- 🗂️ **多会话管理**：支持创建、切换、删除多个独立对话会话
- 🔄 **智能操作**：每个AI回答都支持重新生成和复制功能
- 🎛️ **侧边栏统一控制**：页面切换、功能设置全部集中在侧边栏
- 🎨 **简洁界面**：专注核心功能，移除不必要的统计信息
- 📱 **响应式设计**：自适应不同屏幕尺寸，优化显示效果
- 📝 **AI摘要**：使用AI服务自动生成文档摘要
- 🔑 **关键词提取**：自动提取文档关键词
- ⚡ **实时搜索**：快速响应的搜索体验
- 🏗️ **模块化架构**：清晰的代码结构，易于维护和扩展
- 🤖 **多AI服务商支持**：支持OpenAI、通义千问、DeepSeek、Claude、Gemini、Kimi、腾讯混元、豆包等主流AI服务商

## 项目结构

```
├── ai.py                    # 主程序入口
├── knowledge_search_app.py  # 主应用程序类
├── config_manager.py        # 配置管理模块
├── search_service.py        # 搜索服务模块
├── ai_service.py           # AI服务模块
├── web_search_service.py   # 网络搜索服务模块
├── ui_components.py        # UI组件模块
├── config.json             # 实际配置文件
├── config.template.json    # 配置模板文件
├── requirements.txt        # 依赖包列表
└── README.md              # 说明文档
```

## 模块说明

### 核心模块

1. **ConfigManager** (`config_manager.py`)
   - 负责加载和管理应用程序配置
   - 提供统一的配置访问接口

2. **SearchService** (`search_service.py`)
   - 处理文档搜索和向量嵌入
   - 封装Meilisearch混合搜索功能

3. **AIService** (`ai_service.py`)
   - 处理AI相关功能
   - 提供摘要生成和关键词提取服务

4. **UIComponents** (`ui_components.py`)
   - 管理Streamlit界面组件
   - 提供可复用的UI渲染方法

5. **WebSearchService** (`web_search_service.py`)
   - 处理网络搜索功能
   - 提供联网搜索API调用和结果格式化

6. **KnowledgeSearchApp** (`knowledge_search_app.py`)
   - 主应用程序类
   - 整合所有模块，协调应用流程
   - 提供知识库搜索和AI问答两个主要功能页面

## 安装和配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置应用
```bash
# 复制配置模板
cp config.template.json config.json

# 编辑配置文件，填入实际的服务信息
```

### 3. 配置文件说明
编辑 `config.json` 文件，填入你的实际配置信息：

- **openai**: OpenAI系列模型配置
  - `api_key`: 你的API密钥
  - `base_url`: API基础URL
  - `model`: 使用的模型名称

- **qwen**: 通义千问API配置
  - `api_key`: 你的通义千问API密钥
  - `base_url`: API基础URL
  - `model`: 使用的模型名称

- **deepseek**: DeepSeek模型配置
  - `api_key`: 你的DeepSeek API密钥
  - `base_url`: API基础URL
  - `model`: 使用的模型名称

- **claude**: Claude模型配置
  - `api_key`: 你的Claude API密钥
  - `base_url`: API基础URL
  - `model`: 使用的模型名称

- **gemini**: Google Gemini模型配置
  - `api_key`: 你的Gemini API密钥
  - `base_url`: API基础URL
  - `model`: 使用的模型名称

- **kimi**: 月之暗面Kimi模型配置
  - `api_key`: 你的Kimi API密钥
  - `base_url`: API基础URL
  - `model`: 使用的模型名称

- **hunyuan**: 腾讯混元模型配置
  - `api_key`: 你的腾讯混元API密钥
  - `base_url`: API基础URL
  - `model`: 使用的模型名称

- **doubao**: 豆包模型配置
  - `api_key`: 你的豆包API密钥
  - `base_url`: API基础URL
  - `model`: 使用的模型名称

- **meilisearch**: Meilisearch搜索引擎配置
  - `url`: Meilisearch服务器地址
  - `api_key`: Meilisearch API密钥

- **embedding**: 向量嵌入服务配置
  - `url`: 向量嵌入服务地址
  - `api_key`: 向量嵌入服务API密钥
  - `model`: 嵌入模型名称

- **search**: 搜索默认配置
  - `default_knowledge_base`: 默认知识库名称
  - `default_semantic_ratio`: 默认语义搜索权重
  - `default_top_k`: 默认返回结果数量
  - `max_top_k`: 最大返回结果数量

- **web_search**: 网络搜索配置
  - `url`: 网络搜索服务地址
  - `api_key`: 网络搜索API密钥
  - `default_tool`: 默认搜索工具（如quark_search）
  - `timeout`: 搜索请求超时时间

- **chat**: AI问答配置
  - `max_history_length`: 最大对话历史长度
  - `max_message_length`: 最大消息长度
  - `default_web_search_enabled`: 默认是否启用网络搜索

## 运行应用

```bash
streamlit run ai.py
```

## 架构优势

### 1. 模块化设计
- 每个模块职责单一，便于维护
- 松耦合设计，易于测试和扩展
- 清晰的依赖关系

### 2. 配置管理
- 统一的配置管理
- 支持不同环境的配置
- 敏感信息与代码分离

### 3. 服务分层
- UI层：负责界面展示
- 服务层：处理业务逻辑
- 配置层：管理应用配置

### 4. 可扩展性
- 易于添加新的搜索引擎
- 支持多种AI服务提供商
- 灵活的UI组件系统

## 开发指南

### 添加新功能
1. 在相应的服务模块中添加方法
2. 在UI组件中添加界面元素
3. 在主应用中整合新功能

### 自定义配置
1. 在配置文件中添加新的配置项
2. 在ConfigManager中添加访问方法
3. 在相应服务中使用新配置

### 扩展AI服务
系统已内置支持多种AI服务商，包括：
- OpenAI系列模型
- 通义千问
- DeepSeek
- Claude
- Google Gemini
- 月之暗面Kimi
- 腾讯混元
- 豆包

如需添加新的AI服务商：
1. 在配置文件中添加相应的服务商配置
2. 确保配置包含 `api_key`、`base_url` 和 `model` 字段
3. 在 `ui_components.py` 和 `knowledge_search_app.py` 的 `ai_provider_keys` 列表中添加新的服务商键名
4. 系统会自动识别并显示在AI模型选择器中

## 注意事项

- 确保配置文件 `config.json` 存在且格式正确
- 确保所有服务（Meilisearch、向量嵌入服务、通义千问API）都可正常访问
- 知识库名称需要与Meilisearch中的索引名称一致
- 建议在生产环境中使用环境变量管理敏感配置
