# Deploy 目錄結構規範

## 目錄組織原則

```
deploy/
├── v4.71/          # 版本 4.71 - Memory RAG 版本
│   ├── mobile/     # 移動端部署文件
│   ├── desktop/    # 桌面端部署文件
│   ├── web/        # Web 端部署文件
│   └── docs/       # 版本文檔
│
├── v4.73/          # 版本 4.73 - MCP-Zero 版本
│   ├── mobile/     
│   ├── desktop/    
│   ├── web/        
│   └── docs/       
│
├── v4.74/          # 未來版本
│   └── ...
│
├── common/         # 通用部署資源
│   ├── scripts/    # 通用腳本
│   ├── configs/    # 通用配置
│   └── templates/  # 模板文件
│
└── latest/         # 指向最新穩定版本的符號鏈接
```

## 版本目錄內容

每個版本目錄應包含：

### 1. mobile/ - 移動端部署
- iOS 應用打包文件
- Android APK
- React Native 配置
- 移動端特定腳本

### 2. desktop/ - 桌面端部署  
- Electron 應用
- macOS .app 包
- Windows .exe 安裝程序
- Linux AppImage
- 桌面端配置文件

### 3. web/ - Web 端部署
- 前端構建文件 (dist/)
- nginx 配置
- Docker 文件
- K8s 部署清單
- CDN 配置

### 4. docs/ - 版本文檔
- README.md
- CHANGELOG.md
- API 文檔
- 部署指南
- 故障排除

## 遷移計劃

1. **第一步**: 將 `deployment/v4.71/` 移動到 `deploy/v4.71/`
2. **第二步**: 將 `deployment/v4.73/` 移動到 `deploy/v4.73/`
3. **第三步**: 整理通用腳本到 `deploy/common/`
4. **第四步**: 刪除舊的 `deployment/` 目錄
5. **第五步**: 創建 `latest` 符號鏈接指向 `v4.73`

## 文件命名規範

- 安裝腳本: `install_[platform]_v[version].sh`
- 配置文件: `config_[component]_[env].json`
- 文檔: `[COMPONENT]_[TYPE]_v[version].md`

## 版本控制

- 每個版本都應該是獨立的，包含該版本所需的所有文件
- 避免跨版本引用
- 使用 Git tags 標記每個版本發布

## 自動化部署

```bash
# 一鍵部署命令示例
./deploy/v4.73/desktop/install_macos.sh
./deploy/v4.73/web/deploy_to_aws.sh
./deploy/v4.73/mobile/build_ios.sh
```