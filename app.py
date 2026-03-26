import tkinter as tk
from tkinter import ttk


class BeadsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("拼豆像素圖工具")
        self.root.geometry("1000x700")

        self.create_ui()

    def create_ui(self):
        # 上方控制區
        top_frame = ttk.Frame(self.root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        ttk.Button(top_frame, text="載入圖片").pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="產生拼豆圖").pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="儲存拼豆圖").pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="匯出 CSV").pack(side=tk.LEFT, padx=5)

        ttk.Label(top_frame, text="拼豆尺寸:").pack(side=tk.LEFT, padx=10)

        self.size_var = tk.IntVar(value=52)
        ttk.Entry(top_frame, textvariable=self.size_var, width=5).pack(side=tk.LEFT)

        # 中間畫布
        self.canvas = tk.Canvas(self.root, bg="lightgray")
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 下方狀態列
        self.status_var = tk.StringVar()
        self.status_var.set("請先載入圖片")

        status_bar = ttk.Label(self.root, textvariable=self.status_var)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)


def main():
    root = tk.Tk()
    app = BeadsApp(root)
    root.mainloop()