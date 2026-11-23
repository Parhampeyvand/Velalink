#!/usr/bin/env python3
"""Persian desktop control panel for the VelaLink system service."""
from __future__ import annotations

import json
import subprocess
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

HERE = Path(__file__).resolve().parent
CONFIG = HERE / "config.json"
SERVICE = "velalink.service"

BG = "#101827"
CARD = "#192334"
CARD_ALT = "#223049"
TEXT = "#F4F7FB"
MUTED = "#AAB7CB"
ACCENT = "#35C7A5"
ACCENT_DARK = "#17866F"
DANGER = "#F06479"
FIELD = "#0D1421"
FONT = "Vazirmatn"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ولا لینک")
        self.geometry("860x760")
        self.minsize(720, 650)
        self.configure(bg=BG)
        self.vpn_enabled = tk.BooleanVar()
        self.sleep_enabled = tk.BooleanVar()
        self.values: dict[str, tk.StringVar] = {}
        self.status_text = tk.StringVar(value="در حال بررسی وضعیت…")
        self.build()
        self.load_config()
        self.refresh_status()

    def label(self, parent: tk.Misc, text: str, size: int = 11, color: str = TEXT, bold: bool = False, **kw):
        return tk.Label(parent, text=text, bg=parent.cget("bg"), fg=color,
                        font=(FONT, size, "bold" if bold else "normal"), **kw)

    def button(self, parent: tk.Misc, text: str, command, color: str = ACCENT, **kw):
        return tk.Button(parent, text=text, command=command, bg=color, fg="#071411",
                         activebackground=ACCENT_DARK, activeforeground=TEXT, relief="flat",
                         bd=0, cursor="hand2", font=(FONT, 11, "bold"), padx=16, pady=9, **kw)

    def card(self, parent: tk.Misc) -> tk.Frame:
        return tk.Frame(parent, bg=CARD, highlightthickness=1, highlightbackground="#2A3953", padx=18, pady=16)

    def build(self) -> None:
        outer = tk.Frame(self, bg=BG, padx=30, pady=24)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x", pady=(0, 18))
        self.label(header, "ولا لینک", 26, bold=True, anchor="e").pack(side="right")
        self.label(header, "اشتراک امن اینترنت با هات‌اسپات و VLESS", 11, MUTED, anchor="e").pack(side="right", padx=(0, 16), pady=10)

        status = self.card(outer)
        status.pack(fill="x", pady=(0, 14))
        self.status_dot = tk.Label(status, text="●", bg=CARD, fg=MUTED, font=(FONT, 28))
        self.status_dot.pack(side="right", padx=(0, 12))
        self.status_label = self.label(status, "", 15, bold=True, anchor="e", textvariable=self.status_text)
        self.status_label.pack(side="right", fill="x", expand=True)
        self.button(status, "بروزرسانی", self.refresh_status, color=CARD_ALT).pack(side="left")

        actions = tk.Frame(outer, bg=BG)
        actions.pack(fill="x", pady=(0, 16))
        self.button(actions, "روشن کردن", lambda: self.service("start")).pack(side="right", fill="x", expand=True, padx=(0, 6))
        self.button(actions, "راه‌اندازی دوباره", lambda: self.service("restart"), color="#70A5FA").pack(side="right", fill="x", expand=True, padx=6)
        self.button(actions, "خاموش کردن", lambda: self.service("stop"), color=DANGER).pack(side="right", fill="x", expand=True, padx=(6, 0))

        settings = self.card(outer)
        settings.pack(fill="both", expand=True)
        self.label(settings, "تنظیمات هات‌اسپات", 15, bold=True, anchor="e").grid(row=0, column=0, columnspan=4, sticky="e", pady=(0, 14))
        for col in range(4):
            settings.grid_columnconfigure(col, weight=1)
        fields = (("نام شبکه", "ssid"), ("رمز شبکه", "passphrase"),
                  ("رابط اینترنت", "uplink_interface"), ("رابط Wi‑Fi", "wifi_interface"),
                  ("کشور", "country"), ("کانال", "channel"), ("شبکهٔ داخلی", "subnet"))
        for index, (caption, key) in enumerate(fields):
            row, section = divmod(index, 2)
            column = 3 if section == 0 else 1
            self.label(settings, caption, 10, MUTED, anchor="e").grid(row=row * 2 + 1, column=column - 1, columnspan=2, sticky="e", pady=(4, 2))
            value = tk.StringVar()
            self.values[key] = value
            entry = tk.Entry(settings, textvariable=value, justify="right", bg=FIELD, fg=TEXT,
                             insertbackground=TEXT, relief="flat", font=(FONT, 11),
                             show="•" if key == "passphrase" else "")
            entry.grid(row=row * 2 + 2, column=column - 1, columnspan=2, sticky="ew", padx=5, ipady=8)

        controls_row = 9
        self.check(settings, "فعال‌سازی VPN برای دستگاه‌های متصل", self.vpn_enabled).grid(row=controls_row, column=0, columnspan=4, sticky="e", pady=(16, 5))
        self.label(settings, "لینک VLESS خصوصی", 10, MUTED, anchor="e").grid(row=controls_row + 1, column=0, columnspan=4, sticky="e", pady=(4, 3))
        self.vless = ScrolledText(settings, height=4, wrap="word", bg=FIELD, fg=TEXT, insertbackground=TEXT,
                                  relief="flat", font=(FONT, 10), padx=10, pady=8)
        self.vless.grid(row=controls_row + 2, column=0, columnspan=4, sticky="ew")
        self.check(settings, "هنگام روشن‌بودن هات‌اسپات، سیستم به Sleep نرود", self.sleep_enabled).grid(row=controls_row + 3, column=0, columnspan=4, sticky="e", pady=12)
        self.button(settings, "ذخیرهٔ تنظیمات", self.save_config).grid(row=controls_row + 4, column=0, columnspan=4, sticky="ew")
        self.label(outer, "پس از ذخیره، «راه‌اندازی دوباره» را بزن تا تغییرات اعمال شوند.", 10, MUTED, anchor="e").pack(fill="x", pady=(10, 0))

    def check(self, parent: tk.Misc, text: str, variable: tk.BooleanVar) -> tk.Checkbutton:
        return tk.Checkbutton(parent, text=text, variable=variable, bg=CARD, fg=TEXT,
                              activebackground=CARD, activeforeground=TEXT, selectcolor=FIELD,
                              font=(FONT, 11), anchor="e", justify="right", highlightthickness=0)

    def load_config(self) -> None:
        try:
            cfg = json.loads(CONFIG.read_text())
            for key, value in self.values.items():
                value.set(str(cfg.get(key, "")))
            vpn = cfg.get("vpn", {})
            self.vpn_enabled.set(bool(vpn.get("enabled", False)))
            self.sleep_enabled.set(bool(cfg.get("prevent_sleep", True)))
            self.vless.insert("1.0", vpn.get("vless_uri", ""))
        except (OSError, json.JSONDecodeError) as exc:
            messagebox.showerror("ولا لینک", f"تنظیمات خوانده نشد:\n{exc}")

    def save_config(self) -> None:
        cfg = {key: value.get().strip() for key, value in self.values.items()}
        try:
            cfg["channel"] = int(cfg["channel"])
        except ValueError:
            messagebox.showerror("ولا لینک", "کانال باید عدد باشد.")
            return
        cfg["vpn"] = {"enabled": self.vpn_enabled.get(), "vless_uri": self.vless.get("1.0", "end").strip()}
        cfg["prevent_sleep"] = self.sleep_enabled.get()
        if cfg["vpn"]["enabled"] and not cfg["vpn"]["vless_uri"].startswith("vless://"):
            messagebox.showerror("ولا لینک", "لینک VLESS معتبر نیست.")
            return
        CONFIG.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
        CONFIG.chmod(0o600)
        messagebox.showinfo("ولا لینک", "تنظیمات ذخیره شد. برای اعمال تغییرات، راه‌اندازی دوباره را بزن.")

    def refresh_status(self) -> None:
        result = subprocess.run(("systemctl", "is-active", SERVICE), text=True, capture_output=True)
        active = result.stdout.strip() == "active"
        self.status_text.set("هات‌اسپات و VPN فعال‌اند" if active else "ولا لینک خاموش است")
        self.status_dot.config(fg=ACCENT if active else DANGER)
        self.status_label.config(fg=ACCENT if active else DANGER)

    def service(self, action: str) -> None:
        self.status_text.set("در حال انجام عملیات…")
        self.status_dot.config(fg="#F6C453")
        def run() -> None:
            result = subprocess.run(("pkexec", "systemctl", action, SERVICE), text=True, capture_output=True)
            self.after(0, lambda: self.after_service(action, result))
        threading.Thread(target=run, daemon=True).start()

    def after_service(self, action: str, result: subprocess.CompletedProcess[str]) -> None:
        self.refresh_status()
        if result.returncode:
            messagebox.showerror("ولا لینک", f"عملیات انجام نشد:\n{result.stderr or result.stdout}")
        else:
            names = {"start": "روشن شد", "restart": "راه‌اندازی دوباره انجام شد", "stop": "خاموش شد"}
            messagebox.showinfo("ولا لینک", names[action])


if __name__ == "__main__":
    App().mainloop()
