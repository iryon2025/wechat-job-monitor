# 🚀 超简单部署指南

## 方法一：一键自动部署 (推荐)

只需要运行一个命令，全自动部署！

```bash
python auto_deploy.py
```

脚本会自动：
1. 检查和安装所需工具
2. 登录GitHub
3. 创建仓库
4. 上传代码
5. 配置API密钥
6. 启用自动运行

## 方法二：手动部署 (如果自动部署失败)

### 步骤1：准备GitHub账号
- 访问 [GitHub.com](https://github.com) 注册账号
- 登录后记住您的用户名

### 步骤2：创建新仓库
1. 点击右上角的 "+" 号
2. 选择 "New repository"
3. 仓库名称：`wechat-job-monitor`
4. 设置为 Public
5. 点击 "Create repository"

### 步骤3：上传代码
1. 点击 "uploading an existing file"
2. 将整个项目文件夹拖拽到页面上
3. 或者点击 "choose your files" 选择所有文件
4. 在下方输入提交信息：`初始提交 - 微信公众号招聘信息监控系统`
5. 点击 "Commit changes"

### 步骤4：配置API密钥
1. 进入仓库页面
2. 点击 "Settings" 标签
3. 左侧菜单点击 "Secrets and variables" → "Actions"
4. 点击 "New repository secret"
5. 添加以下secret：
   - Name: `DEEPSEEK_API_KEY`
   - Value: `sk-92d52c5e40fc48bd89bbe1fd60ebb45e`
6. 点击 "Add secret"

### 步骤5：启用Actions
1. 点击 "Actions" 标签
2. 如果显示禁用，点击 "I understand my workflows, go ahead and enable them"
3. 点击左侧的 "微信公众号招聘信息监控"
4. 点击 "Enable workflow"

### 步骤6：运行测试
1. 点击 "Run workflow" 按钮
2. 点击绿色的 "Run workflow"
3. 等待几分钟，查看运行结果

## 方法三：在线编辑器部署

### 使用GitHub Codespaces
1. 在GitHub仓库页面点击绿色的 "Code" 按钮
2. 选择 "Codespaces" 标签
3. 点击 "Create codespace on main"
4. 等待环境加载完成
5. 在终端运行 `python auto_deploy.py`

### 使用Gitpod
1. 在浏览器地址栏输入：`https://gitpod.io/#https://github.com/您的用户名/wechat-job-monitor`
2. 登录Gitpod账号
3. 等待环境加载
4. 在终端运行部署脚本

## 🎯 部署后的效果

### 自动运行
- ✅ 每30分钟自动检查一次
- ✅ 监控"校影"和"深焦DeepFocus"公众号
- ✅ 使用AI识别招聘信息
- ✅ 生成Excel/CSV报告
- ✅ 自动保存到GitHub

### 查看结果
1. 进入仓库的 "Actions" 页面查看运行状态
2. 点击任意一次运行查看详细日志
3. 在 "Artifacts" 区域下载生成的报告文件

### 监控状态
- 🟢 绿色：运行成功
- 🔴 红色：运行失败
- 🟡 黄色：正在运行

## 📧 配置邮件通知 (可选)

如果想接收邮件通知，需要添加以下Secrets：

1. `SMTP_SERVER`: 邮件服务器
   - Gmail: `smtp.gmail.com`
   - QQ邮箱: `smtp.qq.com`
   - 163邮箱: `smtp.163.com`

2. `SMTP_PORT`: 端口号 (通常是 `587`)

3. `SENDER_EMAIL`: 您的邮箱地址

4. `SENDER_PASSWORD`: 邮箱应用密码
   - Gmail: 需要开启两步验证后生成应用密码
   - QQ邮箱: 需要开启SMTP服务获取授权码

5. `RECEIVER_EMAILS`: 接收邮箱 (多个用逗号分隔)

6. `SENDER_NAME`: 发送者名称 (如：`招聘监控系统`)

## 🔧 常见问题

### Q: 部署失败怎么办？
A: 检查以下几点：
1. 确保GitHub账号已登录
2. 确认API密钥正确
3. 检查网络连接
4. 查看Actions页面的错误日志

### Q: 没有收到招聘信息怎么办？
A: 这是正常的，因为：
1. 系统每30分钟检查一次
2. 只有发现新的招聘信息才会发送通知
3. 可以查看Actions页面的运行日志

### Q: 想修改监控的公众号怎么办？
A: 编辑 `config/rss_sources.json` 文件，添加或修改RSS源地址

### Q: 费用是多少？
A: 
- GitHub Actions: 免费 (每月2000分钟)
- DeepSeek API: 1-5元/月
- 总计: 几乎免费

## 🎉 完成！

部署完成后，您的招聘信息监控系统就会24小时自动运行，帮您收集影视行业的招聘信息！

---

💡 **提示**: 如果遇到任何问题，可以查看仓库的 Issues 页面或 Actions 运行日志。