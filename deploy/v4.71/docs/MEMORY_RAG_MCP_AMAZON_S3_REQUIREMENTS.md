# Memory RAG MCP / Amazon S3 需求文档

**版本**: PowerAutomation v4.8  
**创建日期**: 2025-07-16  
**最后更新**: 2025-07-16  

---

## 📋 **文档概述**

本文档详细描述了 PowerAutomation v4.8 中 Memory RAG MCP 和 Amazon S3 集成的完整需求、架构设计和实现规范。

### **核心目标**
- 实现企业级的记忆管理和 RAG 检索系统
- 集成 AWS S3 提供可靠的云端存储
- 支持模式感知的个性化学习适配
- 确保零余额消耗的成本优化架构

---

## 🏗️ **系统架构**

### **整体架构图**
```
用户请求 
    ↓
claude_router_mcp (统一入口)
    ↓
smart_routing_mcp (智能决策)
    ↓
┌─────────────────┬─────────────────┐
│   K2Router      │ IntegrationManager │
│   ↓             │   ↓               │
│ Kimi K2 API     │ RAG + S3          │
│ (免费)          │ (企业级存储)        │
└─────────────────┴─────────────────┘
    ↓
LearningAdapter (模式感知个性化)
    ↓
个性化的最终回答给用户
```

### **核心组件关系**
- **memoryos_mcp**: 核心记忆引擎，包含 RAG 和 S3 功能
- **aws_bedrock_mcp**: 独立的 RAG 服务，专注于文档处理和检索
- **LearningAdapter**: 模式感知的个性化层

---

## 🧠 **Memory RAG MCP 需求**

### **核心功能需求**

#### **1. 记忆管理系统**
- ✅ **多类型记忆存储**
  - 情节记忆 (episodic)
  - 语义记忆 (semantic)  
  - 程序记忆 (procedural)
  - 工作记忆 (working)
  - Claude 交互记忆 (claude_interaction)
  - 用户偏好记忆 (user_preference)

- ✅ **记忆生命周期管理**
  - 自动重要性评分
  - 访问频率追踪
  - 30天 TTL 自动清理
  - 记忆压缩和归档

#### **2. RAG 检索系统**
- ✅ **向量嵌入支持**
  - SentenceTransformer (all-MiniLM-L6-v2)
  - 384维向量空间
  - 相似度阈值: 0.7

- ✅ **FAISS 向量索引**
  - IndexFlatIP 内积索引
  - 毫秒级检索性能
  - 支持增量更新

- ✅ **混合检索策略**
  - 向量相似度检索
  - 记忆重要性排序
  - 智能结果去重和排序

#### **3. 文档处理能力**
- ✅ **多格式支持**
  - 文本文档: TXT, MD, PDF
  - 代码文件: PY, JS, JAVA, CPP, GO
  - 结构化数据: JSON, YAML, XML

- ✅ **智能分块策略**
  - 语义完整性保持
  - 可配置分块大小 (默认 1000 字符)
  - 重叠处理 (默认 200 字符)

### **性能需求**
- **查询响应时间**: < 100ms (单次查询)
- **并发处理能力**: 20+ 并发查询
- **文档索引速度**: 50个文档 < 30秒
- **内存使用限制**: < 500MB

---

## ☁️ **Amazon S3 集成需求**

### **存储架构需求**

#### **1. 存储桶配置**
- ✅ **存储桶命名**: `powerautomation-memory-storage`
- ✅ **区域设置**: `us-east-1` (默认)
- ✅ **存储类别**: `STANDARD_IA` (成本优化)
- ✅ **版本控制**: 启用版本控制
- ✅ **服务器端加密**: AES256

#### **2. 数据组织结构**
```
powerautomation-memory-storage/
├── projects/
│   ├── {project_id}/
│   │   ├── memories/
│   │   ├── documents/
│   │   └── contexts/
├── users/
│   ├── {user_id}/
│   │   ├── preferences/
│   │   └── learning_data/
└── system/
    ├── embeddings/
    └── indexes/
```

#### **3. 成本优化策略**
- ✅ **GZIP 压缩**: 减少 60-80% 存储空间
- ✅ **生命周期管理**: 自动转换到更便宜的存储类别
- ✅ **智能分层**: 根据访问频率自动优化
- ✅ **预估成本**: ~$55/月 (1000个项目)

### **同步和备份需求**
- ✅ **混合存储模式**: 本地 + S3 双重保障
- ✅ **增量同步**: 仅同步变更数据
- ✅ **自动备份**: 可配置定时备份
- ✅ **灾难恢复**: 完整的数据恢复能力

---

