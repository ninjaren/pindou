import os
import csv
import math
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import Counter
from PIL import Image, ImageTk, ImageDraw, ImageFont


# =========================
# 可自訂的拼豆色盤
# =========================
# name: 顏色名稱
# rgb : 顏色值
BEADS_PALETTE = [
    {"name": "白色", "rgb": (255, 255, 255)},
    {"name": "黑色", "rgb": (0, 0, 0)},
    {"name": "淺灰", "rgb": (200, 200, 200)},
    {"name": "深灰", "rgb": (120, 120, 120)},
    {"name": "紅色", "rgb": (220, 20, 60)},
    {"name": "粉紅", "rgb": (255, 182, 193)},
    {"name": "桃紅", "rgb": (255, 105, 180)},
    {"name": "橘色", "rgb": (255, 140, 0)},
    {"name": "膚色", "rgb": (245, 205, 170)},
    {"name": "黃色", "rgb": (255, 215, 0)},
    {"name": "奶油黃", "rgb": (255, 239, 170)},
    {"name": "淺綠", "rgb": (144, 238, 144)},
    {"name": "綠色", "rgb": (34, 139, 34)},
    {"name": "深綠", "rgb": (0, 100, 0)},
    {"name": "薄荷綠", "rgb": (152, 255, 152)},
    {"name": "淺藍", "rgb": (173, 216, 230)},
    {"name": "天藍", "rgb": (135, 206, 235)},
    {"name": "藍色", "rgb": (30, 144, 255)},
    {"name": "深藍", "rgb": (25, 25, 112)},
    {"name": "紫色", "rgb": (138, 43, 226)},
    {"name": "淡紫", "rgb": (216, 191, 216)},
    {"name": "咖啡", "rgb": (139, 69, 19)},
    {"name": "淺咖啡", "rgb": (181, 101, 29)},
    {"name": "米色", "rgb": (245, 245, 220)},
]


def rgb_distance(c1, c2):
    """計算兩個 RGB 顏色距離"""
    return math.sqrt(
        (c1[0] - c2[0]) ** 2 +
        (c1[1] - c2[1]) ** 2 +
        (c1[2] - c2[2]) ** 2
    )


def find_nearest_palette_color(rgb, palette):
    """找出最接近的拼豆色盤顏色"""
    best = None
    best_dist = float("inf")

    for item in palette:
        dist = rgb_distance(rgb, item["rgb"])
        if dist < best_dist:
            best_dist = dist
            best = item

    return best


