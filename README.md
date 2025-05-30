# GitHub搜索Agent

基于LangChain的智能GitHub搜索工具，用于在GitHub中搜索特定的commit或pull request。

## 功能特性

- **配置管理**：支持创建、修改、删除搜索配置
- **智能关键词生成**：使用AI根据自然语言描述生成搜索关键词
- **多条件筛选**：支持语言限制、文件过滤、AI内容判断
- **Token管理**：支持多个GitHub token轮换使用，避免API限制
- **分段搜索**：自动分时间段搜索，避免结果过多
- **结果保存**：搜索结果保存为JSON格式，包含完整信息
- **日志记录**：详细的操作日志，便于追踪和调试

## 安装说明

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量：
创建 `.env` 文件，设置OpenAI API密钥：
```
OPENAI_API_KEY=your_openai_api_key_here
```

3. 配置GitHub Tokens：
运行程序后，通过Token管理功能添加GitHub Personal Access Tokens。

## 使用方法

1. 启动程序：
```bash
python main.py
```

2. 首次使用：
   - 先在"Token管理"中添加GitHub tokens
   - 在"配置管理"中创建搜索配置
   - 在"启动搜索"中执行搜索

3. 配置说明：
   - **语言限制**：如python、javascript等，对应GitHub搜索中的"lang:"
   - **筛选条件**：用自然语言描述要搜索的内容，AI会生成相应的关键词和判断条件
   - **文件过滤**：正则表达式，用于筛选包含特定文件修改的commit/PR
   - **结果文件**：保存搜索结果的JSON文件名

## 项目结构

```
collect_data_from_github/
├── main.py                 # 主程序入口
├── github_agent.py         # GitHub Agent主类
├── config_manager.py       # 配置管理模块
├── token_manager.py        # Token管理模块
├── ai_helper.py           # AI助手模块
├── github_searcher.py     # GitHub搜索模块
├── requirements.txt       # Python依赖
├── README.md              # 项目说明
├── DevelopGuide.txt       # 开发指南
├── configs/               # 配置文件目录
├── results/               # 搜索结果目录
└── logs/                  # 日志文件目录
```

## 搜索结果格式

搜索结果保存为JSON数组，每个元素包含：

```json
[
  {
    "id": 1,
    "title": "commit/PR标题",
    "url": "GitHub链接",
    "type": "commit/pull_request",
    "repository": "仓库全名",
    "date": "创建日期",
    "author": "作者"
  }
]
```

## 注意事项

1. **API限制**：
   - GitHub API有速率限制，建议配置多个tokens
   - OpenAI API调用会产生费用，请合理使用

2. **搜索策略**：
   - 程序会自动分时间段搜索，避免结果过多
   - AI判断会跳过diff过大的提交，节省token

3. **安全性**：
   - GitHub tokens具有敏感性，请妥善保管
   - 不要将tokens提交到代码仓库

## 常见问题

1. **GitHub API错误**：
   - 检查token是否有效
   - 确认token有足够的权限
   - 检查网络连接

2. **OpenAI API错误**：
   - 检查API密钥是否正确
   - 确认账户有足够余额
   - 检查网络连接

3. **搜索结果为空**：
   - 调整搜索关键词
   - 放宽筛选条件
   - 检查日期范围

## 开发说明

本项目遵循开发指南 `DevelopGuide.txt` 中的要求实现，主要特性：

- 使用LangChain框架
- 模块化设计，便于维护和扩展
- 完整的错误处理和日志记录
- 用户友好的交互界面
- 灵活的配置管理系统 