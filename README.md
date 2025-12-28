# 部署在Github上的自动检查苹果App Store应用更新

自动监控App Store应用更新，支持Bark和Telegram Bot推送。

## 功能特性

- ✅ 自动检测App Store应用版本更新
- ✅ 支持Bark推送（iOS）
- ✅ 支持Telegram Bot推送（全平台）
- ✅ 支持多应用同时监控
- ✅ 版本缓存避免重复推送
- ✅ 完全托管在GitHub Actions

## 配置步骤

### 1. 获取App ID

在App Store中找到要监控的应用，复制URL中的数字ID。

例如：`https://apps.apple.com/cn/app/wechat/id414478124` 中的 `414478124`

### 2. 选择推送方式

#### 方式A：使用Bark推送（仅iOS）

1. 在iPhone上安装Bark应用
2. 打开Bark，复制你的推送Key（类似：`xxxxxx/DeviceName`）
3. 在GitHub仓库设置中添加以下Secrets：
   - `PUSH_METHOD` = `bark`
   - `BARK_KEY` = 你的Bark Key
   - `APP_IDS` = 应用ID列表（逗号分隔）

#### 方式B：使用Telegram Bot推送（全平台）

1. **创建Telegram Bot**：
   - 在Telegram中搜索 `@BotFather`
   - 发送 `/newbot` 命令
   - 按提示设置机器人名称和用户名
   - 保存BotFather返回的Bot Token

2. **获取Chat ID**：
   - 给你的Bot发送任意消息
   - 访问 `https://api.telegram.org/bot<你的Bot Token>/getUpdates`
   - 在返回的JSON中找到 `"chat":{"id":123456789}`
   - 这个数字就是你的Chat ID

3. 在GitHub仓库设置中添加以下Secrets：
   - `PUSH_METHOD` = `telegram`
   - `TELEGRAM_BOT_TOKEN` = 你的Bot Token
   - `TELEGRAM_CHAT_ID` = 你的Chat ID
   - `APP_IDS` = 应用ID列表（逗号分隔）

### 3. 修改检查频率（可选）

编辑 `.github/workflows/check-app-update.yml` 中的 cron 表达式：

- `0 * * * *` - 每小时检查一次
- `0 */6 * * *` - 每6小时检查一次
- `0 0 * * *` - 每天检查一次

## Secrets配置清单

| Secret名称 | 必填 | 说明 | 示例 |
|-----------|------|------|------|
| `PUSH_METHOD` | ✅ | 推送方式 | `bark` 或 `telegram` |
| `APP_IDS` | ✅ | App ID列表 | `414478124,123456789` |
| `BARK_KEY` | Bark方式必填 | Bark推送Key | `xxxxxx/iPhone` |
| `TELEGRAM_BOT_TOKEN` | Telegram方式必填 | Bot Token | `123456:ABC-DEF...` |
| `TELEGRAM_CHAT_ID` | Telegram方式必填 | Chat ID | `123456789` |

## 手动触发

进入仓库的 Actions → Check App Store Updates → Run workflow

## 常见问题

**Q: 为什么没有收到推送？**
- 检查Secrets配置是否正确
- 查看Actions运行日志
- 确认应用确实有版本更新

**Q: Telegram推送失败？**
- 确认Bot Token和Chat ID正确
- 检查是否已给Bot发送过消息
- 可以先手动访问API测试

**Q: 如何监控多个应用？**
- 在APP_IDS中用英文逗号分隔多个ID，如：`414478124,123456,789012`
