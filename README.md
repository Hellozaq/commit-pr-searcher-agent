# GitHub搜索Agent

在GitHub中搜索特定commit/pr的工具，用户指定初筛规则，之后AI进一步筛选，最后的结果保存在json文件，便于人工做最后的筛选。

## 适用案例
例如，在Github中，搜集Python项目中在2024年创建的所有关于“修复反序列化漏洞”的commit/pr

## 功能特性

- **配置管理**：支持创建、修改、删除搜索配置
- **智能关键词生成**：使用AI根据自然语言描述生成搜索关键词
- **多条件筛选**：支持程序语言限制、文件过滤、AI内容判断
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
运行程序后，通过Token管理功能添加GitHub Personal Access Tokens

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

4. 返回上一步
   - 可以Ctrl+C返回上一步菜单或退出

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
├── configs/               # 配置文件目录
├── results/               # 搜索结果目录
└── logs/                  # 日志文件目录
```

## 搜索结果格式

搜索结果保存为JSON数组，每个元素包含：

```json
[
  {
    "id": 1(从1编号), 
    "title": "commit/PR标题", 
    "url": "GitHub链接",
    "type": "commit/pull_request",
    "repository": "仓库全名",
    "date": "创建日期",
    "author": "作者", 
    "checked": 0(默认为0，建议0表示未检查或不通过，1表示通过，2表示存疑), 
    "note": "默认为空，便于后续人工添加备注"
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

3. **语言限制**：
   - 搜索pr时会添加语言限制
   - 搜索commit时，不支持语言限制，所以建议在“文件过滤”中添加特定语言代码源文件的过滤表达式