## 🎯 **模式感知的 LearningAdapter**

### **模式识别需求**

#### **1. Claude Code Tool 模式** 👨‍🏫
```
触发条件: 
- 当前工具 = Claude Code Tool
- 当前模型 = Claude

角色定位: 专业导师 (教师模型)

个性化策略:
- 深度技术解释和分析
- 严谨的代码审查和建议
- 详细的最佳实践指导
- 学术级别的专业回答风格
- 提供完整的学习路径
```

#### **2. 其他模式** 🤖
```
触发条件:
- 当前工具 ≠ Claude Code Tool
- 当前模型 = K2 或其他

角色定位: 智能助手

个性化策略:
- 快速实用的回答
- 简洁的代码示例
- 效率优先的建议
- 轻松友好的交流风格
- 聚焦问题解决
```

### **个性化功能需求**

#### **1. 用户偏好学习**
- ✅ **技术栈偏好识别**
  - 编程语言偏好
  - 框架和工具偏好
  - 代码风格偏好

- ✅ **交流风格适配**
  - 回答详细程度
  - 技术深度级别
  - 示例代码复杂度

#### **2. 上下文感知优化**
- ✅ **项目上下文集成**
  - 当前项目技术栈
  - 项目复杂度级别
  - 团队协作模式

- ✅ **历史交互学习**
  - 用户问题模式
  - 成功解决方案记录
  - 错误和改进记录

### **模式切换逻辑**
```python
class ModeAwareLearningAdapter:
    def detect_current_mode(self, context):
        """检测当前模式"""
        current_tool = context.get("current_tool")
        current_model = context.get("current_model")
        
        if current_tool == "claude_code_tool" and current_model == "claude":
            return "teacher_mode"
        else:
            return "assistant_mode"
    
    def personalize_response(self, response, context):
        """根据模式个性化回答"""
        mode = self.detect_current_mode(context)
        
        if mode == "teacher_mode":
            return self.apply_teacher_personalization(response, context)
        else:
            return self.apply_assistant_personalization(response, context)
```

---

## 🔧 **技术实现规范**

### **memoryos_mcp 组件规范**

#### **1. MemoryEngine 扩展**
```python
class MemoryEngine:
    def __init__(self, 
                 db_path: str = "memoryos.db", 
                 max_memories: int = 10000,
                 enable_rag: bool = True, 
                 enable_s3: bool = False, 
                 s3_config: Dict[str, Any] = None):
        # 核心功能实现
```

#### **2. 必需方法**
- `add_document_to_rag(doc_id, content, metadata)` - 添加文档到 RAG
- `rag_query(query, top_k, memory_types)` - RAG 查询
- `get_rag_statistics()` - RAG 统计信息
- `sync_to_s3()` - 同步到 S3
- `restore_from_s3()` - 从 S3 恢复

### **aws_bedrock_mcp 组件规范**

#### **1. 核心组件**
- `bedrock_manager.py` - AWS Bedrock 管理
- `rag_service.py` - RAG 服务核心
- `knowledge_base_manager.py` - 知识库管理
- `document_processor.py` - 文档处理
- `integration_manager.py` - 集成管理
- `k2_router.py` - Kimi K2 路由
- `smart_routing_mcp.py` - 智能路由 MCP

#### **2. MCP 协议支持**
- 标准 MCP Server 接口
- Tool 注册和调用
- Resource 管理
- 错误处理和日志

### **LearningAdapter 扩展规范**

#### **1. 模式感知接口**
```python
class LearningAdapter:
    def detect_mode(self, context) -> str
    def get_user_preferences(self, user_id) -> Dict
    def apply_personalization(self, response, mode, preferences) -> str
    def learn_from_interaction(self, interaction_data) -> None
```

#### **2. 个性化策略**
- 教师模式策略 (Claude Code Tool)
- 助手模式策略 (其他工具)
- 用户偏好适配
- 上下文感知优化

---

## 📊 **成本效益分析**

### **成本结构**

#### **1. AWS S3 存储成本**
```
存储成本 (STANDARD_IA):
- 1TB 数据: ~$23/月
- 查询成本: ~$75/月 (750,000次查询)
- 总计: ~$98/月

优化后成本:
- GZIP 压缩: 减少 60-80%
- 智能分层: 额外节省 20%
- 预估总成本: ~$55/月
```

#### **2. LLM 调用成本**
```
Kimi K2 (免费):
- 输入/输出: $0
- API 调用: $0
- 总计: $0/月

vs Claude 3 Haiku:
- 输入: $187.5/月
- 输出: $937.5/月
- 总计: $1,125/月

节省: 100%
```

