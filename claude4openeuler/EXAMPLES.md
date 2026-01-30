# 使用示例

## 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 设置 API Key
```bash
export DEEPSEEK_API_KEY='sk-xxxxx'
```

### 3. 运行系统
```bash
# 方式 1: 使用启动脚本
./run.sh

# 方式 2: 直接运行客户端
python3 mcp_client.py
```

## 对话示例

### 示例 1: 查找下载信息
```
👤 You: 我想下载 openEuler，在哪里可以找到？

🤖 Assistant: 您可以访问 openEuler 的下载中心。根据搜索结果，
下载页面位于 https://www.openeuler.org/download/

在下载中心，您可以找到：
- 社区版本
- 商业版本
- 不同架构的支持（x86_64, ARM, RISC-V 等）

您需要什么类型的版本？
```

### 示例 2: 查找文档
```
👤 You: 有技术文档吗？

🤖 Assistant: 是的，openEuler 提供了全面的技术文档。
文档中心位于 https://docs.openeuler.org

文档包括：
- 安装指南
- 用户手册
- 开发者指南
- API 参考
- 迁移指南

您对哪方面的文档感兴趣？
```

### 示例 3: 了解社区
```
👤 You: 如何参与 openEuler 社区？

🤖 Assistant: openEuler 社区欢迎各种形式的贡献！
社区页面位于 https://www.openeuler.org/community/

您可以通过以下方式参与：
- 加入 SIG (Special Interest Groups)
- 提交代码贡献
- 参与讨论和问题反馈
- 参加社区活动和会议

社区还提供了详细的贡献指南来帮助新成员入门。
```

### 示例 4: 安全信息
```
👤 You: 在哪里可以查看安全公告？

🤖 Assistant: openEuler 有专门的安全中心。
安全中心位于 https://www.openeuler.org/security/

在安全中心，您可以：
- 查看最新的安全公告
- 获取安全更新
- 了解漏洞修复信息
- 订阅安全通知

建议定期检查安全中心以保持系统安全。
```

## 高级用法

### 搜索特定页面
```
👤 You: 在文档页面搜索 "kernel" 相关内容

🤖 Assistant: [使用 search_openeuler 工具搜索特定 URL]
```

### 获取页面详细信息
```
👤 You: 获取迁移中心的详细信息

🤖 Assistant: [使用 get_page_content 工具获取完整页面内容]
```

### 查看网站结构
```
👤 You: openEuler 网站有哪些主要板块？

🤖 Assistant: [使用 get_main_sections 工具列出所有主要板块]
```

## 常见问题

### Q: 如何退出对话？
A: 输入 `quit`、`exit` 或 `bye`，或按 Ctrl+C

### Q: 支持中文搜索吗？
A: 是的，系统支持中文和英文搜索

### Q: 搜索结果不准确怎么办？
A: 尝试使用更具体的关键词，或者指定要搜索的具体页面 URL

### Q: 可以搜索文档站点吗？
A: 可以，只需在问题中指定 docs.openeuler.org 的 URL

## 技术细节

### MCP Server 工具说明

**search_openeuler**
- 功能: 在指定页面搜索关键词
- 输入: query (必需), url (可选)
- 输出: 匹配片段和相关链接

**get_page_content**
- 功能: 获取页面完整内容
- 输入: url (必需)
- 输出: 标题、内容、链接列表

**get_main_sections**
- 功能: 获取网站主要板块
- 输入: 无
- 输出: 板块列表及描述

### 缓存机制
系统会缓存已访问的页面内容，提高响应速度。缓存在程序运行期间有效。

### 性能优化
- 内容限制: 每个页面最多返回 5000 字符
- 链接限制: 每个页面最多返回 50 个链接
- 搜索结果: 最多返回 5 个匹配片段和 10 个相关链接
