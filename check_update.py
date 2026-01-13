import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import requests

try:
    # requests 内部用 urllib3；通常可用
    from urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter
except Exception:
    Retry = None
    HTTPAdapter = None

ITUNES_API = "https://itunes.apple.com/lookup"
BARK_API = "https://api.day.app"
TELEGRAM_API = "https://api.telegram.org/bot"

REGIONS = [
    "cn", "us", "hk", "tw", "jp", "kr", "gb", "sg", "au",
    "de", "fr", "ca", "it", "es", "ru", "br", "mx", "in", "th", "vn"
]

REGION_NAMES = {
    "cn": "中国", "us": "美国", "hk": "香港", "tw": "台湾", "jp": "日本",
    "kr": "韩国", "gb": "英国", "sg": "新加坡", "au": "澳大利亚",
    "de": "德国", "fr": "法国", "ca": "加拿大", "it": "意大利",
    "es": "西班牙", "ru": "俄罗斯", "br": "巴西", "mx": "墨西哥",
    "in": "印度", "th": "泰国", "vn": "越南",
}

TEST_APP_IDS = ["414478124"]  # 微信

# 缓存文件放脚本同目录，避免 cron/工作目录变化导致找不到
CACHE_FILE = Path(__file__).with_name("version_cache.json")

DEFAULT_TIMEOUT = 8


def get_push_method() -> str:
    return os.getenv("PUSH_METHOD", "bark").lower().strip()


def get_bark_key() -> str:
    return os.getenv("BARK_KEY", "").strip()


def get_telegram_config() -> dict:
    return {
        "bot_token": os.getenv("TELEGRAM_BOT_TOKEN", "").strip(),
        "chat_id": os.getenv("TELEGRAM_CHAT_ID", "").strip()
    }


def get_app_ids():
    env_ids = os.getenv("APP_IDS", "")
    if env_ids:
        ids = [i.strip() for i in env_ids.split(",") if i.strip()]
        print(f"📋 从环境变量获取 App ID: {ids}")
        return ids
    print("⚠️ 未设置 APP_IDS，使用测试 ID: 414478124 (微信)")
    return TEST_APP_IDS


def make_session() -> requests.Session:
    s = requests.Session()
    # 友好一点的 UA，减少部分环境的奇怪拦截概率
    s.headers.update({"User-Agent": "AppStoreUpdateMonitor/1.0"})
    if Retry and HTTPAdapter:
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET", "POST"),
            raise_on_status=False,
        )
        adapter = HTTPAdapter(max_retries=retry)
        s.mount("https://", adapter)
        s.mount("http://", adapter)
    return s


def load_version_cache() -> dict:
    try:
        if not CACHE_FILE.exists():
            print("📂 缓存文件不存在 -> 首次运行")
            return {}
        with CACHE_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            print("⚠️ 缓存格式错误（非 dict），重置为空")
            return {}

        print(f"📂 缓存库加载成功，共 {len(data)} 个应用:")
        for app_id, info in list(data.items())[:3]:
            print(f"   {app_id}: v{info.get('version', '?')} ({info.get('app_name', '?')})")
        if len(data) > 3:
            print(f"   ... 还有 {len(data)-3} 个应用")
        return data
    except Exception as e:
        print(f"❌ 加载缓存异常: {e}")
        return {}


def save_version_cache(cache: dict):
    try:
        tmp = CACHE_FILE.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        tmp.replace(CACHE_FILE)  # 原子替换（大多数系统上）
        print(f"💾 缓存已保存到 {CACHE_FILE} ({len(cache)} 条记录)")
    except Exception as e:
        print(f"❌ 保存缓存失败: {e}")


def format_datetime(iso_datetime: str) -> str:
    if not iso_datetime:
        return "未知"
    try:
        dt = datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))
        utc_plus_8 = dt + timedelta(hours=8)
        return utc_plus_8.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return iso_datetime[:16]


def get_app_info_with_region(session: requests.Session, app_id: str):
    try_limit = int(os.getenv("REGION_TRY_LIMIT", "6"))
    regions = REGIONS[:max(1, min(try_limit, len(REGIONS)))]

    print(f"   尝试查询地区: ", end="")
    for i, region in enumerate(regions):
        try:
            if i > 0:
                print(".", end="", flush=True)

            resp = session.get(
                ITUNES_API,
                params={"id": app_id, "country": region},
                timeout=DEFAULT_TIMEOUT
            )
            if resp.status_code != 200:
                continue

            data = resp.json()
            print(f"\n   [{region}] resultCount={data.get('resultCount', 0)}")
            if data.get("resultCount", 0) > 0:
                app = data["results"][0]
                app["detected_region"] = region
                print(f"   ✓ 找到: {app.get('trackName', 'Unknown')} v{app.get('version', '?')}")
                return app
        except Exception as e:
            print(f"\n   [{region}] 异常: {str(e)[:40]}...", end="")
            continue

    print(" ✗ 全部失败")
    return None


def build_app_detail(app_data: dict, show_old_version: bool = False) -> str:
    notes = app_data.get("notes", "暂无更新说明") or "暂无更新说明"
    if len(notes) > 150:
        notes = notes[:147] + "..."

    ver_part = app_data["version"]
    if show_old_version and app_data.get("old_version"):
        ver_part = f"（{app_data['old_version']}→{app_data['version']}）"

    return (
        f"📱 {app_data['name']} {ver_part} 📱\n"
        f"地区: {app_data['region']} | 更新时间: {app_data['release']}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"{notes}"
    )


