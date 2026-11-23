#!/usr/bin/env python3
"""Local RTL web panel for VelaLink; listens only on this computer."""
from __future__ import annotations

import json
import os
import subprocess
import threading
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONFIG = ROOT / "config.json"
SERVICE = "velalink.service"
ADDRESS = ("127.0.0.1", 8091)

PAGE = r'''<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>ولا لینک</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700&display=swap');
:root{--bg:#080d18;--card:#121c2c;--card2:#18263b;--line:#263852;--text:#eff5ff;--muted:#a8b6ca;--mint:#35d3ae;--blue:#78a9ff;--red:#ff6f83;--yellow:#f8ca68}*{box-sizing:border-box}body{margin:0;background:radial-gradient(80% 80% at 90% 0,#16335b 0,transparent 50%),var(--bg);color:var(--text);font-family:Vazirmatn,Tahoma,sans-serif;min-height:100vh}.wrap{max-width:1000px;margin:auto;padding:38px 22px 60px}header{display:flex;align-items:center;justify-content:space-between;margin-bottom:28px}.brand{display:flex;gap:14px;align-items:center}.logo{width:48px;height:48px;border-radius:16px;display:grid;place-items:center;background:linear-gradient(145deg,#5da9ff,#35d3ae);font-size:25px;box-shadow:0 10px 30px #35d3ae33}.brand h1{font-size:27px;margin:0}.brand p{margin:3px 0 0;color:var(--muted);font-size:13px}.pill{border:1px solid var(--line);border-radius:99px;padding:7px 12px;color:var(--muted);font-size:12px}.card{background:linear-gradient(145deg,#152135,#101928);border:1px solid var(--line);border-radius:22px;padding:22px;margin:15px 0;box-shadow:0 15px 40px #0004}.status{display:flex;justify-content:space-between;align-items:center;gap:16px}.state{display:flex;gap:13px;align-items:center}.dot{width:13px;height:13px;border-radius:50%;background:var(--red);box-shadow:0 0 0 6px #ff6f8320}.dot.on{background:var(--mint);box-shadow:0 0 0 6px #35d3ae20}.state b{font-size:18px}.state small{color:var(--muted);display:block;margin-top:3px}.actions{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:18px}button{border:0;border-radius:13px;padding:12px;font-family:inherit;font-weight:700;font-size:14px;cursor:pointer;background:var(--mint);color:#062019;transition:.18s}button:hover{filter:brightness(1.1);transform:translateY(-1px)}button.secondary{background:var(--blue);color:#081329}button.danger{background:#33202a;color:#ff9cac;border:1px solid #713646}.head{display:flex;align-items:center;justify-content:space-between;margin-bottom:17px}.head h2{font-size:18px;margin:0}.head span{color:var(--muted);font-size:12px}.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:15px}.field label{display:block;color:var(--muted);font-size:12px;margin:0 0 7px}input,textarea{width:100%;border:1px solid var(--line);background:#0a111d;color:var(--text);border-radius:12px;padding:12px;font:14px Vazirmatn,Tahoma,sans-serif;outline:0;transition:.18s;text-align:right}input:focus,textarea:focus{border-color:var(--blue);box-shadow:0 0 0 3px #78a9ff22}textarea{min-height:98px;direction:ltr;text-align:left}.toggle{display:flex;align-items:center;justify-content:space-between;background:#0e1725;border-radius:13px;padding:13px 14px;margin-top:12px}.toggle span{font-size:13px}.switch{appearance:none;width:45px;height:25px;border-radius:99px;background:#344258;position:relative;cursor:pointer;transition:.2s}.switch:after{content:'';position:absolute;width:19px;height:19px;background:white;border-radius:50%;top:3px;right:3px;transition:.2s}.switch:checked{background:var(--mint)}.switch:checked:after{right:23px}.save{margin-top:18px;width:100%}.notice{position:fixed;left:20px;bottom:20px;background:#1d2b42;border:1px solid var(--line);border-radius:12px;padding:12px 16px;opacity:0;transform:translateY(15px);transition:.2s}.notice.show{opacity:1;transform:none}@media(max-width:640px){.wrap{padding:22px 14px}.grid{grid-template-columns:1fr}.actions{grid-template-columns:1fr}.status{align-items:flex-start;flex-direction:column}.pill{display:none}}
</style></head><body><main class="wrap"><header><div class="brand"><div class="logo">✦</div><div><h1>ولا لینک</h1><p>کنترل هات‌اسپات و تونل خصوصی VLESS</p></div></div><div class="pill">فقط روی همین کامپیوتر</div></header>
<section class="card"><div class="status"><div class="state"><i id="dot" class="dot"></i><div><b id="state">در حال بررسی…</b><small id="detail">وضعیت سرویس</small></div></div><button class="secondary" onclick="refresh()">↻ بروزرسانی</button></div><div class="actions"><button onclick="act('start')">روشن کردن</button><button class="secondary" onclick="act('restart')">راه‌اندازی دوباره</button><button class="danger" onclick="act('stop')">خاموش کردن</button></div></section>
<section class="card"><div class="head"><h2>تنظیمات اتصال</h2><span>پس از ذخیره، راه‌اندازی دوباره را بزن</span></div><div class="grid"><div class="field"><label>نام شبکهٔ Wi‑Fi</label><input id="ssid"></div><div class="field"><label>رمز Wi‑Fi</label><input id="passphrase" type="password"></div><div class="field"><label>رابط اینترنت</label><input id="uplink_interface"></div><div class="field"><label>رابط Wi‑Fi</label><input id="wifi_interface"></div><div class="field"><label>کشور</label><input id="country" maxlength="2"></div><div class="field"><label>کانال</label><input id="channel" type="number" min="1" max="13"></div></div><div class="field" style="margin-top:15px"><label>شبکهٔ داخلی</label><input id="subnet"></div><div class="toggle"><span>عبور ترافیک دستگاه‌های متصل از VPN</span><input id="vpn_enabled" class="switch" type="checkbox"></div><div class="field" style="margin-top:14px"><label>لینک خصوصی VLESS</label><textarea id="vless_uri" spellcheck="false"></textarea></div><div class="toggle"><span>جلوگیری از Sleep هنگام فعال‌بودن هات‌اسپات</span><input id="prevent_sleep" class="switch" type="checkbox"></div><button class="save" onclick="save()">ذخیرهٔ تنظیمات</button></section></main><div id="notice" class="notice"></div>
<script>
const ids=['ssid','passphrase','uplink_interface','wifi_interface','country','channel','subnet'];
function toast(t){let n=document.querySelector('#notice');n.textContent=t;n.classList.add('show');setTimeout(()=>n.classList.remove('show'),3600)}
async function api(path,opts={}){let r=await fetch(path,opts);let d=await r.json();if(!r.ok)throw Error(d.error||'خطا در انجام عملیات');return d}
async function refresh(){try{let d=await api('/api/status');let on=d.active;document.querySelector('#state').textContent=on?'هات‌اسپات و VPN فعال‌اند':'ولا لینک خاموش است';document.querySelector('#detail').textContent=on?'Wi‑Fi، VPN و جلوگیری از Sleep آماده‌اند':'برای فعال‌سازی، دکمهٔ «روشن کردن» را بزن';document.querySelector('#dot').classList.toggle('on',on)}catch(e){toast(e.message)}}
async function load(){try{let c=await api('/api/config');ids.forEach(k=>document.querySelector('#'+k).value=c[k]??'');document.querySelector('#vpn_enabled').checked=!!c.vpn?.enabled;document.querySelector('#vless_uri').value=c.vpn?.vless_uri||'';document.querySelector('#prevent_sleep').checked=c.prevent_sleep!==false}catch(e){toast(e.message)}}
async function save(){let c={};ids.forEach(k=>c[k]=document.querySelector('#'+k).value.trim());c.channel=Number(c.channel);c.vpn={enabled:document.querySelector('#vpn_enabled').checked,vless_uri:document.querySelector('#vless_uri').value.trim()};c.prevent_sleep=document.querySelector('#prevent_sleep').checked;try{await api('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(c)});toast('تنظیمات ذخیره شد. برای اعمال، راه‌اندازی دوباره را بزن.')}catch(e){toast(e.message)}}
async function act(action){try{toast('در حال انجام عملیات…');await api('/api/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({action})});toast('عملیات انجام شد.');setTimeout(refresh,800)}catch(e){toast(e.message)}}load();refresh();
</script></body></html>'''