#### **3. 年度成本对比**
```
Memory RAG MCP + S3 + K2: $660/年
vs 商用 RAG 解决方案: $120,000-336,000/年
vs 自建方案: $200,000-500,000/年

节省: 99.4-99.7%
```

---

## 🧪 **测试需求**

### **功能测试**
- ✅ MemoryEngine RAG 功能测试
- ✅ AWS S3 存储和同步测试
- ✅ 文档处理和索引测试
- ✅ 查询性能和准确性测试
- ✅ 模式感知个性化测试

### **性能测试**
- ✅ 并发查询压力测试 (20+ 并发)
- ✅ 大规模文档索引测试 (1000+ 文档)
- ✅ 内存使用监控 (< 500MB)
- ✅ 响应时间基准测试 (< 100ms)

### **集成测试**
- ✅ MCP 组件协调测试
- ✅ 跨组件数据流测试
- ✅ 错误处理和恢复测试
- ✅ 端到端工作流测试

---

## 📚 **部署和配置**

### **环境要求**
```
Python 依赖:
- sentence-transformers
- faiss-cpu
- boto3
- aiohttp
- sqlite3

AWS 配置:
- AWS CLI 配置
- IAM 权限设置
- S3 存储桶创建
```

### **配置文件示例**
```json
{
  "memory_engine": {
    "db_path": "memoryos.db",
    "max_memories": 10000,
    "enable_rag": true,
    "enable_s3": true
  },
  "rag_config": {
    "embedding_model": "all-MiniLM-L6-v2",
    "vector_dimension": 384,
    "similarity_threshold": 0.7,
    "max_results": 10
  },
  "s3_config": {
    "bucket_name": "powerautomation-memory-storage",
    "region": "us-east-1",
    "storage_class": "STANDARD_IA",
    "enable_encryption": true
  },
  "learning_adapter": {
    "enable_mode_awareness": true,
    "teacher_mode_depth": "detailed",
    "assistant_mode_style": "concise"
  }
}
```

### **部署步骤**
1. **环境准备**: 安装依赖和配置 AWS
2. **组件初始化**: 初始化 memoryos_mcp 和 aws_bedrock_mcp
3. **数据迁移**: 导入现有数据和文档
4. **功能测试**: 运行完整测试套件
5. **性能调优**: 根据实际使用情况优化配置
6. **监控部署**: 启用监控和告警

---

## 🔄 **维护和升级**

### **日常维护**
- ✅ **数据备份**: 每日自动备份到 S3
- ✅ **性能监控**: 实时监控查询性能和资源使用
- ✅ **日志分析**: 定期分析错误日志和使用模式
- ✅ **成本监控**: 监控 AWS 成本和使用量

### **升级路径**
- ✅ **版本兼容**: 保持向后兼容性
- ✅ **数据迁移**: 自动数据格式升级
- ✅ **功能扩展**: 支持新的 RAG 算法和模型
- ✅ **性能优化**: 持续优化查询和存储性能

---

## 📋 **验收标准**

### **功能验收**
- [ ] MemoryEngine 支持完整的 RAG 功能
- [ ] AWS S3 集成正常工作
- [ ] 模式感知的 LearningAdapter 正确识别和切换
- [ ] 所有 MCP 组件正常协调工作
- [ ] 文档处理和查询功能完整

### **性能验收**
- [ ] 查询响应时间 < 100ms
- [ ] 支持 20+ 并发查询
- [ ] 内存使用 < 500MB
- [ ] 文档索引速度达标

### **成本验收**
- [ ] 月度成本 < $100
- [ ] 相比商用方案节省 > 99%
- [ ] Kimi K2 零余额消耗

### **质量验收**
- [ ] 所有测试用例通过
- [ ] 代码覆盖率 > 80%
- [ ] 文档完整性检查通过
- [ ] 安全性审计通过

---

## 📞 **支持和联系**

### **技术支持**
- **文档位置**: 
  - `core/components/memoryos_mcp/MEMORY_RAG_MCP_AMAZON_S3_REQUIREMENTS.md`
  - `core/components/aws_bedrock_mcp/MEMORY_RAG_MCP_AMAZON_S3_REQUIREMENTS.md`
  - `docs/MEMORY_RAG_MCP_AMAZON_S3_REQUIREMENTS.md`

### **相关文档**
- PowerAutomation v4.8 开发计划
- AWS Bedrock MCP API 文档
- PowerAutomation v4.8 用户指南
- 测试报告和性能基准

---

**文档版本**: v1.0  
**最后更新**: 2025-07-16  
**下次审查**: 2025-08-16

