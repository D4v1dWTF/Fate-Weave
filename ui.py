# ui.py - 使用者介面
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import json
import os
from data import (
    VERSION, WORLD_BACKGROUND, KEY_NPCS, DEFAULT_CONFIG,
    TRAIT_LIST, TRAIT_EFFECTS  # 匯入特徵列表與效果
)
from core import Player, AIService, GameEngine

from typing import Dict, List

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"命運織網 - 人生模擬 RPG  v{VERSION}")
        self.root.geometry("1050x780")
        self.root.minsize(850, 650)
        self.root.configure(bg="#1a1a2e")

        self.config = self.load_config()
        self.ai = AIService(
            api_key=self.config.get("api_key", ""),
            base_url=self.config.get("base_url", "https://api.chatanywhere.com.cn/v1"),
            model=self.config.get("model", "gpt-3.5-turbo")
        )
        self.engine = GameEngine(self.ai)

        self.event_choices = []
        self.waiting_for_event = False
        self.tutorial_step = 0
        self.in_tutorial = False
        self.view_mode = "story"

        self.setup_ui()
        self.show_welcome()
        self.root.after(100, self.check_api_key)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        if messagebox.askokcancel("離開遊戲", "確定要離開嗎？\n進度將不會儲存，每次開啟遊戲都是一段新的人生。"):
            self.root.destroy()

    def load_config(self) -> Dict:
        if os.path.exists("config_gui.json"):
            try:
                with open("config_gui.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        try:
            with open("config_gui.json", 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except PermissionError:
            messagebox.showerror("儲存失敗", "無法寫入設定檔，請確認檔案未被佔用且有寫入權限。")
        except Exception as e:
            messagebox.showerror("儲存失敗", f"錯誤：{str(e)}")

    def check_api_key(self):
        if not self.config.get("api_key"):
            self.open_api_settings()

    def open_api_settings(self):
        win = tk.Toplevel(self.root)
        win.title("AI 設定")
        win.geometry("450x320")
        win.resizable(False, False)
        win.configure(bg="#1a1a2e")

        tk.Label(win, text="AI 服務設定", font=('Arial', 16, 'bold'),
                 fg="#f0c040", bg="#1a1a2e").pack(pady=10)

        warning = tk.Label(win, text="⚠️ 注意：每次 AI 生成都會消耗您的 API Token，請留意用量。",
                           font=('Arial', 10, 'bold'), fg="#ff6b6b", bg="#1a1a2e")
        warning.pack(pady=2)

        frame = tk.Frame(win, bg="#1a1a2e")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        tk.Label(frame, text="API 金鑰：", font=('Arial', 11),
                 fg="white", bg="#1a1a2e").grid(row=0, column=0, sticky='w', pady=5)
        key_entry = tk.Entry(frame, width=35, font=('Arial', 11), bg="#2a2a4a", fg="white")
        key_entry.grid(row=0, column=1, sticky='w', pady=5)
        key_entry.insert(0, self.config.get("api_key", ""))

        tk.Label(frame, text="Base URL：", font=('Arial', 11),
                 fg="white", bg="#1a1a2e").grid(row=1, column=0, sticky='w', pady=5)
        url_entry = tk.Entry(frame, width=35, font=('Arial', 11), bg="#2a2a4a", fg="white")
        url_entry.grid(row=1, column=1, sticky='w', pady=5)
        url_entry.insert(0, self.config.get("base_url", "https://api.chatanywhere.com.cn/v1"))

        tk.Label(frame, text="模型：", font=('Arial', 11),
                 fg="white", bg="#1a1a2e").grid(row=2, column=0, sticky='w', pady=5)
        model_entry = tk.Entry(frame, width=35, font=('Arial', 11), bg="#2a2a4a", fg="white")
        model_entry.grid(row=2, column=1, sticky='w', pady=5)
        model_entry.insert(0, self.config.get("model", "gpt-3.5-turbo"))

        def save_settings():
            key = key_entry.get().strip()
            url = url_entry.get().strip()
            model = model_entry.get().strip()
            if not url:
                url = "https://api.chatanywhere.com.cn/v1"
            if not model:
                model = "gpt-3.5-turbo"
            self.config["api_key"] = key
            self.config["base_url"] = url
            self.config["model"] = model
            self.save_config()
            self.ai = AIService(api_key=key, base_url=url, model=model)
            self.engine.ai = self.ai
            win.destroy()
            if self.ai.enabled:
                messagebox.showinfo("成功", "AI 設定已儲存！")
            else:
                messagebox.showinfo("提示", "請輸入有效的 API 金鑰和 URL")

        btn_frame = tk.Frame(win, bg="#1a1a2e")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="儲存", command=save_settings,
                  font=('Arial', 11), bg="#f0c040", fg="#1a1a2e", padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=win.destroy,
                  font=('Arial', 11), bg="#4a4a6a", fg="white", padx=15).pack(side=tk.LEFT, padx=5)

    # ---- UI 佈局 ----
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self.info_bar = tk.Frame(main_frame, bg="#1a1a2e", height=80)
        self.info_bar.pack(fill=tk.X, pady=(0, 5))
        self.info_bar.pack_propagate(False)
        self.status_label = tk.Label(self.info_bar, text="", font=('Arial', 10),
                                     fg="#a0d0ff", bg="#1a1a2e", justify=tk.LEFT)
        self.status_label.pack(side=tk.LEFT, padx=5)
        self.power_label = tk.Label(self.info_bar, text="", font=('Arial', 10, 'bold'),
                                    fg="#ffd700", bg="#1a1a2e")
        self.power_label.pack(side=tk.RIGHT, padx=5)

        self.event_monitor = tk.Frame(main_frame, bg="#0d0d1a")
        self.event_monitor.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.text_area = scrolledtext.ScrolledText(self.event_monitor, wrap=tk.WORD,
                                                   font=('Consolas', 11),
                                                   bg="#0d0d1a", fg="#e0e0e0",
                                                   insertbackground="#f0c040",
                                                   relief=tk.FLAT, borderwidth=0)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.tag_configure("title", foreground="#f0c040", font=('Arial', 14, 'bold'))
        self.text_area.tag_configure("highlight", foreground="#ff6b6b")
        self.text_area.tag_configure("gold", foreground="#ffd700")
        self.text_area.tag_configure("green", foreground="#51cf66")
        self.text_area.tag_configure("blue", foreground="#4dabf7")
        self.text_area.tag_configure("npc", foreground="#f06595")
        self.text_area.tag_configure("death", foreground="#ff0000", font=('Arial', 12, 'bold'))
        self.text_area.tag_configure("ending", foreground="#ffd700", font=('Arial', 14, 'bold'))
        self.text_area.tag_configure("tutorial", foreground="#00ffff", font=('Arial', 11, 'bold'))
        self.text_area.tag_configure("error", foreground="#ff4444", font=('Arial', 10, 'bold'))
        self.text_area.tag_configure("item", foreground="#ffa94d")
        self.text_area.tag_configure("solution", foreground="#90ee90", font=('Arial', 10, 'bold'))
        self.text_area.tag_configure("world", foreground="#ffa94d", font=('Arial', 10, 'italic'))
        self.text_area.tag_configure("codex", foreground="#ffd700", font=('Arial', 12, 'bold'))

        self.inventory_frame = tk.Frame(self.event_monitor, bg="#0d0d1a")
        self.inventory_frame.pack(fill=tk.BOTH, expand=True)
        self.inventory_frame.pack_forget()
        self.inventory_list = scrolledtext.ScrolledText(self.inventory_frame, wrap=tk.WORD,
                                                         font=('Consolas', 11),
                                                         bg="#0d0d1a", fg="#e0e0e0",
                                                         relief=tk.FLAT, borderwidth=0)
        self.inventory_list.pack(fill=tk.BOTH, expand=True)
        self.inventory_list.tag_configure("title", foreground="#f0c040", font=('Arial', 12, 'bold'))
        self.inventory_list.tag_configure("item", foreground="#ffa94d")
        self.inventory_list.tag_configure("info", foreground="#4dabf7")

        self.shop_frame = tk.Frame(self.event_monitor, bg="#0d0d1a")
        self.shop_frame.pack(fill=tk.BOTH, expand=True)
        self.shop_frame.pack_forget()
        self.shop_list = scrolledtext.ScrolledText(self.shop_frame, wrap=tk.WORD,
                                                    font=('Consolas', 11),
                                                    bg="#0d0d1a", fg="#e0e0e0",
                                                    relief=tk.FLAT, borderwidth=0)
        self.shop_list.pack(fill=tk.BOTH, expand=True)
        self.shop_list.tag_configure("title", foreground="#f0c040", font=('Arial', 12, 'bold'))
        self.shop_list.tag_configure("item", foreground="#ffa94d")
        self.shop_list.tag_configure("price", foreground="#51cf66")
        self.shop_list.tag_configure("info", foreground="#4dabf7")

        self.action_panel = tk.Frame(main_frame, bg="#1a1a2e", height=65)
        self.action_panel.pack(fill=tk.X)
        self.action_panel.pack_propagate(False)
        self.btn1 = tk.Button(self.action_panel, text="", command=lambda: None,
                              font=('Arial', 10), bg="#2a2a4a", fg="white", relief=tk.FLAT)
        self.btn1.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.btn2 = tk.Button(self.action_panel, text="", command=lambda: None,
                              font=('Arial', 10), bg="#2a2a4a", fg="white", relief=tk.FLAT)
        self.btn2.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.btn3 = tk.Button(self.action_panel, text="", command=lambda: None,
                              font=('Arial', 10), bg="#2a2a4a", fg="white", relief=tk.FLAT)
        self.btn3.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.btn4 = tk.Button(self.action_panel, text="", command=lambda: None,
                              font=('Arial', 10), bg="#2a2a4a", fg="white", relief=tk.FLAT)
        self.btn4.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
        self.hide_buttons()

        self.toolbar = tk.Frame(main_frame, bg="#1a1a2e", height=30)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))
        self.start_btn = tk.Button(self.toolbar, text="🌟 新人生", command=self.start_new_game,
                                   font=('Arial', 10, 'bold'), bg="#f0c040", fg="#1a1a2e",
                                   relief=tk.FLAT, padx=10)
        self.start_btn.pack(side=tk.LEFT, padx=2)
        self.end_year_btn = tk.Button(self.toolbar, text="⏭ 結束年", command=self.end_year,
                                      font=('Arial', 10), bg="#4a4a6a", fg="white",
                                      relief=tk.FLAT, padx=10, state=tk.DISABLED)
        self.end_year_btn.pack(side=tk.LEFT, padx=2)
        self.inventory_btn = tk.Button(self.toolbar, text="🎒 背包", command=self.toggle_inventory,
                                       font=('Arial', 10), bg="#2a4a6a", fg="white",
                                       relief=tk.FLAT, padx=10, state=tk.DISABLED)
        self.inventory_btn.pack(side=tk.LEFT, padx=2)
        self.shop_btn = tk.Button(self.toolbar, text="🏪 商店", command=self.toggle_shop,
                                  font=('Arial', 10), bg="#4a4a2a", fg="white",
                                  relief=tk.FLAT, padx=10, state=tk.DISABLED)
        self.shop_btn.pack(side=tk.LEFT, padx=2)
        self.codex_btn = tk.Button(self.toolbar, text="📖 圖鑑", command=self.open_codex,
                                   font=('Arial', 10), bg="#5a3a2a", fg="#ffd700",
                                   relief=tk.FLAT, padx=10)
        self.codex_btn.pack(side=tk.LEFT, padx=2)
        self.settings_btn = tk.Button(self.toolbar, text="⚙️ API", command=self.open_api_settings,
                                      font=('Arial', 10), bg="#3a3a5a", fg="white",
                                      relief=tk.FLAT, padx=10)
        self.settings_btn.pack(side=tk.LEFT, padx=2)
        self.view_label = tk.Label(self.toolbar, text="📖 故事", font=('Arial', 10),
                                   fg="#a0d0ff", bg="#1a1a2e")
        self.view_label.pack(side=tk.RIGHT, padx=5)
        self.action_label = tk.Label(self.toolbar, text="", font=('Arial', 9),
                                     fg="#a0d0ff", bg="#1a1a2e")
        self.action_label.pack(side=tk.RIGHT, padx=5)

    def hide_buttons(self):
        for btn in [self.btn1, self.btn2, self.btn3, self.btn4]:
            btn.config(text="", command=lambda: None, bg="#2a2a4a")

    def show_action_buttons(self, actions: List[Dict]):
        self.hide_buttons()
        buttons = [self.btn1, self.btn2, self.btn3, self.btn4]
        for i in range(4):
            if i < len(actions):
                buttons[i].config(text=actions[i]["text"], command=actions[i]["command"],
                                  bg="#2a2a4a", fg="white")
            else:
                buttons[i].config(text="", command=lambda: None, bg="#2a2a4a")

    def show_event_buttons(self, choices: List[Dict]):
        self.hide_buttons()
        buttons = [self.btn1, self.btn2, self.btn3, self.btn4]
        for i in range(4):
            if i < len(choices):
                buttons[i].config(text=choices[i].get("text", "選擇"),
                                  command=lambda c=choices[i]: self.choose_event(c),
                                  bg="#4a2a4a", fg="#ffd700")
            else:
                buttons[i].config(text="", command=lambda: None, bg="#2a2a4a")

    def set_view_mode(self, mode: str):
        self.view_mode = mode
        self.text_area.pack_forget()
        self.inventory_frame.pack_forget()
        self.shop_frame.pack_forget()
        if mode == "story":
            self.text_area.pack(fill=tk.BOTH, expand=True)
            self.view_label.config(text="📖 故事")
        elif mode == "inventory":
            self.inventory_frame.pack(fill=tk.BOTH, expand=True)
            self.view_label.config(text="🎒 背包")
            self.refresh_inventory_view()
        elif mode == "shop":
            self.shop_frame.pack(fill=tk.BOTH, expand=True)
            self.view_label.config(text="🏪 商店")
            self.refresh_shop_view()

    def refresh_inventory_view(self):
        self.inventory_list.config(state='normal')
        self.inventory_list.delete(1.0, tk.END)
        p = self.engine.player
        if not p:
            self.inventory_list.insert(tk.END, "尚無角色")
            self.inventory_list.config(state='normal')
            return
        self.inventory_list.insert(tk.END, "🎒 背包物品\n", "title")
        self.inventory_list.insert(tk.END, "─" * 30 + "\n", "info")
        if not p.inventory:
            self.inventory_list.insert(tk.END, "（空的）\n", "info")
        else:
            for i, item in enumerate(p.inventory):
                name = item.get("name", "未知")
                desc = item.get("desc", "")
                self.inventory_list.insert(tk.END, f"{i+1}. {name}", "item")
                if desc:
                    self.inventory_list.insert(tk.END, f" - {desc}", "info")
                self.inventory_list.insert(tk.END, "\n")
        self.inventory_list.config(state='normal')

    def refresh_shop_view(self):
        self.shop_list.config(state='normal')
        self.shop_list.delete(1.0, tk.END)
        p = self.engine.player
        if not p:
            self.shop_list.insert(tk.END, "尚無角色")
            self.shop_list.config(state='normal')
            return
        self.shop_list.insert(tk.END, "🏪 商店\n", "title")
        self.shop_list.insert(tk.END, "─" * 30 + "\n", "info")
        self.shop_list.insert(tk.END, f"你的信用點：{p.credits}\n\n", "price")
        for item in self.engine.shop_items:
            name = item.get("name", "未知")
            desc = item.get("desc", "")
            price = item.get("price", 0)
            self.shop_list.insert(tk.END, f"• {name}", "item")
            self.shop_list.insert(tk.END, f" - {desc}", "info")
            self.shop_list.insert(tk.END, f" (💰{price})\n", "price")
        self.shop_list.config(state='normal')

    # ---- 圖鑑 ----
    def open_codex(self):
        win = tk.Toplevel(self.root)
        win.title("📖 圖鑑 - 命運織網")
        win.geometry("700x600")
        win.minsize(600, 400)
        win.configure(bg="#1a1a2e")

        tk.Label(win, text="📖 圖鑑", font=('Arial', 18, 'bold'),
                 fg="#f0c040", bg="#1a1a2e").pack(pady=10)

        notebook = ttk.Notebook(win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ending_frame = tk.Frame(notebook, bg="#0d0d1a")
        notebook.add(ending_frame, text="🏆 結局")
        ending_text = scrolledtext.ScrolledText(ending_frame, wrap=tk.WORD,
                                                 font=('Consolas', 11),
                                                 bg="#0d0d1a", fg="#e0e0e0",
                                                 relief=tk.FLAT, borderwidth=0)
        ending_text.pack(fill=tk.BOTH, expand=True)
        ending_text.tag_configure("title", foreground="#f0c040", font=('Arial', 12, 'bold'))
        ending_text.tag_configure("unlocked", foreground="#51cf66")
        ending_text.tag_configure("locked", foreground="#4a4a6a")
        ending_text.tag_configure("desc", foreground="#a0d0ff")
        ending_text.tag_configure("condition", foreground="#ffa94d")

        hidden_frame = tk.Frame(notebook, bg="#0d0d1a")
        notebook.add(hidden_frame, text="✨ 隱藏事件")
        hidden_text = scrolledtext.ScrolledText(hidden_frame, wrap=tk.WORD,
                                                 font=('Consolas', 11),
                                                 bg="#0d0d1a", fg="#e0e0e0",
                                                 relief=tk.FLAT, borderwidth=0)
        hidden_text.pack(fill=tk.BOTH, expand=True)
        hidden_text.tag_configure("title", foreground="#f0c040", font=('Arial', 12, 'bold'))
        hidden_text.tag_configure("unlocked", foreground="#51cf66")
        hidden_text.tag_configure("locked", foreground="#4a4a6a")
        hidden_text.tag_configure("desc", foreground="#a0d0ff")
        hidden_text.tag_configure("condition", foreground="#ffa94d")
        hidden_text.tag_configure("positive", foreground="#51cf66")
        hidden_text.tag_configure("negative", foreground="#ff6b6b")

        codex_data = self.engine.get_codex_data()

        ending_text.config(state='normal')
        for ending_id in codex_data["endings"]["all"]:
            is_unlocked = ending_id in codex_data["endings"]["unlocked"]
            definition = ENDING_DEFINITIONS.get(ending_id, {})
            status = "✅ 已解鎖" if is_unlocked else "🔒 未解鎖"
            tag = "unlocked" if is_unlocked else "locked"
            ending_text.insert(tk.END, f"{definition.get('name', ending_id)} - {status}\n", tag)
            ending_text.insert(tk.END, f"  📝 {definition.get('description', '')}\n", "desc")
            ending_text.insert(tk.END, f"  📌 條件：{definition.get('condition_text', '未知')}\n", "condition")
            ending_text.insert(tk.END, "\n")
        ending_text.config(state='normal')

        hidden_text.config(state='normal')
        for event_id in codex_data["hidden_events"]["all"]:
            is_unlocked = event_id in codex_data["hidden_events"]["unlocked"]
            definition = HIDDEN_EVENT_DEFINITIONS.get(event_id, {})
            status = "✅ 已觸發" if is_unlocked else "🔒 未觸發"
            tag = "unlocked" if is_unlocked else "locked"
            pos_neg = "positive" if definition.get("is_positive", True) else "negative"
            type_label = "✨ 增益" if definition.get("is_positive", True) else "⚠️ 危機"
            hidden_text.insert(tk.END, f"{definition.get('name', event_id)} - {status} [{type_label}]\n", tag)
            hidden_text.insert(tk.END, f"  📝 {definition.get('description', '')}\n", "desc")
            hidden_text.insert(tk.END, f"  📌 觸發條件：{definition.get('condition_text', '未知')}\n", "condition")
            hidden_text.insert(tk.END, "\n")
        hidden_text.config(state='normal')

        tk.Button(win, text="關閉", command=win.destroy,
                  font=('Arial', 11), bg="#4a4a6a", fg="white", padx=20, pady=5).pack(pady=10)

    # ---- 輔助 ----
    def append_text(self, text: str, tag: str = None):
        if self.view_mode != "story":
            self.set_view_mode("story")
        self.text_area.config(state='normal')
        if tag:
            self.text_area.insert(tk.END, text + "\n", tag)
        else:
            self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state='normal')

    def update_status(self):
        if not self.engine.player:
            return
        p = self.engine.player
        status = (f"👤 {p.name}  |  🎂 {p.age}歲  |  ❤️{p.health}  🧠{p.intelligence}  💪{p.strength}  "
                  f"🗣️{p.charisma}  🍀{p.luck}  🧠{p.sanity}  ✨{p.creativity}  😊{p.happiness}  "
                  f"💰{p.credits}  ⚡{p.action_points}點  |  🎒{len(p.inventory)}件")
        self.status_label.config(text=status)
        self.power_label.config(text=f"🏆 {p.get_power_level()}  |  {p.get_title()}")

    def show_welcome(self):
        self.append_text("=" * 60, "title")
        self.append_text(f"✦ 命運織網 - 天馬行空的人生模擬 RPG  v{VERSION} ✦", "title")
        self.append_text("=" * 60, "title")
        self.append_text(WORLD_BACKGROUND.strip())
        self.append_text("\n點擊「新人生」開始你的旅程！")
        self.append_text("按鈕說明：", "blue")
        self.append_text("  📖 故事 - 主劇情", "blue")
        self.append_text("  🎒 背包 - 查看/使用物品", "blue")
        self.append_text("  🏪 商店 - 買賣物品", "blue")
        self.append_text("  📖 圖鑑 - 查看已解鎖的結局與隱藏事件", "codex")
        self.append_text("  ⚙️ API - 設定 AI 服務", "blue")

    # ---- 角色創造（完整） ----
    def start_new_game(self):
        self.engine.game_over = False
        self.engine.view_mode = "story"
        self.set_view_mode("story")
        self.text_area.config(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state='normal')
        self.open_character_creation()

    def open_character_creation(self):
        win = tk.Toplevel(self.root)
        win.title("角色創造")
        win.geometry("700x650")
        win.resizable(False, False)
        win.configure(bg="#1a1a2e")

        tk.Label(win, text="✦ 角色創造 ✦", font=('Arial', 18, 'bold'),
                 fg="#f0c040", bg="#1a1a2e").pack(pady=10)

        main_frame = tk.Frame(win, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 左側
        left_frame = tk.Frame(main_frame, bg="#1a1a2e")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(left_frame, text="姓名：", font=('Arial', 12),
                 fg="white", bg="#1a1a2e").grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(left_frame, font=('Arial', 12), bg="#2a2a4a", fg="white")
        name_entry.grid(row=0, column=1, sticky='w', pady=5)
        name_entry.insert(0, "節點行者")

        tk.Label(left_frame, text="擲骰結果 (4d6 取最高 3 個，最高 18 點)", font=('Arial', 11),
                 fg="#a0d0ff", bg="#1a1a2e").grid(row=1, column=0, columnspan=2, pady=10)

        roll_frame = tk.Frame(left_frame, bg="#1a1a2e")
        roll_frame.grid(row=2, column=0, columnspan=2, pady=5)
        attr_names = ["健康", "智力", "力量", "魅力", "運氣", "理智", "創造力"]
        self.roll_labels = {}
        for i, name in enumerate(attr_names):
            tk.Label(roll_frame, text=name, font=('Arial', 10), fg="white", bg="#1a1a2e").grid(row=i, column=0, sticky='e')
            lbl = tk.Label(roll_frame, text="?", font=('Arial', 10, 'bold'), fg="#ffd700", bg="#1a1a2e")
            lbl.grid(row=i, column=1, padx=5, sticky='w')
            self.roll_labels[name] = lbl

        def roll_new():
            rolls = self.engine.roll_stats()
            for i, name in enumerate(attr_names):
                self.roll_labels[name].config(text=str(rolls[i]))
            self.current_roll = rolls

        roll_btn = tk.Button(left_frame, text="🎲 重新擲骰", command=roll_new,
                             font=('Arial', 10), bg="#4a4a6a", fg="white")
        roll_btn.grid(row=3, column=0, columnspan=2, pady=10)
        roll_new()

        # 右側（使用 data.TRAIT_LIST）
        right_frame = tk.Frame(main_frame, bg="#1a1a2e")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(right_frame, text="特徵選擇（點數：10）", font=('Arial', 12),
                 fg="#a0d0ff", bg="#1a1a2e").pack(pady=5)

        self.points_var = tk.IntVar(value=10)
        points_label = tk.Label(right_frame, text="剩餘點數：10", font=('Arial', 11, 'bold'),
                                fg="#ffd700", bg="#1a1a2e")
        points_label.pack(pady=2)

        trait_list = TRAIT_LIST  # 從 data 導入

        trait_frame = tk.Frame(right_frame, bg="#1a1a2e")
        trait_frame.pack(fill=tk.BOTH, expand=True)

        buff_frame = tk.Frame(trait_frame, bg="#1a1a2e")
        buff_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(buff_frame, text="🔹 增益（消耗點數）", font=('Arial', 11),
                 fg="#51cf66", bg="#1a1a2e").pack()
        buff_vars = {}
        for t_name, t_desc, t_cost in [t for t in trait_list if t[2] < 0]:
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(buff_frame, text=f"{t_name} ({t_desc})",
                                 variable=var, font=('Arial', 9),
                                 fg="white", bg="#1a1a2e", selectcolor="#1a1a2e",
                                 onvalue=True, offvalue=False)
            chk.pack(anchor='w')
            buff_vars[t_name] = (var, t_cost)

        debuff_frame = tk.Frame(trait_frame, bg="#1a1a2e")
        debuff_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(debuff_frame, text="🔸 減益（增加點數）", font=('Arial', 11),
                 fg="#ff6b6b", bg="#1a1a2e").pack()
        debuff_vars = {}
        for t_name, t_desc, t_cost in [t for t in trait_list if t[2] > 0]:
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(debuff_frame, text=f"{t_name} ({t_desc})",
                                 variable=var, font=('Arial', 9),
                                 fg="white", bg="#1a1a2e", selectcolor="#1a1a2e",
                                 onvalue=True, offvalue=False)
            chk.pack(anchor='w')
            debuff_vars[t_name] = (var, t_cost)

        def update_points(*args):
            total = 10
            for var, cost in buff_vars.values():
                if var.get():
                    total += cost
            for var, cost in debuff_vars.values():
                if var.get():
                    total += cost
            total = max(-5, min(10, total))
            self.points_var.set(total)
            points_label.config(text=f"剩餘點數：{total}")
            if total < 0:
                points_label.config(fg="#ff6b6b")
            else:
                points_label.config(fg="#ffd700")

        for var, cost in buff_vars.values():
            var.trace_add('write', update_points)
        for var, cost in debuff_vars.values():
            var.trace_add('write', update_points)

        def confirm_creation():
            name = name_entry.get().strip()
            if not name:
                name = "節點行者"
            try:
                rolls = [int(self.roll_labels[name].cget("text")) for name in attr_names]
            except:
                messagebox.showerror("錯誤", "請先擲骰")
                return
            selected = []
            for t_name, (var, cost) in buff_vars.items():
                if var.get():
                    selected.append(t_name)
            for t_name, (var, cost) in debuff_vars.items():
                if var.get():
                    selected.append(t_name)

            current_points = self.points_var.get()
            if current_points < 0:
                messagebox.showerror("點數不足", f"剩餘點數為 {current_points}，不能低於 0。\n請重新調整特徵。")
                return

            # 手動建立 Player 並套用特徵
            p = Player(name)
            attrs = ["health", "intelligence", "strength", "charisma", "luck", "sanity", "creativity"]
            for i, attr in enumerate(attrs):
                setattr(p, attr, rolls[i])
            p.traits = selected
            for t in selected:
                if t in TRAIT_EFFECTS:
                    attr, delta = TRAIT_EFFECTS[t]
                    current = getattr(p, attr)
                    setattr(p, attr, max(0, min(100, current + delta)))
            for attr in attrs:
                setattr(p, attr, max(0, min(100, getattr(p, attr))))
            p.story_memory.append("你在命運起點醒來。")
            p.current_scene = "origin"
            p.unlocked_endings = list(self.engine.unlocked_endings)
            p.unlocked_hidden_events = list(self.engine.unlocked_hidden_events)
            self.engine.player = p
            self.engine.game_over = False
            self.engine.year = 0
            self.engine.current_scene = "origin"
            win.destroy()
            self.start_game_after_creation()

        confirm_btn = tk.Button(win, text="✅ 確認創造", command=confirm_creation,
                                font=('Arial', 12, 'bold'), bg="#f0c040", fg="#1a1a2e")
        confirm_btn.pack(pady=10)

    # ---- 遊戲開始 ----
    def start_game_after_creation(self):
        self.end_year_btn.config(state=tk.NORMAL)
        self.inventory_btn.config(state=tk.NORMAL)
        self.shop_btn.config(state=tk.NORMAL)
        self.set_view_mode("story")

        p = self.engine.player
        self.append_text("=" * 60, "title")
        self.append_text(f"✨ {p.name} 降臨命運之網！", "title")
        self.append_text(f"健康:{p.health} 智力:{p.intelligence} 力量:{p.strength} "
                         f"魅力:{p.charisma} 運氣:{p.luck} 理智:{p.sanity} 創造力:{p.creativity}")
        if p.traits:
            self.append_text(f"特性: {', '.join(p.traits)}")

        desc = self.engine.get_scene_description()
        self.append_text(f"\n📍 {desc}")
        npcs = self.engine.get_scene_npcs()
        for npc_id in npcs:
            if npc_id in KEY_NPCS:
                dialogue = self.engine.ai.generate_npc_dialogue(p, npc_id)
                self.append_text(f"👤 {KEY_NPCS[npc_id]['name']}：{dialogue}", "npc")

        self.append_text("\n人生開始！每年 5 個行動。", "gold")
        self.append_text("💡 0 歲教學：試試所有按鈕熟悉操作！", "tutorial")

        if self.engine.ai.last_error:
            self.append_text(f"⚠️ AI 警告：{self.engine.ai.last_error}", "error")
            self.append_text("將使用靜態事件模式，不影響遊戲進行。", "error")

        self.in_tutorial = True
        self.tutorial_step = 0
        self.show_tutorial_step()
        self.update_status()
        self.show_actions()

    def show_tutorial_step(self):
        if not self.in_tutorial or self.engine.player.age > 0:
            self.in_tutorial = False
            return
        steps = [
            "👶 第一步：點擊「漫步」按鈕。",
            "👶 第二步：點擊「研讀」按鈕。",
            "👶 第三步：點擊「工作」按鈕。",
            "👶 第四步：點擊「交際」按鈕。",
            "👶 第五步：點擊「結束年」進入 1 歲。",
        ]
        if self.tutorial_step < len(steps):
            self.append_text(steps[self.tutorial_step], "tutorial")
        else:
            self.in_tutorial = False
            self.append_text("🎉 教學完成！自由探索吧！", "gold")

    def advance_tutorial(self):
        self.tutorial_step += 1
        self.show_tutorial_step()

    # ---- 行動 ----
    def show_actions(self):
        if self.engine.game_over:
            self.hide_buttons()
            return
        if self.engine.last_event and not self.waiting_for_event:
            self.show_event(self.engine.last_event)
            self.engine.last_event = None
            return
        if self.view_mode == "inventory":
            self.show_inventory_actions()
            return
        if self.view_mode == "shop":
            self.show_shop_actions()
            return

        actions = self.engine.get_available_actions()
        display = []
        for action in actions[:4]:
            display.append({
                "text": f"{action['name']} ({action.get('points',1)}點)",
                "command": lambda a=action: self.execute_action(a)
            })
        while len(display) < 4:
            display.append({"text": "", "command": lambda: None})
        self.show_action_buttons(display)

    def execute_action(self, action_data):
        if self.engine.game_over:
            return
        p = self.engine.player
        if p.action_points <= 0:
            self.append_text("行動點已用完，點擊「結束年」繼續。")
            return

        if action_data.get("is_tech"):
            tech = self.engine.unlocked_tech
            if tech:
                self.engine.perform_action(action_data)
                self.append_text(f"🔬 安裝了 {tech['name']}！", "gold")
                self.append_text(f"⚠️ 副作用：{tech['side_effect']}", "highlight")
                self.engine.unlocked_tech = None
                self.update_status()
                self.show_actions()
                if self.in_tutorial and p.age == 0:
                    self.advance_tutorial()
                return

        if action_data.get("is_work"):
            cost_pts = action_data.get("points", 2)
            cost_credits = action_data.get("credits", 0)
            if p.credits < cost_credits:
                self.append_text("信用點不足！", "error")
                return
            if p.action_points < cost_pts:
                self.append_text("行動點不足！", "error")
                return

            result = self.engine.do_work()
            desc = result.get("description", "你努力工作了一天。")
            income = result.get("income", 0)

            p.action_points -= cost_pts
            p.credits -= cost_credits
            p.credits += income
            p.year_actions += 1

            self.append_text(f"💼 {desc}", "gold")
            self.append_text(f"💰 賺取 {income} 信用點", "green")

            self.engine.check_achievements()
            if self.engine.epic_achievement:
                self.append_text(f"\n🌟 史詩時刻：{self.engine.epic_text}", "gold")
                self.engine.epic_achievement = None
                self.engine.epic_text = ""

            if p.action_points <= 0:
                self.engine.next_year()

            if self.engine.game_over:
                self.show_game_over()
                return

            self.update_status()
            self.show_actions()
            if self.in_tutorial and p.age == 0:
                self.advance_tutorial()
            return

        self.engine.perform_action(action_data)
        self.append_text(f"▶ {action_data['name']}")
        if "income" in action_data and action_data["income"]:
            self.append_text(f"賺取 {action_data['income']} 信用點", "green")

        if self.engine.epic_achievement:
            self.append_text(f"\n🌟 史詩時刻：{self.engine.epic_text}", "gold")
            self.engine.epic_achievement = None
            self.engine.epic_text = ""

        if self.engine.last_event and not self.waiting_for_event:
            self.show_event(self.engine.last_event)
            self.engine.last_event = None
            return

        if self.engine.game_over:
            self.show_game_over()
            return

        self.update_status()
        self.show_actions()
        if self.in_tutorial and p.age == 0:
            self.advance_tutorial()

    # ---- 事件 ----
    def show_event(self, event: Dict):
        self.waiting_for_event = True
        is_hidden = event.get("is_hidden", False)
        is_positive = event.get("is_positive", False)
        choices = event.get("choices", [])
        solution = event.get("solution", None)

        self.append_text("\n" + "─" * 40, "blue")
        if is_hidden:
            if is_positive:
                self.append_text(f"✨ 隱藏事件（增益）：{event.get('title', '未知')}", "gold")
            else:
                self.append_text(f"⚠️ 隱藏事件：{event.get('title', '未知')}", "highlight")
        else:
            self.append_text(f"⚡ 事件：{event.get('title', '未知事件')}", "title")
        self.append_text(event.get('description', ''))

        if solution and event.get("is_solvable", True):
            self.append_text(f"💡 解法：{solution}", "solution")

        if is_positive:
            effects = event.get("effects", {})
            for attr, val in effects.items():
                if attr == "flags":
                    for f in val: self.engine.player.flags.add(f)
                else:
                    current = getattr(self.engine.player, attr, 0)
                    setattr(self.engine.player, attr, max(0, min(100, current + val)))
            self.append_text("✅ 事件已自動應用增益！", "green")
            self.waiting_for_event = False
            self.update_status()
            self.show_actions()
            return

        if choices:
            self.show_event_buttons(choices)
            self.event_choices = choices
        else:
            if is_hidden and solution:
                self.show_event_buttons([
                    {"text": "執行解法", "effects": event.get("solution_effects", {})},
                    {"text": "暫時忽略", "effects": {}}
                ])
                self.event_choices = [
                    {"text": "執行解法", "effects": event.get("solution_effects", {})},
                    {"text": "暫時忽略", "effects": {}}
                ]
            else:
                self.show_event_buttons([{"text": "繼續", "effects": {}}])
                self.event_choices = [{"text": "繼續", "effects": {}}]

    def choose_event(self, choice: Dict):
        self.engine.apply_event_choice(choice)
        self.append_text(f"➜ 選擇：{choice.get('text', '未知')}", "gold")

        if self.engine.epic_achievement:
            self.append_text(f"\n🌟 史詩時刻：{self.engine.epic_text}", "gold")
            self.engine.epic_achievement = None
            self.engine.epic_text = ""

        self.waiting_for_event = False
        self.event_choices = []

        if self.engine.game_over:
            self.show_game_over()
            return

        self.update_status()
        self.show_actions()

    # ---- 結束年 ----
    def end_year(self):
        if self.engine.game_over or not self.engine.player:
            return
        p = self.engine.player
        if p.action_points > 0:
            if not messagebox.askyesno("結束今年", f"還有 {p.action_points} 行動點未用，確定結束？"):
                return

        self.engine.next_year()

        if self.engine.game_over:
            self.show_game_over()
            return

        self.append_text("\n" + "=" * 50, "blue")
        self.append_text(f"✦ 第 {p.age} 年 ✦", "title")

        if self.engine.unlocked_tech:
            tech = self.engine.unlocked_tech
            self.append_text(f"\n🔬 科技解鎖：{tech['name']}！", "gold")
            self.append_text(f"描述：{tech['desc']}")
            self.append_text(f"費用：{tech['cost']} 信用點 | 副作用：{tech['side_effect']}", "highlight")
            self.append_text("在行動列表中選擇「安裝」來使用。")

        desc = self.engine.get_scene_description()
        self.append_text(f"\n📍 {desc}")

        npcs = self.engine.get_scene_npcs()
        for npc_id in npcs:
            if npc_id in KEY_NPCS:
                dialogue = self.engine.ai.generate_npc_dialogue(p, npc_id)
                self.append_text(f"👤 {KEY_NPCS[npc_id]['name']}：{dialogue}", "npc")

        if self.engine.epic_achievement:
            self.append_text(f"\n🌟 史詩時刻：{self.engine.epic_text}", "gold")
            self.engine.epic_achievement = None
            self.engine.epic_text = ""

        self.update_status()
        self.show_actions()

        if p.age == 1 and self.in_tutorial:
            self.in_tutorial = False
            self.append_text("🎉 你長大了！教學結束，自由探索吧！", "gold")

    # ---- 遊戲結束 ----
    def show_game_over(self):
        self.hide_buttons()
        self.end_year_btn.config(state=tk.DISABLED)
        self.inventory_btn.config(state=tk.DISABLED)
        self.shop_btn.config(state=tk.DISABLED)

        p = self.engine.player
        self.append_text("\n" + "=" * 60, "death")
        self.append_text("💀 故事終結 💀", "death")
        self.append_text("=" * 60, "death")
        self.append_text(f"角色：{p.name}")
        self.append_text(f"享年：{p.age} 歲")
        self.append_text(f"死因：{p.death_reason}", "highlight")
        self.append_text(f"總財富：{p.credits} 信用點")
        self.append_text(f"成就：{', '.join(p.life_achievements) if p.life_achievements else '無'}")

        codex_data = self.engine.get_codex_data()
        unlocked_endings = len(codex_data["endings"]["unlocked"])
        total_endings = len(codex_data["endings"]["all"])
        unlocked_hidden = len(codex_data["hidden_events"]["unlocked"])
        total_hidden = len(codex_data["hidden_events"]["all"])

        self.append_text("\n📖 圖鑑進度：", "codex")
        self.append_text(f"  🏆 結局：{unlocked_endings}/{total_endings}", "codex")
        self.append_text(f"  ✨ 隱藏事件：{unlocked_hidden}/{total_hidden}", "codex")

        self.append_text("\n" + "=" * 60, "ending")
        self.append_text(f"✦ 結局：{self.engine.ending_title} ✦", "ending")
        self.append_text(f"版本：{self.engine.ending_version_name}", "gold")
        self.append_text(self.engine.ending_text)
        self.append_text("\n🌍 世界的反應：", "title")
        self.append_text(self.engine.world_reaction, "world")
        self.append_text("=" * 60, "ending")

        self.append_text("\n點擊「新人生」重新開始。")
        self.start_btn.config(text="🔄 轉世重生")
        self.update_status()

    # ---- 背包與商店 ----
    def toggle_inventory(self):
        if self.view_mode == "inventory":
            self.set_view_mode("story")
            self.show_actions()
        else:
            self.set_view_mode("inventory")
            self.show_inventory_actions()

    def toggle_shop(self):
        if self.view_mode == "shop":
            self.set_view_mode("story")
            self.show_actions()
        else:
            self.set_view_mode("shop")
            self.show_shop_actions()

    def show_inventory_actions(self):
        p = self.engine.player
        if not p or not p.inventory:
            self.hide_buttons()
            self.btn1.config(text="返回", command=self.toggle_inventory, bg="#4a4a6a", fg="white")
            return
        actions = []
        for i, item in enumerate(p.inventory[:3]):
            actions.append({
                "text": f"使用 {item.get('name', '物品')}",
                "command": lambda it=item: self.use_item(it)
            })
        actions.append({"text": "返回", "command": self.toggle_inventory})
        self.show_action_buttons(actions)

    def use_item(self, item):
        p = self.engine.player
        if not p: return
        effect = p.use_item(item.get("id"))
        if effect:
            for attr, val in effect.items():
                if attr == "flags":
                    for f in val: p.flags.add(f)
                else:
                    current = getattr(p, attr, 0)
                    setattr(p, attr, max(0, min(100, current + val)))
            self.append_text(f"💊 使用了 {item.get('name')}", "gold")
            self.refresh_inventory_view()
            self.update_status()
            self.show_inventory_actions()

    def show_shop_actions(self):
        actions = [
            {"text": "購買", "command": self.buy_selected},
            {"text": "賣出", "command": self.sell_selected},
            {"text": "返回", "command": self.toggle_shop}
        ]
        self.show_action_buttons(actions)

    def buy_selected(self):
        p = self.engine.player
        if not p: return
        items = [f"{item['name']} (💰{item['price']})" for item in self.engine.shop_items]
        items.append("取消")
        choice = simpledialog.askstring("購買物品",
                                         "輸入要購買的物品編號：\n" +
                                         "\n".join([f"{i+1}. {name}" for i, name in enumerate(items)]),
                                         parent=self.root)
        if not choice: return
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(self.engine.shop_items):
                item = self.engine.shop_items[idx]
                if self.engine.buy_item(item["id"]):
                    self.append_text(f"🛒 購買了 {item['name']}", "green")
                    self.refresh_shop_view()
                    self.update_status()
                else:
                    self.append_text("❌ 信用點不足！", "error")
        except ValueError:
            pass

    def sell_selected(self):
        p = self.engine.player
        if not p or not p.inventory:
            self.append_text("背包是空的！", "error")
            return
        items = [f"{item['name']}" for item in p.inventory]
        items.append("取消")
        choice = simpledialog.askstring("賣出物品",
                                         "輸入要賣出的物品編號（半價）：\n" +
                                         "\n".join([f"{i+1}. {name}" for i, name in enumerate(items)]),
                                         parent=self.root)
        if not choice: return
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(p.inventory):
                item = p.inventory[idx]
                if self.engine.sell_item(item["id"]):
                    self.append_text(f"💰 賣出了 {item['name']}", "green")
                    self.refresh_shop_view()
                    self.update_status()
        except ValueError:
            pass

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    app.run()