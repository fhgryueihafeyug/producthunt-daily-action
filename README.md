# Product Hunt 每日中文热榜
我已经帮你完成了从动态服务器架构到 Jamstack (静态网站) 架构的迁移。现在你的项目可以直接通过 GitHub Pages 托管，无需任何服务器成本。



以下是完成的更改详情：



### 1. 创建生成器脚本 build.rb

创建了一个新的 Ruby 脚本 build.rb ，它替代了原来的 server.rb 。



- 功能 ：它会扫描 data/ 目录下的所有 Markdown 文件，解析内容，并生成一个包含索引和详情的静态 data.json 文件。

- 结构保持 ：为了兼容现有的前端逻辑，生成的 JSON 保持了与原 API 相同的 { "index": [...], "details": {...} } 结构。

### 2. 更新前端 index.html

修改了 index.html 中的数据获取逻辑。



- 变更 ：将 fetch('/api/data') 改为 fetch('./data.json') 。

- 效果 ：页面现在直接读取静态生成的 JSON 文件，不再依赖后端服务器。同时更新了错误提示信息，使其更符合静态站点的场景。

### 3. 配置 GitHub Action

更新了 .github/workflows/generate_markdown.yml 工作流文件。



- 新增步骤 ：

  1. Set up Ruby : 配置 Ruby 3.0 环境。

  2. Generate JSON Data : 在生成 Markdown 后，运行 ruby build.rb 生成 data.json 。

- 自动部署 ：生成的 data.json 会随 Markdown 文件一起自动提交到仓库，GitHub Pages 会自动部署更新后的内容。
