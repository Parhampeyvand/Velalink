# VelaLink ESP32 (Arduino)

نسخهٔ ESP32، اینترنت یک Wi-Fi موجود را به یک هات‌اسپات WPA2 دیگر تبدیل می‌کند.
ESP32 به شبکهٔ بالادستی وصل می‌شود (Station) و هم‌زمان یک شبکهٔ خصوصی برای
دستگاه‌ها می‌سازد (Access Point). با NAPT/NAT، دستگاه‌های متصل از اینترنت Wi-Fi
بالادستی استفاده می‌کنند.

> این یک روتر سبک است، نه نسخهٔ کامل لینوکسی VelaLink. ESP32 منابع کافی برای
> اجرای امن Xray/VLESS ندارد؛ تونل VLESS در این نسخه وجود ندارد.

## سخت‌افزار

- ESP32 DevKit، ESP32-S3، ESP32-C3 یا برد سازگار دیگر
- کابل USB داده
- شبکهٔ Wi-Fi بالادستی با اینترنت

## نصب در Arduino IDE

1. در **Boards Manager**، پکیج **esp32 by Espressif Systems** نسخهٔ 3.x را نصب
   یا به‌روز کن.
2. فایل `VelaLinkESP32/VelaLinkESP32.ino` را در Arduino IDE باز کن.
3. مقادیر `UPLINK_SSID`، `UPLINK_PASSWORD`، `HOTSPOT_SSID` و
   `HOTSPOT_PASSWORD` را تغییر بده.
4. از منوی **Tools → Board** برد ESP32 خودت و از **Tools → Port** پورت درست را
   انتخاب کن.
5. Upload را بزن و Serial Monitor را با سرعت `115200` باز کن.
6. به شبکه‌ای که در `HOTSPOT_SSID` تعریف کرده‌ای وصل شو.

## نکات مهم

- رمز هات‌اسپات باید بین ۸ تا ۶۳ نویسه باشد.
- هرگز رمز Wi-Fi را در GitHub منتشر نکن؛ پیش از Commit کردن، رمزها را به مقدار
  نمونه برگردان.
- این firmware به IPv4 NAPT وابسته است. اگر هنگام کامپایل تابع
  `esp_netif_napt_enable` پیدا نشد، پکیج برد Espressif را به Arduino-ESP32 3.x
  ارتقا بده. NAPT در ESP-IDF باید فعال باشد.
- یک رادیوی Wi-Fi هم‌زمان برای اتصال بالادستی و هات‌اسپات استفاده می‌شود؛ برای
  استفادهٔ سبک و تعداد محدود دستگاه مناسب است، نه سرعت یا تعداد کاربر بالا.
- همهٔ دستگاه‌ها روی کانال Wi-Fi شبکهٔ بالادستی کار می‌کنند؛ این محدودیت طبیعی
  حالت هم‌زمان AP+STA در ESP32 است.

## امنیت

- هات‌اسپات از WPA2-PSK استفاده می‌کند؛ رمز قوی و یکتا بگذار.
- پنل وب و VLESS در این firmware وجود ندارند؛ بنابراین هیچ رمز یا لینک VPN روی
  برد ذخیره نمی‌شود مگر خودت آن را در کد قرار دهی.
- برای اتصال حساس یا تونل VLESS، از نسخهٔ لینوکسی VelaLink استفاده کن.

## English

This Arduino firmware turns an ESP32 into a small Wi-Fi-to-Wi-Fi router. It
joins an existing Wi-Fi uplink as a station and exposes a separate WPA2 access
point for client devices. IPv4 NAPT shares the uplink connection.

It intentionally does **not** run Xray/VLESS. For transparent VLESS routing,
use the Linux VelaLink version instead.