def send_bark_notification(session: requests.Session, bark_key: str, title: str, content: str, url=None, icon_url=None):
    try:
        data = {
            "title": title,
            "body": content,
            "group": "App Store更新",
            "sound": "bell",
            "isArchive": "1",
        }
        if url:
            data["url"] = url
        if icon_url:
            data["icon"] = icon_url

        resp = session.post(f"{BARK_API}/{bark_key}", data=data, timeout=10)
        ok = (resp.status_code == 200)
        print(f"📱 Bark推送: {'✅成功' if ok else f'❌失败({resp.status_code})'}")
        return ok
    except Exception as e:
        print(f"❌ Bark推送异常: {e}")
        return False


def escape_markdown_v2(text: str) -> str:
    # Telegram MarkdownV2 需要转义这些字符：_ * [ ] ( ) ~ ` > # + - = | { } . !
    if text is None:
        return ""
    special = r"_*[]()~`>#+-=|{}.!\\"
    out = []
    for ch in text:
        if ch in special:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)


def send_telegram_notification(session: requests.Session, bot_token: str, chat_id: str, title: str, content: str):
    try:
        # 使用 MarkdownV2 更稳；把 title/content 都转义
        safe_title = escape_markdown_v2(title)
        safe_content = escape_markdown_v2(content)
        message = f"*{safe_title}*\n\n{safe_content}"

        url = f"{TELEGRAM_API}{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": False,
        }
        resp = session.post(url, json=payload, timeout=10)
        data = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        ok = bool(data.get("ok"))
        print(f"📱 Telegram推送: {'✅成功' if ok else '❌失败'}")
        return ok
    except Exception as e:
        print(f"❌ Telegram推送异常: {e}")
        return False


def send_notification(session: requests.Session, title: str, content: str, url=None, icon_url=None):
    method = get_push_method()
    if method == "bark":
        key = get_bark_key()
        if not key:
            print("⚠️ 跳过推送: 未配置 BARK_KEY")
            return False
        return send_bark_notification(session, key, title, content, url, icon_url)

    if method == "telegram":
        cfg = get_telegram_config()
        if not cfg["bot_token"] or not cfg["chat_id"]:
            print("⚠️ 跳过推送: Telegram配置不全")
            return False
        return send_telegram_notification(session, cfg["bot_token"], cfg["chat_id"], title, content)

    print(f"⚠️ 未知推送方式: {method}")
    return False


def check_updates():
    print("🚀 App Store 更新监控启动")

    app_ids = get_app_ids()
    if not app_ids:
        print("❌ 错误: 没有有效的 App ID")
        return

    print(f"📢 推送方式: {get_push_method()}")
    print(f"📱 要监控 {len(app_ids)} 个应用: {app_ids}")
    print("=" * 60)

    session = make_session()
    cache = load_version_cache()

    new_apps = []
    updated_apps = []

    for idx, app_id in enumerate(app_ids, start=1):
        print(f"\n🔍 [第{idx}/{len(app_ids)}] 检查 {app_id}")

        info = get_app_info_with_region(session, app_id)
        if not info:
            print("   ⚠️ 跳过: 无法获取应用信息")
            continue

        name = info.get("trackName", "Unknown App")
        version = info.get("version", "0.0")
        notes = info.get("releaseNotes", "暂无更新说明")
        url = info.get("trackViewUrl", "")
        release_iso = info.get("currentVersionReleaseDate", "")
        region_code = info.get("detected_region", "us")
        region_name = REGION_NAMES.get(region_code, region_code.upper())
        icon = info.get("artworkUrl100", "")

        release_time = format_datetime(release_iso)

        is_new_app = app_id not in cache
        old_version = cache.get(app_id, {}).get("version", "")

        app_data = {
            "id": app_id,
            "name": name,
            "version": version,
            "region": region_name,
            "icon": icon,
            "old_version": old_version,
            "notes": notes,
            "release": release_time,
            "url": url
        }

        if is_new_app:
            print(f"   📝 新增监控: {name} v{version}")
            new_apps.append(app_data)
        elif old_version != version:
            print(f"   🎉 发现更新: {name} {old_version} → v{version}")
            updated_apps.append(app_data)
        else:
            print(f"   ✅ 最新: {name} v{version}")

        # 无论新增/更新/最新，都刷新缓存（确保 app_name/icon/region 不会老化）
        cache[app_id] = {
            "version": version,
            "app_name": name,
            "region": region_code,
            "icon": icon,
            "updated_at": datetime.now().isoformat(),
        }

    print("\n" + "=" * 60)

    # 推送策略：新增与更新分开推
    if new_apps:
        title = f"📱 新增监控 ({len(new_apps)} 个应用)"
        details = "\n\n".join(build_app_detail(a, show_old_version=False) for a in new_apps)
        content = f"✅ 已添加以下应用到监控列表：\n\n{details}"
        first = new_apps[0]
        send_notification(session, title, content, first["url"], first["icon"])

    if updated_apps:
        if len(updated_apps) == 1:
            a = updated_apps[0]
            title = f"🔥 {a['name']} 有新版本啦！"
            content = build_app_detail(a, show_old_version=True)
            send_notification(session, title, content, a["url"], a["icon"])
        else:
            title = f"📱 App Store 更新 ({len(updated_apps)} 个)"
            details = "\n\n".join(build_app_detail(a, show_old_version=True) for a in updated_apps)
            content = f"发现以下应用有更新：\n\n{details}"
            first = updated_apps[0]
            send_notification(session, title, content, first["url"], first["icon"])

    if not new_apps and not updated_apps:
        print("😊 一切正常，无需通知")

    save_version_cache(cache)


if __name__ == "__main__":
    check_updates()
