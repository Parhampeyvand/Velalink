#!/usr/bin/env python3
"""Small, reversible Ethernet-to-Wi-Fi hotspot manager."""
from __future__ import annotations

import argparse
import ipaddress
import json
import os
import shutil
import signal
import subprocess
import sys
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

RUN = Path("/run/simple-hotspot")
HOSTAPD = RUN / "hostapd.conf"
DNSMASQ = RUN / "dnsmasq.conf"
PID = RUN / "dnsmasq.pid"
XRAY = RUN / "xray.json"
TPROXY_PORT = 12345
MARK = "0x1"
ROUTE_TABLE = "100"
XRAY_BIN = shutil.which("xray") or "/usr/local/bin/xray"


def cmd(*args: str, check: bool = True, capture: bool = False):
    return subprocess.run(args, text=True, check=check, capture_output=capture)


def root() -> None:
    if os.geteuid() != 0:
        raise RuntimeError("این فرمان را با sudo اجرا کنید.")


def config(path: Path) -> dict:
    cfg = json.loads(path.read_text())
    required = {"uplink_interface", "wifi_interface", "ssid", "passphrase", "country", "channel", "subnet"}
    missing = required - cfg.keys()
    if missing:
        raise RuntimeError("تنظیمات ناقص است: " + ", ".join(sorted(missing)))
    if cfg["uplink_interface"] == cfg["wifi_interface"]:
        raise RuntimeError("رابط کابل و Wi-Fi نباید یکی باشند.")
    if not 8 <= len(cfg["passphrase"]) <= 63:
        raise RuntimeError("رمز Wi-Fi باید ۸ تا ۶۳ نویسه باشد.")
    net = ipaddress.ip_network(cfg["subnet"], strict=True)
    if net.version != 4 or net.prefixlen != 24:
        raise RuntimeError("شبکه باید دقیقاً مانند 10.42.0.0/24 باشد.")
    hosts = net.hosts()
    gateway = next(hosts)
    for _ in range(48):
        next(hosts)
    dhcp_start = next(hosts)
    dhcp_end = list(hosts)[-2]
    cfg.update(network=net, gateway=str(gateway), dhcp_start=str(dhcp_start), dhcp_end=str(dhcp_end))
    vpn = cfg.get("vpn", {})
    if not isinstance(vpn, dict):
        raise RuntimeError("بخش VPN باید یک شیء تنظیمات باشد.")
    vpn["enabled"] = bool(vpn.get("enabled", False))
    if vpn["enabled"] and not str(vpn.get("vless_uri", "")).startswith("vless://"):
        raise RuntimeError("برای VPN، لینک VLESS را در vpn.vless_uri وارد کنید.")
    cfg["vpn"] = vpn
    return cfg


def preflight(cfg: dict) -> list[str]:
    errors: list[str] = []
    tools = ["ip", "iw", "nft", "hostapd", "dnsmasq"]
    if cfg["vpn"]["enabled"] and not Path(XRAY_BIN).is_file():
        errors.append("ابزار لازم وجود ندارد: xray")
    for tool in tools:
        if not shutil.which(tool):
            errors.append(f"ابزار لازم وجود ندارد: {tool}")
    for key in ("uplink_interface", "wifi_interface"):
        if not Path("/sys/class/net", cfg[key]).exists():
            errors.append(f"رابط پیدا نشد: {cfg[key]}")
    if errors:
        return errors
    route = cmd("ip", "route", "show", "default", check=False, capture=True).stdout
    if cfg["uplink_interface"] not in route:
        errors.append("رابط اینترنت ورودی مسیر پیش‌فرض ندارد.")
    info = cmd("iw", "dev", cfg["wifi_interface"], "info", check=False, capture=True).stdout
    if "type managed" not in info and "type AP" not in info:
        errors.append("Wi-Fi در وضعیت قابل‌استفاده نیست.")
    processes = cmd("pgrep", "-af", "hostapd", check=False, capture=True).stdout.splitlines()
    if any(str(HOSTAPD) not in process for process in processes):
        errors.append("یک هات‌اسپات دیگر این Wi-Fi را در اختیار دارد. ابتدا آن را خاموش کنید.")
    return errors


