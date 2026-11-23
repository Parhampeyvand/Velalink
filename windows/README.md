# VelaLink for Windows

نسخهٔ ویندوز VelaLink یک پنل فارسی برای ساخت هات‌اسپات از اینترنت موجود ویندوز
است. به Windows 11، دسترسی Administrator و کارت Wi‑Fi دارای پشتیبانی Hosted
Network نیاز دارد.

## اجرا

1. فایل `VelaLink.ps1` را روی ویندوز کپی کن.
2. روی آن راست‌کلیک کن و **Run with PowerShell** را با دسترسی Administrator
   اجرا کن؛ یا PowerShell را با Administrator باز و این دستور را بزن:

   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   .\VelaLink.ps1
   ```

3. نام اتصال اینترنت و نام کارت Wi‑Fi مجازی را انتخاب کن، نام و رمز شبکه را
   وارد کن و «روشن کردن هات‌اسپات» را بزن.

> Windows 11 روی بعضی کارت‌های جدید Hosted Network را غیرفعال کرده است. در آن
> حالت، باید از **Settings → Network & Internet → Mobile hotspot** خود ویندوز
> استفاده شود. ماشین مجازی نیز بدون USB Wi‑Fi passthrough نمی‌تواند SSID پخش کند.

## VPN

این نسخهٔ نخست هات‌اسپات و Internet Connection Sharing را مدیریت می‌کند. عبور
شفاف همهٔ ترافیک دستگاه‌ها از VLESS روی ویندوز به یک درایور شبکه مانند WinDivert
یا Wintun نیاز دارد و عمداً در این نسخه فعال نشده تا اتصال عادی ویندوز مختل نشود.
