# VelaLink

**Turn a Linux PC into a private Wi-Fi gateway — with an optional VLESS/Xray privacy layer.**

VelaLink shares a wired Internet connection through a dedicated Wi-Fi hotspot.
It is built for a simple, useful separation: devices connected to the hotspot
can use the normal Internet or an optional VLESS/Xray tunnel, while the host
computer keeps its own Internet connection unchanged.

**Website:** [parhampeyvand.ir/velalink.html](https://parhampeyvand.ir/velalink.html)

> **Private by design:** your Wi-Fi password and VLESS link stay in a local
> `config.json` file. That file is ignored by Git and must never be uploaded.

---

## What it does

- Creates a Wi-Fi hotspot from an Ethernet/uplink connection.
- Shares Internet using DHCP, DNS and NAT.
- Optionally routes only hotspot clients through a transparent VLESS/Xray
  tunnel.
- Leaves the computer's own traffic outside the VPN tunnel.
- Includes a modern local control panel with start, stop, restart, status and
  configuration controls.
- Can start automatically after Linux boots and prevents sleep while the
  hotspot is active.
- Uses its own `nftables` table, so it does not overwrite unrelated firewall
  rules from Docker or other applications.

## How it works

```text
Internet / Ethernet
        │
        ▼
   Linux PC running VelaLink
        │
        ├── Host computer: normal Internet connection
        │
        └── Wi-Fi hotspot clients: direct Internet or VLESS/Xray tunnel
```

## Requirements

- Linux with Python 3
- A wired/uplink network interface and a Wi-Fi adapter that supports Access
  Point mode
- `hostapd`, `dnsmasq`, `nftables`, and `iw`
- Xray only when enabling VLESS VPN routing

## Quick start

```bash
cp config.example.json config.json
chmod 600 config.json
# Edit config.json: interface names, Wi-Fi name/password, and optional VLESS link.
sudo python3 hotspot.py check --config config.json
sudo python3 hotspot.py start --config config.json
```

Useful commands:

```bash
sudo python3 hotspot.py status --config config.json
sudo python3 hotspot.py stop --config config.json
```

## Local control panel

Install the included services once:

```bash
sudo install -m 644 velalink.service /etc/systemd/system/velalink.service
sudo install -m 644 velalink-panel.service /etc/systemd/system/velalink-panel.service
sudo systemctl daemon-reload
sudo systemctl enable --now velalink.service velalink-panel.service
```

Then open [http://127.0.0.1:8091](http://127.0.0.1:8091) on the same computer.
The panel listens only on localhost; it is not exposed to your network.

## VLESS/Xray mode

Set `vpn.enabled` to `true` and add your own VLESS share link to
`vpn.vless_uri` in local `config.json`. VelaLink supports TCP, WebSocket and
gRPC transports with TLS or Reality. VPN routing applies only to connected
hotspot devices.

## Windows preview

The [`windows`](windows) folder includes a Persian PowerShell control panel for
starting a Windows hotspot and configuring Internet Connection Sharing.

- It needs Windows 11, Administrator access and Wi-Fi hardware that supports
  Hosted Network.
- A virtual machine cannot broadcast Wi-Fi without USB Wi-Fi passthrough.
- Transparent VLESS routing is intentionally not included in the Windows
  preview yet, because it needs a network driver such as WinDivert or Wintun.

## Security

- Never commit `config.json`, your Wi-Fi password, or a VLESS URI.
- Use `config.example.json` as the safe public template.
- Review the interface names carefully before enabling automatic startup.

## License

Choose and add a license before distributing production builds.

---

# فارسی

**VelaLink کامپیوتر لینوکسی را به یک دروازهٔ Wi-Fi خصوصی با لایهٔ اختیاری VLESS/Xray تبدیل می‌کند.**

این ابزار اینترنت کابل یا اتصال بالادستی را از طریق یک هات‌اسپات Wi-Fi در
اختیار دستگاه‌ها می‌گذارد. دستگاه‌های متصل می‌توانند اینترنت عادی داشته باشند
یا در صورت فعال‌سازی، فقط ترافیک آن‌ها از تونل VLESS/Xray عبور کند؛ اینترنت خود
کامپیوتر بدون تغییر باقی می‌ماند.

**وب‌سایت:** [parhampeyvand.ir/velalink.html](https://parhampeyvand.ir/velalink.html)

> **حریم خصوصی:** رمز Wi-Fi و لینک VLESS فقط در `config.json` محلی ذخیره
> می‌شوند. این فایل در Git نادیده گرفته شده و نباید در گیت‌هاب قرار بگیرد.

## قابلیت‌ها

- ساخت هات‌اسپات Wi-Fi از اینترنت کابل یا اتصال بالادستی.
- اشتراک اینترنت با DHCP، DNS و NAT.
- عبور اختیاری و شفاف ترافیک دستگاه‌های متصل از VLESS/Xray.
- جدا نگه‌داشتن اینترنت کامپیوتر از تونل VPN.
- پنل کنترل مدرن محلی برای روشن، خاموش، راه‌اندازی مجدد، مشاهدهٔ وضعیت و
  تنظیمات.
- شروع خودکار پس از روشن‌شدن لینوکس و جلوگیری از Sleep هنگام فعال‌بودن هات‌اسپات.
- استفاده از جدول مستقل `nftables` بدون پاک‌کردن قوانین Docker یا برنامه‌های
  دیگر.

## راه‌اندازی سریع

```bash
cp config.example.json config.json
chmod 600 config.json
# نام رابط‌ها، نام/رمز Wi-Fi و در صورت نیاز لینک VLESS را ویرایش کن.
sudo python3 hotspot.py check --config config.json
sudo python3 hotspot.py start --config config.json
```

فرمان‌های کاربردی:

```bash
sudo python3 hotspot.py status --config config.json
sudo python3 hotspot.py stop --config config.json
```

## پنل کنترل محلی

سرویس‌ها را یک‌بار نصب و فعال کن:

```bash
sudo install -m 644 velalink.service /etc/systemd/system/velalink.service
sudo install -m 644 velalink-panel.service /etc/systemd/system/velalink-panel.service
sudo systemctl daemon-reload
sudo systemctl enable --now velalink.service velalink-panel.service
```

سپس در همان کامپیوتر آدرس [http://127.0.0.1:8091](http://127.0.0.1:8091) را
باز کن. این پنل فقط روی خود کامپیوتر در دسترس است و به شبکه منتشر نمی‌شود.

## حالت VLESS/Xray

در `config.json` محلی، مقدار `vpn.enabled` را `true` کن و لینک شخصی خود را در
`vpn.vless_uri` قرار بده. TCP، WebSocket و gRPC با TLS یا Reality پشتیبانی
می‌شوند. فقط ترافیک دستگاه‌های متصل به هات‌اسپات وارد تونل می‌شود.

## پیش‌نمایش ویندوز

پوشهٔ [`windows`](windows) یک پنل PowerShell فارسی برای ساخت هات‌اسپات ویندوز و
تنظیم Internet Connection Sharing دارد.

- Windows 11، دسترسی Administrator و کارت Wi-Fi دارای Hosted Network لازم است.
- ماشین مجازی بدون USB Wi-Fi passthrough نمی‌تواند SSID پخش کند.
- عبور شفاف VLESS در نسخهٔ پیش‌نمایش ویندوز عمداً فعال نیست؛ این قابلیت به
  درایوری مانند WinDivert یا Wintun نیاز دارد.

## نکات امنیتی

- هرگز `config.json`، رمز Wi-Fi یا لینک VLESS را منتشر نکن.
- برای نمونهٔ قابل انتشار از `config.example.json` استفاده کن.
- پیش از فعال‌سازی اجرای خودکار، نام رابط‌های شبکه را بررسی کن.
