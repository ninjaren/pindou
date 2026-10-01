import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from PIL import Image, ImageTk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    _DND_AVAILABLE = True
except ImportError:
    _DND_AVAILABLE = False

from beads_logic import generate_beads_pattern, build_color_statistics, merge_similar_colors
from preview_utils import build_preview_image
from export_utils import save_image_file, export_color_statistics_csv


class BeadsGuiPretty:
    def __init__(self, root):
        self.root = root
        self.root.title("拼豆圖工具 v0.7")
        self.root.geometry("1280x860")
        self.root.minsize(1100, 760)

        self.grid_size = tk.IntVar(value=52)
        self.cell_size = tk.IntVar(value=14)
        self.show_grid = tk.BooleanVar(value=True)
        self.show_number = tk.BooleanVar(value=False)
        self.keep_ratio = tk.BooleanVar(value=True)

        # 影像處理選項
        self.ignore_bg_type = tk.StringVar(value="去除黑底")
        self.pre_quantize_colors = tk.IntVar(value=12)
        self.color_merge_threshold = tk.IntVar(value=30)
        self.noise_removal = tk.BooleanVar(value=True)

        # 資料狀態
        self.original_image = None    # PIL Image（原圖）
        self.preview_image = None     # PIL Image（拼豆圖預覽）
        self.color_statistics = None  # 顏色統計清單
        self.image_stem = None        # 原檔名（不含副檔名）

        # PhotoImage 參照（防止被 GC 回收導致圖片消失）
        self._original_photo = None
        self._pattern_photo = None

        self._setup_style()
        self._build_ui()

    def _setup_style(self):
        style = ttk.Style()

        try:
            style.theme_use("clam")
        except Exception:
            pass

        self.root.configure(bg="#eef2f7")

        style.configure(
            "App.TFrame",
            background="#eef2f7"
        )

        style.configure(
            "Card.TFrame",
            background="#ffffff",
            relief="flat"
        )

        style.configure(
            "Toolbar.TFrame",
            background="#eef2f7"
        )

        style.configure(
            "Title.TLabel",
            background="#eef2f7",
            foreground="#1f2937",
            font=("Microsoft JhengHei UI", 20, "bold")
        )

        style.configure(
            "SubTitle.TLabel",
            background="#eef2f7",
            foreground="#6b7280",
            font=("Microsoft JhengHei UI", 10)
        )

        style.configure(
            "Section.TLabelframe",
            background="#ffffff",
            foreground="#1f2937",
            borderwidth=1,
            relief="solid"
        )

        style.configure(
            "Section.TLabelframe.Label",
            background="#ffffff",
            foreground="#111827",
            font=("Microsoft JhengHei UI", 11, "bold")
        )

        style.configure(
            "Field.TLabel",
            background="#ffffff",
            foreground="#374151",
            font=("Microsoft JhengHei UI", 10)
        )

        style.configure(
            "StatusTitle.TLabel",
            background="#ffffff",
            foreground="#111827",
            font=("Microsoft JhengHei UI", 10, "bold")
        )

        style.configure(
            "StatusValue.TLabel",
            background="#ffffff",
            foreground="#2563eb",
            font=("Microsoft JhengHei UI", 10)
        )

        style.configure(
            "Primary.TButton",
            font=("Microsoft JhengHei UI", 10, "bold"),
            padding=(14, 10),
            foreground="#ffffff",
            background="#2563eb",
            borderwidth=0
        )
        style.map(
            "Primary.TButton",
            background=[("active", "#1d4ed8"), ("pressed", "#1e40af")]
        )

        style.configure(
            "Secondary.TButton",
            font=("Microsoft JhengHei UI", 10),
            padding=(12, 10),
            foreground="#111827",
            background="#ffffff",
            borderwidth=1
        )
        style.map(
            "Secondary.TButton",
            background=[("active", "#f3f4f6"), ("pressed", "#e5e7eb")]
        )

        style.configure(
            "Tool.TButton",
            font=("Microsoft JhengHei UI", 10),
            padding=(12, 8)
        )

        style.configure(
            "App.TCheckbutton",
            background="#ffffff",
            foreground="#374151",
            font=("Microsoft JhengHei UI", 10)
        )

    def _build_ui(self):
        outer = ttk.Frame(self.root, style="App.TFrame", padding=18)
        outer.pack(fill="both", expand=True)

        self._build_header(outer)
        self._build_toolbar(outer)
        self._build_body(outer)

    def _build_header(self, parent):
        header = ttk.Frame(parent, style="App.TFrame")
        header.pack(fill="x", pady=(0, 12))

        ttk.Label(
            header,
            text="拼豆圖工具",
            style="Title.TLabel"
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="把圖片轉成適合拼豆製作的格子設計圖",
            style="SubTitle.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        ttk.Label(
            header,
            text="作者：Allen Lin　　v0.7",
            style="SubTitle.TLabel"
        ).pack(anchor="w")

    def _build_toolbar(self, parent):
        toolbar = ttk.Frame(parent, style="Toolbar.TFrame")
        toolbar.pack(fill="x", pady=(0, 14))

        ttk.Button(toolbar, text="開啟圖片", style="Primary.TButton", command=self.open_image).pack(side="left", padx=(0, 8))
        self._generate_btn = ttk.Button(toolbar, text="產生拼豆圖", style="Secondary.TButton", command=self.generate_pattern)
        self._generate_btn.pack(side="left", padx=8)
        ttk.Button(toolbar, text="儲存拼豆圖", style="Secondary.TButton", command=self.save_pattern).pack(side="left", padx=8)
        ttk.Button(toolbar, text="匯出顏色統計", style="Secondary.TButton", command=self.export_colors).pack(side="left", padx=8)

    def _build_body(self, parent):
        body = ttk.Frame(parent, style="App.TFrame")
        body.pack(fill="both", expand=True)

        self._build_left_panel(body)
        self._build_right_panel(body)

    def _build_left_panel(self, parent):
        left_wrap = ttk.Frame(parent, style="App.TFrame")
        left_wrap.pack(side="left", fill="y", padx=(0, 14))

        settings = ttk.LabelFrame(left_wrap, text="參數設定", style="Section.TLabelframe", padding=16)
        settings.pack(fill="x")

        ttk.Label(settings, text="切割數量", style="Field.TLabel").grid(row=0, column=0, sticky="w", pady=8)
        ttk.Spinbox(settings, from_=10, to=300, textvariable=self.grid_size, width=10).grid(row=0, column=1, sticky="ew", pady=8)

        ttk.Label(settings, text="每格大小", style="Field.TLabel").grid(row=1, column=0, sticky="w", pady=8)
        ttk.Spinbox(settings, from_=4, to=50, textvariable=self.cell_size, width=10).grid(row=1, column=1, sticky="ew", pady=8)

        settings.columnconfigure(1, weight=1)

        sep = ttk.Separator(settings, orient="horizontal")
        sep.grid(row=2, column=0, columnspan=2, sticky="ew", pady=12)

        ttk.Checkbutton(settings, text="顯示格線", variable=self.show_grid, style="App.TCheckbutton").grid(row=3, column=0, columnspan=2, sticky="w", pady=6)
        ttk.Checkbutton(settings, text="顯示編號", variable=self.show_number, style="App.TCheckbutton").grid(row=4, column=0, columnspan=2, sticky="w", pady=6)
        ttk.Checkbutton(settings, text="維持原圖比例", variable=self.keep_ratio, style="App.TCheckbutton").grid(row=5, column=0, columnspan=2, sticky="w", pady=6)

        sep2 = ttk.Separator(settings, orient="horizontal")
        sep2.grid(row=6, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Label(settings, text="背景處理", style="Field.TLabel").grid(row=7, column=0, sticky="w", pady=6)
        ttk.Combobox(
            settings,
            textvariable=self.ignore_bg_type,
            values=["不處理", "去除黑底", "去除白底"],
            state="readonly",
            font=("Microsoft JhengHei UI", 10),
            width=8,
        ).grid(row=7, column=1, sticky="ew", pady=6)

        ttk.Label(settings, text="量化色數", style="Field.TLabel").grid(row=8, column=0, sticky="w", pady=6)
        ttk.Spinbox(
            settings, from_=0, to=32,
            textvariable=self.pre_quantize_colors, width=10
        ).grid(row=8, column=1, sticky="ew", pady=6)

        ttk.Label(settings, text="合併閾值", style="Field.TLabel").grid(row=9, column=0, sticky="w", pady=6)
        ttk.Spinbox(
            settings, from_=0, to=100,
            textvariable=self.color_merge_threshold, width=10
        ).grid(row=9, column=1, sticky="ew", pady=6)

        ttk.Checkbutton(settings, text="雜點消除", variable=self.noise_removal, style="App.TCheckbutton").grid(row=10, column=0, columnspan=2, sticky="w", pady=6)

        status = ttk.LabelFrame(left_wrap, text="狀態資訊", style="Section.TLabelframe", padding=16)
        status.pack(fill="x", pady=(14, 0))

        ttk.Label(status, text="目前狀態", style="StatusTitle.TLabel").pack(anchor="w")
        self.status_label = ttk.Label(status, text="尚未載入圖片", style="StatusValue.TLabel")
        self.status_label.pack(anchor="w", pady=(4, 12))

        ttk.Label(status, text="目前設定", style="StatusTitle.TLabel").pack(anchor="w")
        self.setting_label = ttk.Label(
            status,
            text="52 x 52 / 每格 14",
            style="Field.TLabel"
        )
        self.setting_label.pack(anchor="w", pady=(4, 0))

        tips = ttk.LabelFrame(left_wrap, text="小提醒", style="Section.TLabelframe", padding=16)
        tips.pack(fill="x", pady=(14, 0))

        tip_text = (
            "• 先從 52 x 52 開始最穩定\n"
            "• 圖片越簡單，拼豆效果越好\n"
            "• 人物圖建議先裁切主體再轉換"
        )
        ttk.Label(tips, text=tip_text, style="Field.TLabel", justify="left").pack(anchor="w")

    def _build_right_panel(self, parent):
        right_wrap = ttk.Frame(parent, style="App.TFrame")
        right_wrap.pack(side="left", fill="both", expand=True)

        preview_row = ttk.Frame(right_wrap, style="App.TFrame")
        preview_row.pack(fill="both", expand=True)

        original_box = ttk.LabelFrame(preview_row, text="原圖預覽", style="Section.TLabelframe", padding=12)
        original_box.pack(side="left", fill="both", expand=True, padx=(0, 7))

        self.original_canvas = tk.Canvas(
            original_box,
            bg="#f8fafc",
            highlightthickness=1,
            highlightbackground="#d1d5db",
            bd=0
        )
        self.original_canvas.pack(fill="both", expand=True)
        self._draw_placeholder(self.original_canvas, "原圖顯示區")

        # 拖曳開啟圖片
        if _DND_AVAILABLE:
            self.original_canvas.drop_target_register(DND_FILES)
            self.original_canvas.dnd_bind("<<Drop>>", self._on_drop)

        pattern_box = ttk.LabelFrame(preview_row, text="拼豆圖預覽", style="Section.TLabelframe", padding=12)
        pattern_box.pack(side="left", fill="both", expand=True, padx=(7, 0))

        self.pattern_canvas = tk.Canvas(
            pattern_box,
            bg="#f8fafc",
            highlightthickness=1,
            highlightbackground="#d1d5db",
            bd=0
        )
        self.pattern_canvas.pack(fill="both", expand=True)
        self._draw_placeholder(self.pattern_canvas, "拼豆圖顯示區")

        self._build_bottom(right_wrap)

    def _build_bottom(self, parent):
        bottom = ttk.LabelFrame(parent, text="顏色統計", style="Section.TLabelframe", padding=12)
        bottom.pack(fill="x", pady=(10, 0))

        text_frame = ttk.Frame(bottom, style="Card.TFrame")
        text_frame.pack(fill="x")

        self.color_text = tk.Text(
            text_frame,
            height=7,
            font=("Consolas", 10),
            bg="#f8fafc",
            fg="#111827",
            relief="flat",
            wrap="word",
            padx=12,
            pady=8
        )
        self.color_text.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(text_frame, orient="vertical", command=self.color_text.yview)
        scroll.pack(side="right", fill="y")
        self.color_text.configure(yscrollcommand=scroll.set)

        self.color_text.insert(
            "1.0",
            "產生拼豆圖後，這裡會顯示用色統計（顏色名稱、RGB、顆數）。"
        )

    def _draw_placeholder(self, canvas, text):
        canvas.delete("all")
        canvas.update_idletasks()

        w = max(canvas.winfo_width(), 300)
        h = max(canvas.winfo_height(), 300)

        canvas.create_rectangle(20, 20, w - 20, h - 20, outline="#cbd5e1", width=2, dash=(6, 4))
        canvas.create_text(
            w / 2,
            h / 2,
            text=text,
            fill="#64748b",
            font=("Microsoft JhengHei UI", 15, "bold")
        )

    def _refresh_setting_label(self):
        self.setting_label.config(
            text=f"{self.grid_size.get()} x {self.grid_size.get()} / 每格 {self.cell_size.get()}"
        )

    def _display_on_canvas(self, canvas, pil_image):
        """將 PIL Image 等比縮放後顯示於 Canvas 中央，回傳 PhotoImage 參照"""
        canvas.delete("all")
        canvas.update_idletasks()

        cw = canvas.winfo_width()
        ch = canvas.winfo_height()
        if cw < 10 or ch < 10:
            cw, ch = 400, 400

        img = pil_image.copy()
        img.thumbnail((cw, ch), Image.Resampling.LANCZOS)

        photo = ImageTk.PhotoImage(img)
        canvas.create_image(cw // 2, ch // 2, anchor="center", image=photo)
        return photo  # 呼叫端必須保留此參照

    def _on_drop(self, event):
        """處理拖曳進來的檔案"""
        raw = event.data.strip()
        # Windows 路徑若含空格會被 {} 包圍，多個檔案以空格分隔
        # 格式可能是：{C:/path/file.png} 或 C:/path/file.png
        if raw.startswith("{"):
            # 取第一個 {...} 區塊
            end = raw.find("}")
            file_path = raw[1:end] if end != -1 else raw[1:]
        else:
            # 無大括號，取第一個空白之前的部分
            file_path = raw.split()[0]
        if file_path:
            self._load_image_from_path(file_path)

    def open_image(self):
        file_path = filedialog.askopenfilename(
            title="選擇圖片",
            filetypes=[("圖片檔", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if not file_path:
            return
        self._load_image_from_path(file_path)

    def _load_image_from_path(self, file_path):
        try:
            raw = Image.open(file_path)
            if raw.mode in ("RGBA", "LA") or (raw.mode == "P" and "transparency" in raw.info):
                # 將透明區域合成到白色背景，避免 convert("RGB") 把透明變黑色
                raw = raw.convert("RGBA")
                white_bg = Image.new("RGBA", raw.size, (255, 255, 255, 255))
                white_bg.paste(raw, mask=raw.split()[3])
                img = white_bg.convert("RGB")
            else:
                img = raw.convert("RGB")
        except Exception as e:
            messagebox.showerror("錯誤", f"圖片開啟失敗：{e}")
            return

        self.original_image = img
        self.image_stem = os.path.splitext(os.path.basename(file_path))[0]

        w, h = img.size
        self.status_label.config(
            text=f"已載入：{os.path.basename(file_path)}  ({w} x {h})"
        )
        self._refresh_setting_label()
        self._original_photo = self._display_on_canvas(self.original_canvas, img)

    def generate_pattern(self):
        if self.original_image is None:
            messagebox.showwarning("提示", "請先開啟圖片")
            return

        self._generate_btn.config(state="disabled", text="產生中...")
        self._refresh_setting_label()
        self.status_label.config(text="產生中，請稍候...")
        self.root.update_idletasks()

        # 在主執行緒擷取所有 Tk 變數（StringVar/IntVar 不可在子執行緒存取）
        params = dict(
            grid_size=self.grid_size.get(),
            keep_ratio=self.keep_ratio.get(),
            ignore_bg={"不處理": None, "去除黑底": "black", "去除白底": "white"}.get(
                self.ignore_bg_type.get(), None
            ),
            pre_quantize_colors=self.pre_quantize_colors.get(),
            threshold=self.color_merge_threshold.get(),
            noise_removal=self.noise_removal.get(),
            cell_size=self.cell_size.get(),
            show_grid=self.show_grid.get(),
            show_symbol=self.show_number.get(),
            image=self.original_image,
        )

        def _worker():
            try:
                result = generate_beads_pattern(
                    image=params["image"],
                    grid_width=params["grid_size"],
                    grid_height=params["grid_size"],
                    keep_ratio=params["keep_ratio"],
                    ignore_bg=params["ignore_bg"],
                    pre_quantize_colors=params["pre_quantize_colors"],
                    noise_removal=params["noise_removal"],
                )
                color_stats = build_color_statistics(result["color_counter"])
                palette_map = result["palette_map"]
                if params["threshold"] > 0:
                    palette_map, color_stats = merge_similar_colors(
                        palette_map, color_stats, params["threshold"]
                    )
                preview = build_preview_image(
                    small_image=result["small_image"],
                    palette_map=palette_map,
                    color_statistics=color_stats,
                    cell_size=params["cell_size"],
                    show_grid=params["show_grid"],
                    show_symbol=params["show_symbol"],
                )
                self.root.after(0, lambda: _on_done(result, palette_map, color_stats, preview))
            except Exception as e:
                self.root.after(0, lambda: _on_error(e))

        def _on_done(result, palette_map, color_stats, preview):
            self.color_statistics = color_stats
            self.preview_image = preview
            self._pattern_photo = self._display_on_canvas(self.pattern_canvas, self.preview_image)
            self._update_color_text()
            total = result["grid_width"] * result["grid_height"]
            color_count = len(self.color_statistics)
            self.status_label.config(
                text=f"完成！{result['grid_width']} x {result['grid_height']} 格 | 共 {total} 顆 | {color_count} 種顏色"
            )
            self._generate_btn.config(state="normal", text="產生拼豆圖")

        def _on_error(e):
            messagebox.showerror("錯誤", f"產生拼豆圖失敗：{e}")
            self.status_label.config(text="產生失敗")
            self._generate_btn.config(state="normal", text="產生拼豆圖")

        threading.Thread(target=_worker, daemon=True).start()

    def _update_color_text(self):
        """更新底部顏色統計文字區域"""
        self.color_text.delete("1.0", "end")

        total = sum(item["count"] for item in self.color_statistics)
        color_count = len(self.color_statistics)

        lines = [
            f"總拼豆數：{total} 顆　　使用顏色：{color_count} 種",
            "─" * 48,
            ""
        ]

        for idx, item in enumerate(self.color_statistics, start=1):
            r, g, b = item["rgb"]
            lines.append(
                f"{idx:02d}. {item['name']:<4}  RGB({r:3d},{g:3d},{b:3d})  {item['count']:5d} 顆"
            )

        lines += [
            "",
            "─" * 48,
            "若有開啟「顯示符號」，上方清單順序就是符號編號。"
        ]

        self.color_text.insert("1.0", "\n".join(lines))

    def save_pattern(self):
        if self.preview_image is None:
            messagebox.showwarning("提示", "請先產生拼豆圖")
            return

        stem = self.image_stem or "beads"
        default_name = f"{stem}_beads_pattern.png"

        file_path = filedialog.asksaveasfilename(
            title="儲存拼豆圖",
            defaultextension=".png",
            initialfile=default_name,
            filetypes=[("PNG 圖片", "*.png"), ("JPEG 圖片", "*.jpg"), ("BMP 圖片", "*.bmp")]
        )
        if not file_path:
            return

        try:
            save_image_file(self.preview_image, file_path)
            messagebox.showinfo("完成", f"拼豆圖已儲存：\n{file_path}")
        except Exception as e:
            messagebox.showerror("錯誤", f"儲存失敗：{e}")

    def export_colors(self):
        if self.color_statistics is None:
            messagebox.showwarning("提示", "請先產生拼豆圖")
            return

        stem = self.image_stem or "beads"
        default_name = f"{stem}_beads_colors.csv"

        file_path = filedialog.asksaveasfilename(
            title="匯出顏色統計 CSV",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV 檔案", "*.csv")]
        )
        if not file_path:
            return

        try:
            export_color_statistics_csv(self.color_statistics, file_path)
            messagebox.showinfo("完成", f"顏色統計已匯出：\n{file_path}")
        except Exception as e:
            messagebox.showerror("錯誤", f"匯出失敗：{e}")


def main():
    if _DND_AVAILABLE:
        root = TkinterDnD.Tk()
    else:
        root = tk.Tk()
    app = BeadsGuiPretty(root)

    _resize_original_job = None
    _resize_pattern_job = None

    def on_resize_original(event):
        nonlocal _resize_original_job
        if _resize_original_job is not None:
            root.after_cancel(_resize_original_job)
        def _do():
            if app.original_image is not None:
                app._original_photo = app._display_on_canvas(app.original_canvas, app.original_image)
            else:
                app._draw_placeholder(app.original_canvas, "原圖顯示區")
        _resize_original_job = root.after(150, _do)

    def on_resize_pattern(event):
        nonlocal _resize_pattern_job
        if _resize_pattern_job is not None:
            root.after_cancel(_resize_pattern_job)
        def _do():
            if app.preview_image is not None:
                app._pattern_photo = app._display_on_canvas(app.pattern_canvas, app.preview_image)
            else:
                app._draw_placeholder(app.pattern_canvas, "拼豆圖顯示區")
        _resize_pattern_job = root.after(150, _do)

    app.original_canvas.bind("<Configure>", on_resize_original)
    app.pattern_canvas.bind("<Configure>", on_resize_pattern)

    root.mainloop()


if __name__ == "__main__":
    main()