# 🚀 App Store 更新监控器 V1.0

<div align="center">
<img src="https://img.shields.io/badge/状态-🟢运行中-green?style=flat-square" alt="运行中">
<img src="https://img.shields.io/badge/推送-Bark%20%7C%20Telegram-blue?style=flat-square" alt="推送方式">
<img src="https://img.shields.io/badge/地区-20%2B区-orange?style=flat-square" alt="智能地区">
<img src="https://img.shields.io/badge/频率-每小时/可自定义-purple?style=flat-square" alt="检查频率">
</div>

<br>

**完全托管在GitHub Actions上，自动监控App Store应用更新，智能推送详细版本信息！**

## ✨ **核心功能**

| 🎯 **功能** | ✅ **状态** | 📝 **说明** |
|-------------|------------|-------------|
| **自动版本检测** | ✅ | iTunes API实时查询最新版本 |
| **智能地区识别** | ✅ | 自动匹配20+地区（🇨🇳中国优先） |
| **详细更新信息** | ✅ | 版本号 + 更新内容 + 发布时间 |
| **应用图标显示** | ✅ | Bark推送带官方App图标 |
| **整合推送** | ✅ | 多应用更新一条消息 |
| **版本缓存** | ✅ | 首次初始化，后续只推变化 |
| **双推送支持** | ✅ | Bark(iOS) + Telegram(全平台) |
| **手动触发** | ✅ | Actions页面一键运行 |

## 📱 **推送效果预览**

### **🔥 单个应用更新（详细版）**

标题：🔥 WeChat 有新版本啦！
----------------------------------------
```
📱 WeChat（8.0.51→8.0.52） 📱
地区: 中国 | 更新时间: 2025-12-28 15:45
━━━━━━━━━━━━━━━
✓ 支持新年红包动画
✓ 优化群聊性能
✓ 修复语音通话问题
━━━━━━━━━━━━━━━
[点击跳转 App Store]
```

### **📊 多个应用更新（列表版）**
```
标题：📱 App Store 更新 (3 个)
----------------------------------------
发现以下应用有更新：

📱 WeChat 8.0.51→8.0.52 📱
中国 | 2025-12-28 15:45
支持新年红包动画...

📱 支付宝 10.5.1→10.5.2 📱
中国 | 2025-12-28 16:20
新增扫码支付优化...

📱 QQ 9.2.1→9.2.2 📱
中国 | 2025-12-28 17:10
优化视频通话...
```

## ⚙️ **快速部署（3分钟）** 

### **📦 Step 1: Fork仓库**
```
1. 点击右上角 "Fork" 按钮
2. 等待Fork完成  
3. 进入你的Fork仓库
4. 删除Fork后仓库中的version_cache.json文件！！！
5. 启用Workflow Read and write 路径：仓库Settings → Actions → General → Workflow permissions = Read and write
```

### **🔑 Step 2: 配置Secrets**
> **仓库设置 → Secrets and variables → Actions → New repository secret**

| **名称** | **必填** | **说明** | **示例值** |
|----------|----------|----------|------------|
| `PUSH_METHOD` | ✅ | 推送方式 | `bark` 或 `telegram` |
| `APP_IDS` | ✅ | 应用ID | `414478124,123456789` |
| `BARK_KEY` | Bark必填 | Bark密钥 | `QPT8.../iPhone` |
| `TELEGRAM_BOT_TOKEN` | TG必填 | Bot Token | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | TG必填 | 聊天ID | `123456789` |

#### **Bark配置（iOS）**
```
1. App Store搜索 "Bark" 下载
2. 打开App → 复制推送地址中的Key部分  
3. Secrets中填入 → 立即测试推送成功！
```

#### **Telegram配置（全平台）**
```
1. Telegram搜索 @BotFather → /newbot
2. 设置名称 → 获取 Token
3. 给Bot发消息 → https://api.telegram.org/bot{Token}/getUpdates  
4. 复制 chat.id（不是BOT_TOKEN！！！） → 配置完成
```

### **▶️ Step 3: 立即测试**
```
仓库首页 → Actions → Check App Store Updates → Run workflow
```

## ⏰ **检查频率设置**

编辑 `.github/workflows/check-app-update.yml` 中的 `cron`：

```
# 推荐配置
- cron: '0 * * * *'        # 每小时检查一次
# - cron: '0 */6 * * *'     # 每6小时检查一次  
# - cron: '0 9,21 * * *'    # 早9晚9检查
# - cron: '0 0 * * *'       # 每天午夜检查
```

## 🛠️ **完整Secrets配置示例**

### **仅Bark（推荐iOS用户）**
```
PUSH_METHOD=bark
APP_IDS=414478124,585027354,333903271
BARK_KEY=QPT8gWxxxxxxxxxxxx/iPhone14
```

### **仅Telegram（推荐Android/PC用户）**
```
PUSH_METHOD=telegram
APP_IDS=414478124,585027354,333903271
TELEGRAM_BOT_TOKEN=776xxxxxx:AAHxxxxxx
TELEGRAM_CHAT_ID=123456789
```

## 🔍 **运行日志解读**

```
🚀 App Store 更新监控启动
📢 推送方式: bark
📱 监控: ['414478124']
🔄 首次运行 (缓存: 0 条)

🔍 检查 414478124
✓ [cn] WeChat v8.0.52
📝 初始化: WeChat v8.0.52
💾 缓存已保存 (1 条记录)
✅ 首次运行完成！
```

**第二次运行：**
```
🔄 后续运行 (缓存: 1 条)
✅ 最新: WeChat v8.0.52
😊 一切正常
```

## 🚨 **常见问题**

<details>
<summary>❌ 为什么每次都是首次运行？</summary>

**检查清单：**
1. [ ] `Settings → Actions → General → Workflow permissions = Read and write`
2. [ ] workflow中有 `permissions: contents: write`
3. [ ] 仓库根目录出现 `version_cache.json` 文件
4. [ ] Actions日志最后有 `git push` 成功

</details>

<details>
<summary>❌ 查不到应用信息？</summary>

**测试微信ID：** `APP_IDS=414478124`
```
预期日志：✓ [cn] WeChat v8.0.52
异常日志：✗ 全部失败
```
**解决方案：** 更换App Store地区或检查App ID格式

</details>

<details>
<summary>❌ 收不到推送？</summary>

**Bark：** 浏览器访问 `https://api.day.app/{你的key}/测试`
**Telegram：** 浏览器访问 `https://api.telegram.org/bot{token}/getMe`

</details>

## 📈 **版本历史**

| **版本** | **日期** | **更新内容** |
|----------|----------|--------------|
| V1.0 | 2025-12 | **详细推送+图标+缓存优化** |

## ⭐ **Star支持**

喜欢这个项目？请点个 **Star** 支持一下！⭐

<div align="center">
<img src="https://img.shields.io/github/stars/yourusername/app-store-monitor?style=social" alt="Stars">
</div>

*由 [GitHub Actions](https://github.com/features/actions) 驱动 | Made with ❤️ for DuoJla*
