import os
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import Counter
from PIL import Image, ImageTk, ImageDraw


class BeadsPatternTool:
    def __init__(self, root):
        self.root = root
        self.root.title("拼豆圖產生器")
        self.root.geometry("1200x820")

        self.original_image = None
        self.pattern_image_small = None   # 真正的格子資料，例如 52x52
        self.pattern_image_preview = None # 放大後可視化圖
        self.original_path = None
        self.preview_tk = None

        # 預設參數
        self.grid_width_var = tk.IntVar(value=52)
        self.grid_height_var = tk.IntVar(value=52)
        self.cell_size_var = tk.IntVar(value=14)      # 預覽時每格顯示大小
        self.color_count_var = tk.IntVar(value=32)    # 顏色數量
        self.show_grid_var = tk.BooleanVar(value=True)
        self.keep_ratio_var = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self.root, padx=10, pady=10)
        top.pack(side=tk.TOP, fill=tk.X)

        tk.Button(top, text="開啟圖片", width=12, command=self.open_image).grid(row=0, column=0, padx=4, pady=4)
        tk.Button(top, text="產生拼豆圖", width=12, command=self.generate_pattern).grid(row=0, column=1, padx=4, pady=4)
        tk.Button(top, text="儲存拼豆圖", width=12, command=self.save_pattern_image).grid(row=0, column=2, padx=4, pady=4)
        tk.Button(top, text="匯出顏色統計 CSV", width=14, command=self.export_color_csv).grid(row=0, column=3, padx=4, pady=4)

        tk.Label(top, text="寬格數").grid(row=0, column=4, padx=4)
        tk.Spinbox(top, from_=8, to=300, width=6, textvariable=self.grid_width_var).grid(row=0, column=5, padx=4)

        tk.Label(top, text="高格數").grid(row=0, column=6, padx=4)
        tk.Spinbox(top, from_=8, to=300, width=6, textvariable=self.grid_height_var).grid(row=0, column=7, padx=4)

        tk.Label(top, text="每格大小").grid(row=0, column=8, padx=4)
        tk.Spinbox(top, from_=4, to=50, width=6, textvariable=self.cell_size_var).grid(row=0, column=9, padx=4)

        tk.Label(top, text="顏色數").grid(row=0, column=10, padx=4)
        tk.Spinbox(top, from_=2, to=128, width=6, textvariable=self.color_count_var).grid(row=0, column=11, padx=4)

        tk.Checkbutton(top, text="顯示格線", variable=self.show_grid_var).grid(row=0, column=12, padx=8)
        tk.Checkbutton(top, text="維持原圖比例", variable=self.keep_ratio_var).grid(row=0, column=13, padx=8)

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

        tk.Label(bottom, text="顏色統計").pack(anchor="w")
        self.color_text = tk.Text(bottom, height=12)
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
            self.pattern_image_small = None
            self.pattern_image_preview = None

            self._show_fit_preview(self.original_image, self.original_preview_label, max_w=520, max_h=520)
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
            cell_size = max(2, self.cell_size_var.get())
            color_count = max(2, min(128, self.color_count_var.get()))

            img = self.original_image.copy()

            # 維持比例時：先縮放進目標格數範圍，再補白底
            if self.keep_ratio_var.get():
                img.thumbnail((grid_w, grid_h), Image.Resampling.LANCZOS)

                canvas = Image.new("RGB", (grid_w, grid_h), (255, 255, 255))
                paste_x = (grid_w - img.width) // 2
                paste_y = (grid_h - img.height) // 2
                canvas.paste(img, (paste_x, paste_y))
                img = canvas
            else:
                img = img.resize((grid_w, grid_h), Image.Resampling.LANCZOS)

            # 降色
            img = img.quantize(colors=color_count, method=Image.Quantize.MEDIANCUT).convert("RGB")
            self.pattern_image_small = img

            # 產生放大預覽圖
            preview = self._build_preview_image(
                small_img=img,
                cell_size=cell_size,
                show_grid=self.show_grid_var.get()
            )
            self.pattern_image_preview = preview

            self._show_fit_preview(preview, self.pattern_preview_label, max_w=520, max_h=520)
            self._update_color_statistics()

            self.info_label.config(
                text=f"拼豆圖完成 | 格數：{grid_w} x {grid_h} | 顏色數上限：{color_count} | 預覽尺寸：{preview.width} x {preview.height}"
            )

        except Exception as e:
            messagebox.showerror("錯誤", f"產生拼豆圖失敗：\n{e}")

    def _build_preview_image(self, small_img, cell_size, show_grid):
        w, h = small_img.size
        out_w = w * cell_size
        out_h = h * cell_size

        preview = Image.new("RGB", (out_w, out_h), "white")
        draw = ImageDraw.Draw(preview)

        for y in range(h):
            for x in range(w):
                color = small_img.getpixel((x, y))
                x1 = x * cell_size
                y1 = y * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                draw.rectangle([x1, y1, x2, y2], fill=color)

        if show_grid and cell_size >= 4:
            grid_color = (180, 180, 180)
            for x in range(w + 1):
                xx = x * cell_size
                draw.line([(xx, 0), (xx, out_h)], fill=grid_color, width=1)
            for y in range(h + 1):
                yy = y * cell_size
                draw.line([(0, yy), (out_w, yy)], fill=grid_color, width=1)

        return preview

    def _update_color_statistics(self):
        self.color_text.delete("1.0", tk.END)

        if self.pattern_image_small is None:
            return

        pixels = list(self.pattern_image_small.getdata())
        counter = Counter(pixels)

        sorted_colors = sorted(counter.items(), key=lambda item: item[1], reverse=True)

        total = sum(counter.values())
        self.color_text.insert(tk.END, f"總拼豆數：{total}\n")
        self.color_text.insert(tk.END, f"顏色種類：{len(sorted_colors)}\n")
        self.color_text.insert(tk.END, "-" * 50 + "\n")

        for idx, (rgb, count) in enumerate(sorted_colors, start=1):
            self.color_text.insert(
                tk.END,
                f"{idx:02d}. RGB{rgb}  →  {count} 顆\n"
            )

    def save_pattern_image(self):
        if self.pattern_image_preview is None:
            messagebox.showwarning("提醒", "請先產生拼豆圖")
            return

        try:
            default_name = "beads_pattern.png"
            if self.original_path:
                base = os.path.splitext(os.path.basename(self.original_path))[0]
                default_name = f"{base}_beads_pattern.png"

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

            self.pattern_image_preview.save(save_path)
            messagebox.showinfo("完成", f"拼豆圖已儲存：\n{save_path}")

        except Exception as e:
            messagebox.showerror("錯誤", f"儲存失敗：\n{e}")

    def export_color_csv(self):
        if self.pattern_image_small is None:
            messagebox.showwarning("提醒", "請先產生拼豆圖")
            return

        try:
            pixels = list(self.pattern_image_small.getdata())
            counter = Counter(pixels)
            sorted_colors = sorted(counter.items(), key=lambda item: item[1], reverse=True)

            default_name = "beads_colors.csv"
            if self.original_path:
                base = os.path.splitext(os.path.basename(self.original_path))[0]
                default_name = f"{base}_beads_colors.csv"

            save_path = filedialog.asksaveasfilename(
                title="匯出顏色統計 CSV",
                defaultextension=".csv",
                initialfile=default_name,
                filetypes=[("CSV File", "*.csv")]
            )

            if not save_path:
                return

            with open(save_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["編號", "R", "G", "B", "數量"])

                for idx, (rgb, count) in enumerate(sorted_colors, start=1):
                    writer.writerow([idx, rgb[0], rgb[1], rgb[2], count])

            messagebox.showinfo("完成", f"顏色統計已匯出：\n{save_path}")

        except Exception as e:
            messagebox.showerror("錯誤", f"匯出 CSV 失敗：\n{e}")

    def _show_fit_preview(self, pil_image, target_label, max_w=520, max_h=520):
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
    app = BeadsPatternTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()