def write_files(cfg: dict) -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    HOSTAPD.write_text("\n".join((
        f"interface={cfg['wifi_interface']}", "driver=nl80211", f"ssid={cfg['ssid']}",
        "hw_mode=g", f"channel={cfg['channel']}", f"country_code={cfg['country']}",
        "ieee80211d=1", "wmm_enabled=1", "auth_algs=1", "wpa=2",
        f"wpa_passphrase={cfg['passphrase']}", "wpa_key_mgmt=WPA-PSK", "rsn_pairwise=CCMP", "")))
    DNSMASQ.write_text("\n".join((
        f"interface={cfg['wifi_interface']}", "bind-interfaces",
        f"dhcp-range={cfg['dhcp_start']},{cfg['dhcp_end']},12h",
        f"dhcp-option=3,{cfg['gateway']}", f"dhcp-option=6,{cfg['gateway']},1.1.1.1",
        "server=1.1.1.1", "server=9.9.9.9", f"pid-file={PID}", "")))
    if cfg["vpn"]["enabled"]:
        XRAY.write_text(json.dumps(xray_config(cfg["vpn"]["vless_uri"]), indent=2))


def xray_config(uri: str) -> dict:
    """Turn a standard VLESS share link into the small config this tool needs."""
    parsed = urlparse(uri)
    if parsed.scheme != "vless" or not parsed.hostname or not parsed.username or not parsed.port:
        raise RuntimeError("لینک VLESS معتبر نیست.")
    q = {key: values[-1] for key, values in parse_qs(parsed.query).items()}
    network = q.get("type", "tcp")
    security = q.get("security", "none")
    if network not in {"tcp", "ws", "grpc"} or security not in {"none", "tls", "reality"}:
        raise RuntimeError("این نسخه VLESS از tcp، ws، grpc و TLS/Reality پشتیبانی می‌کند.")
    stream = {"network": network, "security": security}
    if network == "ws":
        stream["wsSettings"] = {"path": q.get("path", "/"), "headers": {"Host": q.get("host", "")}}
    elif network == "grpc":
        stream["grpcSettings"] = {"serviceName": q.get("serviceName", "")}
    if security == "tls":
        stream["tlsSettings"] = {"serverName": q.get("sni", parsed.hostname), "fingerprint": q.get("fp", "chrome")}
    elif security == "reality":
        public_key = q.get("pbk", "")
        if not public_key:
            raise RuntimeError("لینک Reality کلید عمومی ندارد.")
        stream["realitySettings"] = {
            "serverName": q.get("sni", parsed.hostname), "fingerprint": q.get("fp", "chrome"),
            "publicKey": public_key, "shortId": q.get("sid", ""), "spiderX": unquote(q.get("spx", "")),
        }
    user = {"id": parsed.username, "encryption": q.get("encryption", "none")}
    if q.get("flow"):
        user["flow"] = q["flow"]
    return {
        "log": {"loglevel": "warning"},
        "inbounds": [{"tag": "hotspot-in", "port": TPROXY_PORT, "protocol": "dokodemo-door",
                      "settings": {"network": "tcp,udp", "followRedirect": True},
                      "sniffing": {"enabled": True, "destOverride": ["http", "tls", "quic"]},
                      "streamSettings": {"sockopt": {"tproxy": "tproxy"}}}],
        "outbounds": [{"tag": "vpn", "protocol": "vless", "settings": {"vnext": [{"address": parsed.hostname,
                      "port": parsed.port, "users": [user]}]}, "streamSettings": stream}],
        "routing": {"rules": [{"type": "field", "inboundTag": ["hotspot-in"], "outboundTag": "vpn"}]},
    }