class BeadsPatternToolV2:
    def __init__(self, root):
        self.root = root
        self.root.title("拼豆圖產生器 v2")
        self.root.geometry("1320x900")

        self.original_image = None
        self.original_path = None

        # small pattern：真正格子資料，例如 52x52
        self.pattern_small = None

        # preview：放大後圖
        self.pattern_preview = None

        # 每格對應的拼豆色資訊
        self.pattern_palette_map = []  # 2D list: [[palette_item, ...], ...]

        # 統計結果
        self.color_counter = Counter()

        # 參數
        self.grid_width_var = tk.IntVar(value=52)
        self.grid_height_var = tk.IntVar(value=52)
        self.cell_size_var = tk.IntVar(value=14)
        self.show_grid_var = tk.BooleanVar(value=True)
        self.keep_ratio_var = tk.BooleanVar(value=True)
        self.show_symbol_var = tk.BooleanVar(value=False)

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self.root, padx=10, pady=10)
        top.pack(side=tk.TOP, fill=tk.X)

        tk.Button(top, text="開啟圖片", width=12, command=self.open_image).grid(row=0, column=0, padx=4, pady=4)
        tk.Button(top, text="產生拼豆圖", width=12, command=self.generate_pattern).grid(row=0, column=1, padx=4, pady=4)
        tk.Button(top, text="儲存拼豆圖", width=12, command=self.save_pattern_image).grid(row=0, column=2, padx=4, pady=4)
        tk.Button(top, text="匯出顏色統計 CSV", width=16, command=self.export_color_csv).grid(row=0, column=3, padx=4, pady=4)

        tk.Label(top, text="寬格數").grid(row=0, column=4, padx=4)
        tk.Spinbox(top, from_=8, to=300, width=6, textvariable=self.grid_width_var).grid(row=0, column=5, padx=4)

        tk.Label(top, text="高格數").grid(row=0, column=6, padx=4)
        tk.Spinbox(top, from_=8, to=300, width=6, textvariable=self.grid_height_var).grid(row=0, column=7, padx=4)

        tk.Label(top, text="每格大小").grid(row=0, column=8, padx=4)
        tk.Spinbox(top, from_=4, to=50, width=6, textvariable=self.cell_size_var).grid(row=0, column=9, padx=4)

        tk.Checkbutton(top, text="顯示格線", variable=self.show_grid_var).grid(row=0, column=10, padx=8)
        tk.Checkbutton(top, text="維持比例", variable=self.keep_ratio_var).grid(row=0, column=11, padx=8)
        tk.Checkbutton(top, text="顯示符號", variable=self.show_symbol_var).grid(row=0, column=12, padx=8)

        self.info_label = tk.Label(self.root, text="請先開啟圖片", anchor="w", padx=10)
        self.info_label.pack(fill=tk.X)

        middle = tk.Frame(self.root, padx=10, pady=10)
        middle.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.LabelFrame(middle, text="原圖", padx=8, pady=8)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        right_frame = tk.LabelFrame(middle, text="拼豆圖預覽", padx=8, pady=8)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.original_preview_label = tk.Label(left_frame, bg="#e8e8e8")
        self.original_preview_label.pack(fill=tk.BOTH, expand=True)

        self.pattern_preview_label = tk.Label(right_frame, bg="#e8e8e8")
        self.pattern_preview_label.pack(fill=tk.BOTH, expand=True)

        bottom = tk.Frame(self.root, padx=10, pady=10)
        bottom.pack(fill=tk.BOTH)

        tk.Label(bottom, text="顏色統計（名稱 / RGB / 顆數）").pack(anchor="w")
        self.color_text = tk.Text(bottom, height=14)
        self.color_text.pack(fill=tk.BOTH, expand=False)

    def open_image(self):
        path = filedialog.askopenfilename(
            title="選擇圖片",
            filetypes=[
                ("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp"),
                ("All Files", "*.*")
            ]
        )
        if not path:
            return

        try:
            self.original_image = Image.open(path).convert("RGB")
            self.original_path = path

            self.pattern_small = None
            self.pattern_preview = None
            self.pattern_palette_map = []
            self.color_counter = Counter()

            self._show_fit_preview(self.original_image, self.original_preview_label, max_w=560, max_h=560)
            self.pattern_preview_label.config(image="")
            self.pattern_preview_label.image = None
            self.color_text.delete("1.0", tk.END)

            self.info_label.config(
                text=f"已載入：{os.path.basename(path)} | 原圖尺寸：{self.original_image.width} x {self.original_image.height}"
            )
        except Exception as e:
            messagebox.showerror("錯誤", f"圖片開啟失敗：\n{e}")

    def generate_pattern(self):
        if self.original_image is None:
            messagebox.showwarning("提醒", "請先開啟圖片")
            return

        try:
            grid_w = max(1, self.grid_width_var.get())
            grid_h = max(1, self.grid_height_var.get())
            cell_size = max(4, self.cell_size_var.get())

            img = self.original_image.copy()

            # 先縮到指定格數
            if self.keep_ratio_var.get():
                img.thumbnail((grid_w, grid_h), Image.Resampling.LANCZOS)
                canvas = Image.new("RGB", (grid_w, grid_h), (255, 255, 255))
                paste_x = (grid_w - img.width) // 2
                paste_y = (grid_h - img.height) // 2
                canvas.paste(img, (paste_x, paste_y))
                img = canvas
            else:
                img = img.resize((grid_w, grid_h), Image.Resampling.LANCZOS)

            # 映射到固定拼豆色盤
            mapped = Image.new("RGB", (grid_w, grid_h))
            self.pattern_palette_map = []
            self.color_counter = Counter()

            for y in range(grid_h):
                row = []
                for x in range(grid_w):
                    rgb = img.getpixel((x, y))
                    nearest = find_nearest_palette_color(rgb, BEADS_PALETTE)
                    mapped.putpixel((x, y), nearest["rgb"])
                    row.append(nearest)
                    self.color_counter[nearest["name"]] += 1
                self.pattern_palette_map.append(row)

            self.pattern_small = mapped

            self.pattern_preview = self._build_preview_image(
                cell_size=cell_size,
                show_grid=self.show_grid_var.get(),
                show_symbol=self.show_symbol_var.get()
            )

            self._show_fit_preview(self.pattern_preview, self.pattern_preview_label, max_w=560, max_h=560)
            self._update_color_statistics()

            self.info_label.config(
                text=(
                    f"拼豆圖完成 | 格數：{grid_w} x {grid_h} | "
                    f"使用色數：{len(self.color_counter)} | "
                    f"預覽尺寸：{self.pattern_preview.width} x {self.pattern_preview.height}"
                )
            )

        except Exception as e:
            messagebox.showerror("錯誤", f"產生拼豆圖失敗：\n{e}")

    def _build_preview_image(self, cell_size, show_grid, show_symbol):
        """建立放大預覽圖"""
        if self.pattern_small is None:
            return None

        w, h = self.pattern_small.size
        out_w = w * cell_size
        out_h = h * cell_size

        preview = Image.new("RGB", (out_w, out_h), "white")
        draw = ImageDraw.Draw(preview)

        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

        # 建立顏色名稱到符號的對應
        used_color_names = sorted(self.color_counter.keys())
        symbol_map = {}
        for idx, name in enumerate(used_color_names, start=1):
            symbol_map[name] = str(idx)

        for y in range(h):
            for x in range(w):
                item = self.pattern_palette_map[y][x]
                color = item["rgb"]
                name = item["name"]

                x1 = x * cell_size
                y1 = y * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size

                draw.rectangle([x1, y1, x2, y2], fill=color)

                if show_symbol and cell_size >= 12:
                    # 判斷文字顏色，避免看不清楚
                    brightness = (color[0] * 299 + color[1] * 587 + color[2] * 114) / 1000
                    text_color = (0, 0, 0) if brightness > 160 else (255, 255, 255)

                    symbol = symbol_map[name]
                    bbox = draw.textbbox((0, 0), symbol, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]

                    tx = x1 + (cell_size - text_w) / 2
                    ty = y1 + (cell_size - text_h) / 2

                    draw.text((tx, ty), symbol, fill=text_color, font=font)

        if show_grid and cell_size >= 4:
            grid_color = (170, 170, 170)
            for x in range(w + 1):
                xx = x * cell_size
                draw.line([(xx, 0), (xx, out_h)], fill=grid_color, width=1)
            for y in range(h + 1):
                yy = y * cell_size
                draw.line([(0, yy), (out_w, yy)], fill=grid_color, width=1)

        return preview

    def _update_color_statistics(self):
        self.color_text.delete("1.0", tk.END)

        if not self.color_counter:
            return

        total = sum(self.color_counter.values())
        used_items = []

        for item in BEADS_PALETTE:
            name = item["name"]
            if name in self.color_counter:
                used_items.append({
                    "name": name,
                    "rgb": item["rgb"],
                    "count": self.color_counter[name]
                })

        used_items.sort(key=lambda x: x["count"], reverse=True)

        self.color_text.insert(tk.END, f"總拼豆數：{total}\n")
        self.color_text.insert(tk.END, f"使用顏色種類：{len(used_items)}\n")
        self.color_text.insert(tk.END, "-" * 60 + "\n")

        for idx, item in enumerate(used_items, start=1):
            self.color_text.insert(
                tk.END,
                f"{idx:02d}. {item['name']} | RGB{item['rgb']} | {item['count']} 顆\n"
            )

        self.color_text.insert(tk.END, "-" * 60 + "\n")
        self.color_text.insert(tk.END, "若有開啟『顯示符號』，上方清單順序就是符號編號。\n")
        self.color_text.insert(tk.END, "例如：01 = 白色，02 = 黑色，03 = 紅色 ...\n")

    def save_pattern_image(self):
        if self.pattern_preview is None:
            messagebox.showwarning("提醒", "請先產生拼豆圖")
            return

        try:
            default_name = "beads_pattern_v2.png"
            if self.original_path:
                base = os.path.splitext(os.path.basename(self.original_path))[0]
                default_name = f"{base}_beads_pattern_v2.png"

            save_path = filedialog.asksaveasfilename(
                title="儲存拼豆圖",
                defaultextension=".png",
                initialfile=default_name,
                filetypes=[
                    ("PNG Image", "*.png"),
                    ("JPEG Image", "*.jpg"),
                    ("BMP Image", "*.bmp")
                ]
            )

            if not save_path:
                return

            self.pattern_preview.save(save_path)
            messagebox.showinfo("完成", f"拼豆圖已儲存：\n{save_path}")

        except Exception as e:
            messagebox.showerror("錯誤", f"儲存失敗：\n{e}")

    def export_color_csv(self):
        if not self.color_counter:
            messagebox.showwarning("提醒", "請先產生拼豆圖")
            return

        try:
            default_name = "beads_colors_v2.csv"
            if self.original_path:
                base = os.path.splitext(os.path.basename(self.original_path))[0]
                default_name = f"{base}_beads_colors_v2.csv"

            save_path = filedialog.asksaveasfilename(
                title="匯出顏色統計 CSV",
                defaultextension=".csv",
                initialfile=default_name,
                filetypes=[("CSV File", "*.csv")]
            )

            if not save_path:
                return

            used_items = []
            for item in BEADS_PALETTE:
                name = item["name"]
                if name in self.color_counter:
                    used_items.append({
                        "name": name,
                        "rgb": item["rgb"],
                        "count": self.color_counter[name]
                    })

            used_items.sort(key=lambda x: x["count"], reverse=True)

            with open(save_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["編號", "顏色名稱", "R", "G", "B", "數量"])

                for idx, item in enumerate(used_items, start=1):
                    writer.writerow([
                        idx,
                        item["name"],
                        item["rgb"][0],
                        item["rgb"][1],
                        item["rgb"][2],
                        item["count"]
                    ])

            messagebox.showinfo("完成", f"顏色統計已匯出：\n{save_path}")

        except Exception as e:
            messagebox.showerror("錯誤", f"匯出 CSV 失敗：\n{e}")

    def _show_fit_preview(self, pil_image, target_label, max_w=560, max_h=560):
        img = pil_image.copy()

        ratio = min(max_w / img.width, max_h / img.height, 1)
        new_w = max(1, int(img.width * ratio))
        new_h = max(1, int(img.height * ratio))
        img = img.resize((new_w, new_h), Image.Resampling.NEAREST)

        tk_img = ImageTk.PhotoImage(img)
        target_label.config(image=tk_img)
        target_label.image = tk_img


def main():
    root = tk.Tk()
    app = BeadsPatternToolV2(root)
    root.mainloop()


if __name__ == "__main__":
    main()