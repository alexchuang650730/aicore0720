# PowerAutomation v4.6.9.7 发布指导

## 🎯 发布前准备

### 1. 确保所有文件已提交到 GitHub

```bash
# 在您的本地 aicore0716 目录中
cd /path/to/your/aicore0716

# 添加所有新文件
git add .

# 提交更改
git commit -m "feat: PowerAutomation v4.6.9.7 统一 MCP 解决方案

- 整合所有相关组件为统一的 claude_router_mcp
- 实现 Claude 工具模式，完全避免模型推理余额消耗
- 集成 K2 服务路由，自动路由 AI 推理任务
- 确保 Claude Code Sync Service 正常工作
- 提供 npm/curl 一键安装方式
- 移除分散的组件目录，统一架构"

# 推送到 GitHub
git push origin main
```

### 2. 验证 GitHub 上的文件

确保以下文件已成功推送到 GitHub：
- ✅ `install_powerautomation_v4697.sh`
- ✅ `package.json`
- ✅ `bin/powerautomation.js`
- ✅ `scripts/` 目录下的所有脚本
- ✅ `core/components/claude_router_mcp/` 完整目录
- ✅ `README.md`
- ✅ `LICENSE`

## 🚀 发布到 npm registry

### 步骤 1: 登录 npm

```bash
# 如果还没有 npm 账户，先注册
npm adduser

# 如果已有账户，登录
npm login
```

### 步骤 2: 验证登录状态

```bash
npm whoami
```

### 步骤 3: 运行发布脚本

```bash
cd /path/to/your/aicore0716

# 干运行（测试发布流程，不实际发布）
node scripts/publish.js --dry-run

# 实际发布
node scripts/publish.js
```

### 步骤 4: 验证发布成功

```bash
# 检查包是否已发布
npm view powerautomation-unified

# 测试安装
npm install -g powerautomation-unified
```

## 📦 手动发布（备选方案）

如果自动发布脚本有问题，可以手动发布：

```bash
cd /path/to/your/aicore0716

# 运行预发布检查
node scripts/prepack.js

# 手动发布
npm publish --access public
```

## 🔧 发布后验证

### 1. 测试 npm 安装

```bash
# 在新的终端或机器上测试
npm install -g powerautomation-unified

# 验证安装
powerautomation --help
powerautomation test
```

### 2. 测试 curl 安装

```bash
# 现在这个命令应该可以工作了
curl -fsSL https://raw.githubusercontent.com/alexchuang650730/aicore0716/main/install_powerautomation_v4697.sh | bash
```

### 3. 验证功能

```bash
# 启动服务
powerautomation start

# 查看状态
powerautomation status

# 测试功能
powerautomation test
```

## 🎉 发布成功后的操作

### 1. 更新 README 徽章

确保 README.md 中的徽章显示正确的版本：
```markdown
[![npm version](https://badge.fury.io/js/powerautomation-unified.svg)](https://badge.fury.io/js/powerautomation-unified)
```

### 2. 创建 GitHub Release

```bash
# 创建 Git 标签
git tag v4.6.9.7
git push origin v4.6.9.7
```

然后在 GitHub 上创建 Release：
1. 访问 https://github.com/alexchuang650730/aicore0716/releases
2. 点击 "Create a new release"
3. 选择标签 `v4.6.9.7`
4. 填写 Release 标题：`PowerAutomation v4.6.9.7 - 统一 MCP 解决方案`
5. 复制 CHANGELOG.md 的内容到描述中
6. 发布 Release

### 3. 宣传和推广

- 📝 更新项目文档
- 🐦 社交媒体宣传
- 📧 通知用户更新

## 🔍 故障排除

### 发布失败的常见原因

1. **版本号已存在**
   ```bash
   # 更新版本号
   npm version patch  # 或 minor, major
   ```

2. **权限问题**
   ```bash
   # 确保有发布权限
   npm owner ls powerautomation-unified
   ```

3. **文件缺失**
   ```bash
   # 检查 package.json 中的 files 字段
   npm pack --dry-run
   ```

4. **网络问题**
   ```bash
   # 检查 npm registry
   npm config get registry
   ```

### 回滚发布

如果需要回滚：
```bash
# 撤销发布（仅在发布后24小时内）
npm unpublish powerautomation-unified@4.6.9.7

# 或者发布修复版本
npm version patch
npm publish
```

## 📞 支持

如果在发布过程中遇到问题：

1. 检查 npm 日志：`~/.npm/_logs/`
2. 查看 GitHub Actions（如果配置了 CI/CD）
3. 联系 npm 支持：https://www.npmjs.com/support

---

## 🎯 快速发布检查清单

- [ ] 所有代码已提交并推送到 GitHub
- [ ] `install_powerautomation_v4697.sh` 在 GitHub 上可访问
- [ ] npm 账户已登录
- [ ] 运行 `node scripts/prepack.js` 通过
- [ ] 运行 `node scripts/publish.js --dry-run` 通过
- [ ] 执行 `node scripts/publish.js` 发布
- [ ] 验证 `npm install -g powerautomation-unified` 成功
- [ ] 测试 `powerautomation test` 功能正常
- [ ] 创建 GitHub Release
- [ ] 更新文档和宣传

完成以上步骤后，PowerAutomation v4.6.9.7 就成功发布了！🎉

