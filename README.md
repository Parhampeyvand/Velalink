# VelaLink

**English below · فارسی در ادامه**

VelaLink turns a Linux computer with a wired Internet connection into a Wi-Fi
hotspot. Connected devices can use the Internet directly or pass their traffic
through a private VLESS/Xray tunnel. The computer's own Internet connection is
kept outside the VPN tunnel.

## Features

- Shares Ethernet through a dedicated Wi-Fi hotspot.
- Optional transparent VLESS VPN layer for connected devices only.
- Uses a dedicated `nftables` table (`simple_hotspot`) and leaves unrelated
  Docker and firewall rules alone.
- Refuses to start if another hotspot manager already controls the same Wi-Fi
  adapter.
- Includes `check`, `start`, `status`, and `stop` commands.

## Requirements

Linux with `hostapd`, `dnsmasq`, `nftables`, `iw`, and Python 3. Install Xray
as well when enabling the VLESS VPN layer.

## Quick start

```bash
cp config.example.json config.json
chmod 600 config.json
sudo python3 hotspot.py check --config config.json
sudo python3 hotspot.py start --config config.json
sudo python3 hotspot.py status --config config.json
sudo python3 hotspot.py stop --config config.json
```

Edit `config.json` before starting. Set the Ethernet interface, Wi-Fi adapter,
hotspot name, and password to match your system.

## VLESS VPN

Set `vpn.enabled` to `true` and put a standard VLESS share link in
`vpn.vless_uri`. VelaLink supports TCP, WebSocket, and gRPC transports with
TLS or Reality. VPN traffic is transparent for devices connected to the
hotspot; the host computer itself keeps using its normal connection.

## Security notes

`config.json` may contain a Wi-Fi password and a private VLESS link. It is
ignored by Git on purpose—never commit or share it. Use the included
`config.example.json` as a safe public template.

## Start automatically after boot

Install the included systemd unit, then enable it once:

```bash
sudo install -m 644 velalink.service /etc/systemd/system/velalink.service
sudo systemctl daemon-reload
sudo systemctl enable --now velalink.service
```

## Modern local control panel

VelaLink also includes a modern, right-to-left Persian web panel. Install and
start its local-only service, then open `http://127.0.0.1:8091` in a browser:

```bash
sudo install -m 644 velalink-panel.service /etc/systemd/system/velalink-panel.service
sudo systemctl daemon-reload
sudo systemctl enable --now velalink-panel.service
```

The panel listens only on the local computer and provides start, stop, restart,
status, and configuration controls.

---

## فارسی

VelaLink یک کامپیوتر لینوکسی با اینترنت کابل را به هات‌اسپات Wi‑Fi تبدیل
می‌کند. دستگاه‌های متصل می‌توانند اینترنت را مستقیم بگیرند یا ترافیکشان را از
تونل خصوصی VLESS/Xray عبور دهند. اینترنت خود کامپیوتر وارد تونل نمی‌شود.

### قابلیت‌ها

- اشتراک اینترنت کابل از طریق هات‌اسپات Wi‑Fi.
- لایهٔ اختیاری VPN شفاف برای دستگاه‌های متصل، بدون تغییر اینترنت کامپیوتر.
- استفاده از جدول مستقل `nftables` با نام `simple_hotspot`؛ بدون دست‌کاری
  قوانین Docker و ابزارهای دیگر.
- جلوگیری از اجرا هنگام فعال‌بودن هات‌اسپات دیگری روی همان آداپتور Wi‑Fi.
- فرمان‌های بررسی، روشن‌کردن، دیدن وضعیت و خاموش‌کردن.

### پیش‌نیازها

لینوکس با Python 3، `hostapd`، `dnsmasq`، `nftables` و `iw`. برای VPN نیز
Xray لازم است.

### راه‌اندازی سریع

```bash
cp config.example.json config.json
chmod 600 config.json
sudo python3 hotspot.py check --config config.json
sudo python3 hotspot.py start --config config.json
sudo python3 hotspot.py status --config config.json
sudo python3 hotspot.py stop --config config.json
```

پیش از اجرا، نام رابط اینترنت کابل، آداپتور Wi‑Fi، نام شبکه و رمز را در
`config.json` تغییر بده.

### VPN با VLESS

در `config.json` مقدار `vpn.enabled` را `true` کن و لینک VLESS را در
`vpn.vless_uri` قرار بده. TCP، WebSocket و gRPC با TLS یا Reality پشتیبانی
می‌شوند. ترافیک دستگاه‌های متصل شفاف از تونل عبور می‌کند؛ اینترنت کامپیوتر
مستقیم باقی می‌ماند.

### نکات امنیتی

`config.json` ممکن است رمز Wi‑Fi و لینک خصوصی VLESS داشته باشد. این فایل عمداً
در Git نادیده گرفته می‌شود؛ آن را منتشر نکن. برای انتشار عمومی از
`config.example.json` استفاده کن.

### اجرای خودکار پس از روشن‌شدن سیستم

فایل `velalink.service` را نصب و سرویس را یک‌بار فعال کن:

```bash
sudo install -m 644 velalink.service /etc/systemd/system/velalink.service
sudo systemctl daemon-reload
sudo systemctl enable --now velalink.service
```

### پنل کنترل مدرن و فارسی

یک پنل وب فارسی، راست‌چین و مدرن نیز همراه پروژه هست. سرویس آن را فعال کن و
سپس `http://127.0.0.1:8091` را در مرورگر باز کن:

```bash
sudo install -m 644 velalink-panel.service /etc/systemd/system/velalink-panel.service
sudo systemctl daemon-reload
sudo systemctl enable --now velalink-panel.service
```

پنل فقط روی خود همان کامپیوتر باز می‌شود و کنترل روشن/خاموش، راه‌اندازی مجدد،
وضعیت و تنظیمات را دارد.