def firewall(cfg: dict) -> None:
    net = str(cfg["network"])
    tproxy = ""
    if cfg["vpn"]["enabled"]:
        tproxy = f''' chain prerouting {{
  type filter hook prerouting priority mangle; policy accept;
  iifname "{cfg['wifi_interface']}" ip saddr {net} meta l4proto {{ tcp, udp }} tproxy ip to 127.0.0.1:{TPROXY_PORT} meta mark set {MARK} accept
 }}
'''
    rules = f'''table inet simple_hotspot {{
{tproxy}
 chain forward {{
  type filter hook forward priority -20; policy accept;
  iifname "{cfg['wifi_interface']}" oifname "{cfg['uplink_interface']}" ip saddr {net} accept
  iifname "{cfg['uplink_interface']}" oifname "{cfg['wifi_interface']}" ip daddr {net} ct state established,related accept
 }}
 chain postrouting {{
  type nat hook postrouting priority srcnat; policy accept;
  oifname "{cfg['uplink_interface']}" ip saddr {net} masquerade
 }}
}}'''
    cmd("nft", "delete", "table", "inet", "simple_hotspot", check=False, capture=True)
    subprocess.run(("nft", "-f", "-"), input=rules, text=True, check=True)


def stop(cfg: dict, quiet: bool = False) -> None:
    root()
    if PID.exists():
        try:
            os.kill(int(PID.read_text().strip()), signal.SIGTERM)
        except (ValueError, ProcessLookupError):
            pass
    cmd("pkill", "-f", str(HOSTAPD), check=False)
    cmd("pkill", "-f", str(XRAY), check=False)
    cmd("nft", "delete", "table", "inet", "simple_hotspot", check=False, capture=True)
    cmd("ip", "rule", "del", "fwmark", MARK, "table", ROUTE_TABLE, "priority", "100", check=False, capture=True)
    cmd("ip", "route", "flush", "table", ROUTE_TABLE, check=False, capture=True)
    cmd("ip", "addr", "flush", "dev", cfg["wifi_interface"], check=False)
    cmd("ip", "link", "set", cfg["wifi_interface"], "down", check=False)
    if not quiet:
        print("هات‌اسپات خاموش و قوانین اختصاصی پاک شد.")


def start(cfg: dict) -> None:
    root()
    errors = preflight(cfg)
    if errors:
        raise RuntimeError("\n".join(errors))
    stop(cfg, quiet=True)
    write_files(cfg)
    cmd("ip", "link", "set", cfg["wifi_interface"], "down")
    cmd("ip", "addr", "add", f"{cfg['gateway']}/{cfg['network'].prefixlen}", "dev", cfg["wifi_interface"])
    cmd("ip", "link", "set", cfg["wifi_interface"], "up")
    cmd("sysctl", "-w", "net.ipv4.ip_forward=1")
    if cfg["vpn"]["enabled"]:
        cmd("ip", "rule", "add", "fwmark", MARK, "table", ROUTE_TABLE, "priority", "100")
        cmd("ip", "route", "add", "local", "0.0.0.0/0", "dev", "lo", "table", ROUTE_TABLE)
        cmd(XRAY_BIN, "run", "-test", "-c", str(XRAY))
        subprocess.Popen((XRAY_BIN, "run", "-c", str(XRAY)), stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    firewall(cfg)
    cmd("hostapd", "-B", str(HOSTAPD))
    cmd("dnsmasq", "--conf-file=" + str(DNSMASQ))
    print(f"روشن شد: {cfg['ssid']} ({cfg['gateway']})")


def status(cfg: dict) -> None:
    hostapd = cmd("pgrep", "-af", str(HOSTAPD), check=False, capture=True).returncode == 0
    nft = cmd("nft", "list", "table", "inet", "simple_hotspot", check=False).returncode == 0
    print("هات‌اسپات:", "روشن" if hostapd else "خاموش")
    print("NAT:", "فعال" if nft else "غیرفعال")
    if cfg["vpn"]["enabled"]:
        xray = cmd("pgrep", "-af", str(XRAY), check=False, capture=True).returncode == 0
        print("VPN:", "فعال" if xray else "غیرفعال")


def main() -> int:
    parser = argparse.ArgumentParser(description="Simple Hotspot")
    parser.add_argument("action", choices=("check", "start", "stop", "status"))
    parser.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    try:
        cfg = config(args.config)
        if args.action == "check":
            errors = preflight(cfg)
            print("آماده است." if not errors else "\n".join(errors))
            return int(bool(errors))
        {"start": start, "stop": stop, "status": status}[args.action](cfg)
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print("خطا:", exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