def response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode()
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class Panel(BaseHTTPRequestHandler):
    def log_message(self, *_args) -> None:
        pass

    def do_GET(self) -> None:
        if self.path == "/":
            body = PAGE.encode()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/status":
            active = subprocess.run(("systemctl", "is-active", SERVICE), capture_output=True, text=True).stdout.strip() == "active"
            response(self, HTTPStatus.OK, {"active": active})
        elif self.path == "/api/config":
            try:
                response(self, HTTPStatus.OK, json.loads(CONFIG.read_text()))
            except (OSError, json.JSONDecodeError) as exc:
                response(self, HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(exc)})
        else:
            response(self, HTTPStatus.NOT_FOUND, {"error": "یافت نشد"})

    def do_POST(self) -> None:
        try:
            size = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(size))
            if self.path == "/api/config":
                required = {"ssid", "passphrase", "uplink_interface", "wifi_interface", "country", "channel", "subnet", "vpn", "prevent_sleep"}
                if not required.issubset(data) or not 8 <= len(data["passphrase"]) <= 63:
                    raise ValueError("تنظیمات کامل یا معتبر نیست.")
                CONFIG.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
                CONFIG.chmod(0o600)
                response(self, HTTPStatus.OK, {"ok": True})
            elif self.path == "/api/action":
                action = data.get("action")
                if action not in {"start", "stop", "restart"}:
                    raise ValueError("عملیات نامعتبر است.")
                command = ("systemctl", action, SERVICE) if os.geteuid() == 0 else ("pkexec", "systemctl", action, SERVICE)
                result = subprocess.run(command, text=True, capture_output=True)
                if result.returncode:
                    raise RuntimeError(result.stderr or result.stdout or "عملیات انجام نشد.")
                response(self, HTTPStatus.OK, {"ok": True})
            else:
                response(self, HTTPStatus.NOT_FOUND, {"error": "یافت نشد"})
        except (ValueError, RuntimeError, json.JSONDecodeError) as exc:
            response(self, HTTPStatus.BAD_REQUEST, {"error": str(exc)})


if __name__ == "__main__":
    server = ThreadingHTTPServer(ADDRESS, Panel)
    if os.environ.get("VELALINK_OPEN_BROWSER") == "1":
        threading.Timer(0.4, lambda: webbrowser.open("http://127.0.0.1:8091/")).start()
    server.serve_forever()
