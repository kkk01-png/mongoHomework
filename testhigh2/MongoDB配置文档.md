# Windows系统MongoDB 7.0.31配置指南

## 目录
1. [下载与安装MongoDB 7.0.31](#1-下载与安装mongodb-7031)
2. [启动MongoDB服务](#2-启动mongodb服务)
3. [配置环境变量](#3-配置环境变量可选)
4. [连接MongoDB并创建数据库](#4-连接mongodb并创建数据库)
5. [在Spring Boot项目中配置连接](#5-在spring-boot项目中配置连接)
6. [数据模型设计](#6-数据模型设计)
7. [性能优化](#7-性能优化)
8. [常见问题排查](#8-常见问题排查)
9. [MongoDB 7.0新特性](#9-mongodb-70新特性)

---

## 1. 下载与安装MongoDB 7.0.31

### 1.1 下载MongoDB Community Server 7.0.31

1. 访问 [MongoDB官网下载页](https://www.mongodb.com/try/download/community)
2. 选择 **Version**: 7.0.31
3. 选择 **Platform**: Windows x64
4. 选择 **Package**: MSI
5. 点击下载

### 1.2 安装MongoDB 7.0.31

1. 运行下载的MSI安装包（如：`mongodb-windows-x86_64-7.0.31-signed.msi`）
2. 在欢迎页面点击"Next"
3. 接受许可协议，点击"Next"
4. 选择"Complete"安装类型，点击"Next"
5. 在"Service Configuration"页面：
   - 勾选"Install MongoDB as a service"
   - 选择"Run service as Network Service user"
   - Service Name: MongoDB
   - Data Directory: `D:\MongoDB\data`（可自定义，建议设置为D盘）
   - Log Directory: `D:\MongoDB\log`（可自定义，建议设置为D盘）
6. 在"MongoDB Compass"页面，可选择是否安装Compass（推荐安装）
7. 点击"Install"开始安装
8. 完成安装后点击"Finish"

### 1.3 验证安装

1. 打开命令提示符（以管理员身份运行）
2. 执行命令：`mongod --version`
   - 预期输出：`db version v7.0.31`
3. 执行命令：`mongo --version` 或 `mongosh --version`
   - MongoDB 7.0默认使用mongosh作为shell工具

---

## 2. 启动MongoDB服务

### 2.1 检查服务状态

1. 打开"服务"管理工具（Win+R，输入`services.msc`）
2. 找到"MongoDB"服务（注意：服务名称不再包含"Server"）
3. 确保服务状态为"已启动"，启动类型为"自动"

### 2.2 手动启动服务

如果服务未自动启动：

1. 右键点击"MongoDB"服务
2. 选择"启动"

### 2.3 使用命令行启动（开发环境）

```bash
# 启动MongoDB（带配置文件，推荐）
mongod --config "C:\Program Files\MongoDB\Server\7.0\bin\mongod.cfg"

# 或直接指定数据和日志目录（适用于自定义路径）
mongod --dbpath "D:\MongoDB\data" --logpath "D:\MongoDB\log\mongod.log" --logappend
```

---

## 3. 配置环境变量（可选）

### 3.1 打开环境变量设置

1. 右键"此电脑" → "属性" → "高级系统设置" → "环境变量"
2. 在"系统变量"中找到"Path"，点击"编辑"

### 3.2 添加MongoDB路径

1. 点击"新建"，输入MongoDB的bin目录路径：
   ```
   C:\Program Files\MongoDB\Server\7.0\bin
   ```
2. 点击"确定"保存

### 3.3 验证配置

打开新的命令提示符，执行：
```bash
mongosh
```
应成功进入MongoDB shell。

---

## 4. 连接MongoDB并创建数据库

### 4.1 连接MongoDB

**方法1：使用mongosh（推荐）**
```bash
mongosh
```

**方法2：使用连接字符串**
```bash
mongosh "mongodb://localhost:27017"
```

### 4.2 创建数据库和集合

```javascript
// 创建数据库
use github_analysis

// 创建项目集合
db.createCollection("projects")

// 创建所有者集合
db.createCollection("owners")

// 创建组织集合
db.createCollection("organizations")

// 创建提交集合
db.createCollection("commits")

// 创建贡献者集合
db.createCollection("contributors")

// 创建分析结果集合
db.createCollection("analysis_results")

// 创建检索记录集合
db.createCollection("search_records")
```

### 4.3 创建索引

```javascript
// 项目集合索引
db.projects.createIndex({ "full_name": 1 }, { unique: true })
db.projects.createIndex({ "language": 1 })
db.projects.createIndex({ "stars_count": -1 })
db.projects.createIndex({ "updated_at": -1 })
db.projects.createIndex({ "quality_score": -1 })
db.projects.createIndex({ "long_term_value": -1 })
db.projects.createIndex({ "category": 1 })

// 所有者集合索引
db.owners.createIndex({ "login": 1 }, { unique: true })
db.owners.createIndex({ "type": 1 })

// 组织集合索引
db.organizations.createIndex({ "login": 1 }, { unique: true })
db.organizations.createIndex({ "activity_score": -1 })
db.organizations.createIndex({ "tech_depth": -1 })
db.organizations.createIndex({ "main_tech_stacks": 1 })

// 提交集合索引
db.commits.createIndex({ "project_id": 1 })
db.commits.createIndex({ "date": -1 })
db.commits.createIndex({ "author": 1 })

// 贡献者集合索引
db.contributors.createIndex({ "project_id": 1 })
db.contributors.createIndex({ "contributions": -1 })
db.contributors.createIndex({ "login": 1 })

// 分析结果集合索引
db.analysis_results.createIndex({ "analysis_type": 1 })
db.analysis_results.createIndex({ "period": 1 })
db.analysis_results.createIndex({ "created_at": -1 })

// 检索记录集合索引
db.search_records.createIndex({ "query": "text" })
db.search_records.createIndex({ "query_type": 1 })
db.search_records.createIndex({ "created_at": -1 })
db.search_records.createIndex({ "validated": 1 })
```

---

## 5. 在Spring Boot项目中配置连接

### 5.1 添加依赖

在`pom.xml`中添加MongoDB依赖：

```xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-data-mongodb</artifactId>
</dependency>

<!-- 若需要MongoDB 7.0新特性支持，可指定MongoDB驱动版本 -->
<dependency>
    <groupId>org.mongodb</groupId>
    <artifactId>mongodb-driver-sync</artifactId>
    <version>4.11.0</version>
</dependency>
```

### 5.2 配置application.properties

```properties
# MongoDB配置
spring.data.mongodb.uri=mongodb://localhost:27017/github_analysis

# 连接池配置（MongoDB 7.0推荐配置）
spring.data.mongodb.auto-index-creation=true
spring.data.mongodb.connection-timeout=10000
spring.data.mongodb.socket-timeout=30000
spring.data.mongodb.max-connection-life-time=3600000
spring.data.mongodb.max-connection-idle-time=600000
```

### 5.3 配置application.yml（推荐）

```yaml
spring:
  data:
    mongodb:
      uri: mongodb://localhost:27017/github_analysis
      auto-index-creation: true
      connection-timeout: 10000
      socket-timeout: 30000
      max-connection-life-time: 3600000
      max-connection-idle-time: 600000
```

### 5.4 测试连接

1. 启动Spring Boot应用
2. 查看日志，确认MongoDB连接成功

---

## 6. 数据模型设计

### 6.1 项目集合（projects）

```javascript
{
  "_id": ObjectId,
  "name": "vue",
  "full_name": "vuejs/vue",
  "owner": ObjectId("..."),
  "description": "🖖 Vue.js - 渐进式 JavaScript 框架",
  "language": "JavaScript",
  "stars_count": 205000,
  "forks_count": 33000,
  "open_issues_count": 324,
  "created_at": ISODate("2013-07-29T00:00:00Z"),
  "updated_at": ISODate("2023-06-15T00:00:00Z"),
  "topics": ["javascript", "vue", "frontend", "framework"],
  "license": "MIT",
  "watchers_count": 205000,
  "size": 29000,
  "default_branch": "main",
  "category": "Web",
  "quality_score": 0.85,
  "long_term_value": 0.92
}
```

### 6.2 所有者集合（owners）

```javascript
{
  "_id": ObjectId,
  "login": "vuejs",
  "type": "Organization",
  "avatar_url": "https://avatars.githubusercontent.com/u/6128107?v=4",
  "url": "https://github.com/vuejs",
  "repos_count": 100,
  "followers_count": 20000
}
```

### 6.3 组织集合（organizations）

```javascript
{
  "_id": ObjectId,
  "login": "google",
  "name": "Google",
  "description": "Google's GitHub organization",
  "avatar_url": "https://avatars.githubusercontent.com/u/1342004?v=4",
  "url": "https://github.com/google",
  "repos_count": 2000,
  "members_count": 10000,
  "created_at": ISODate("2012-03-10T00:00:00Z"),
  "activity_score": 0.95,
  "tech_depth": 0.92,
  "main_tech_stacks": ["Python", "JavaScript", "Java", "Go"]
}
```

### 6.4 提交集合（commits）

```javascript
{
  "_id": ObjectId,
  "project_id": ObjectId("..."),
  "sha": "a1b2c3d4e5f6...",
  "author": ObjectId("..."),
  "message": "feat: add new feature",
  "date": ISODate("2023-06-15T10:30:00Z"),
  "additions": 150,
  "deletions": 20
}
```

### 6.5 贡献者集合（contributors）

```javascript
{
  "_id": ObjectId,
  "login": "contributor_username",
  "avatar_url": "https://avatars.githubusercontent.com/u/1234567?v=4",
  "contributions": 500,
  "project_id": ObjectId("...")
}
```

### 6.6 分析结果集合（analysis_results）

```javascript
{
  "_id": ObjectId,
  "analysis_type": "language_trend",
  "analysis_data": {
    "period": "monthly",
    "data": [
      {"month": "2023-01", "JavaScript": 35000, "Python": 28000, "Java": 22000},
      {"month": "2023-02", "JavaScript": 36000, "Python": 29500, "Java": 22500}
    ],
    "predictions": {
      "2023-07": {"JavaScript": 38000, "Python": 32000, "Java": 23000}
    }
  },
  "period": "monthly",
  "created_at": ISODate("2023-06-15T12:00:00Z"),
  "accuracy": 0.93
}
```

### 6.7 检索记录集合（search_records）

```javascript
{
  "_id": ObjectId,
  "query": "find machine learning projects in Python",
  "query_type": "natural_language",
  "results": [
    {
      "project_id": ObjectId("..."),
      "project_name": "scikit-learn",
      "match_score": 0.92,
      "quality_score": 0.95
    }
  ],
  "match_score": 0.88,
  "validated": true,
  "validation_result": {
    "accuracy": 0.91,
    "recall": 0.87,
    "precision": 0.93
  },
  "created_at": ISODate("2023-06-15T10:00:00Z")
}
```

---

## 7. 性能优化

### 7.1 内存配置

1. 打开MongoDB配置文件：`C:\Program Files\MongoDB\Server\7.0\bin\mongod.cfg`
2. 修改内存配置（根据服务器内存调整）：

```yaml
storage:
  dbPath: D:\MongoDB\data
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4  # 根据实际内存调整，建议设置为物理内存的50%
```

### 7.2 日志配置

在`mongod.cfg`中配置日志路径：

```yaml
systemLog:
  destination: file
  path: "D:\\MongoDB\\log\\mongod.log"
  logAppend: true
  logRotate: reopen
  verbosity: 0
```

### 7.3 连接池配置（MongoDB 7.0推荐）

```yaml
net:
  port: 27017
  bindIp: 127.0.0.1

processManagement:
  windowsService:
    serviceName: MongoDB
    displayName: MongoDB
    description: MongoDB Server
```

### 7.4 定期维护

```javascript
// 查看数据库状态
use github_analysis
db.stats()

// 集合压缩（MongoDB 7.0推荐使用compact）
db.runCommand({ compact: "projects" })
db.runCommand({ compact: "analysis_results" })

// 索引重建（必要时）
db.projects.reIndex()
```

### 7.5 监控工具

1. **MongoDB Compass**（推荐）：可视化管理数据库
2. **mongosh内置命令**：
   ```javascript
   // 查看服务器状态
   db.serverStatus()
   
   // 查看当前操作
   db.currentOp()
   
   // 查看慢查询日志
   db.getProfilingStatus()
   ```

---

## 8. 常见问题排查

### 8.1 服务启动失败

- 检查数据目录权限（确保Network Service用户有读写权限）
- 查看日志文件：`D:\MongoDB\log\mongod.log`（根据实际配置路径调整）
- 确保端口27017未被占用（使用`netstat -ano | findstr :27017`检查）
- 检查是否已安装Visual C++ Redistributable（MongoDB 7.0依赖）

### 8.2 连接超时

- 检查MongoDB服务是否运行
- 验证连接字符串是否正确
- 检查防火墙是否允许27017端口（入站规则）
- 尝试使用`127.0.0.1`代替`localhost`

### 8.3 mongosh命令找不到

- 确保已配置环境变量
- 或使用完整路径：`"C:\Program Files\MongoDB\Server\7.0\bin\mongosh.exe"`

### 8.4 索引问题

- 使用`db.collection.getIndexes()`查看索引
- 对常用查询创建适当的索引
- 避免创建过多索引（会影响写入性能）

### 8.5 数据备份与恢复

```bash
# 导出数据库
mongodump --db github_analysis --out C:\backup\mongodb\20230615

# 导入数据库
mongorestore --db github_analysis C:\backup\mongodb\20230615\github_analysis

# 压缩备份（MongoDB 7.0新特性）
mongodump --db github_analysis --archive=C:\backup\mongodb\github_analysis.archive.gz --gzip
```

---

## 9. MongoDB 7.0新特性

### 9.1 重要改进

| 特性 | 说明 |
|------|------|
| **mongosh默认shell** | 取代旧版`mongo`命令，提供更好的交互体验和语法支持 |
| **增强的查询优化器** | 改进查询计划生成，提升复杂查询性能 |
| **时间序列集合增强** | 更好的时序数据支持，适合趋势分析场景 |
| **事务增强** | 支持更大的事务范围和更好的并发控制 |
| **安全增强** | 默认禁用TLS 1.0/1.1，强制使用更安全的加密协议 |

### 9.2 兼容性注意事项

1. **驱动版本**：建议使用MongoDB驱动4.10+版本
2. **旧版工具**：`mongo`命令已移除，使用`mongosh`替代
3. **配置文件**：部分旧配置项已废弃，参考新版配置格式
4. **索引限制**：集合最大索引数从64增加到128

---

通过以上步骤，您可以在Windows系统上成功配置MongoDB 7.0.31，为GitHub开源项目分析平台提供科研级的数据存储支持。
