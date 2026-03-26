from PIL import Image, ImageDraw, ImageFont, ImageTk


def build_symbol_map(color_statistics):
    """
    根據顏色統計建立符號表
    例如：
    白色 -> "1"
    黑色 -> "2"
    粉紅 -> "3"
    """
    symbol_map = {}

    for idx, item in enumerate(color_statistics, start=1):
        symbol_map[item["name"]] = str(idx)

    return symbol_map


def get_text_color_by_background(rgb):
    """
    根據背景顏色亮度，決定文字要用黑色還是白色
    避免文字看不清楚
    """
    brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
    return (0, 0, 0) if brightness > 160 else (255, 255, 255)


def build_preview_image(small_image, palette_map, color_statistics, cell_size=14, show_grid=True, show_symbol=False):
    """
    建立放大後的拼豆圖預覽

    參數:
    - small_image: 小尺寸拼豆圖，例如 52x52
    - palette_map: 二維顏色資訊陣列
    - color_statistics: 顏色統計資料
    - cell_size: 每格放大多大
    - show_grid: 是否顯示格線
    - show_symbol: 是否顯示顏色編號

    回傳:
    - PIL.Image
    """
    w, h = small_image.size
    out_w = w * cell_size
    out_h = h * cell_size

    preview = Image.new("RGB", (out_w, out_h), "white")
    draw = ImageDraw.Draw(preview)

    try:
        font = ImageFont.load_default()
    except Exception:
        font = None

    symbol_map = build_symbol_map(color_statistics)

    for y in range(h):
        for x in range(w):
            item = palette_map[y][x]
            color = item["rgb"]
            name = item["name"]

            x1 = x * cell_size
            y1 = y * cell_size
            x2 = x1 + cell_size
            y2 = y1 + cell_size

            draw.rectangle([x1, y1, x2, y2], fill=color)

            if show_symbol and cell_size >= 12:
                symbol = symbol_map.get(name, "")
                text_color = get_text_color_by_background(color)

                if font is not None:
                    bbox = draw.textbbox((0, 0), symbol, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]
                else:
                    text_w = 6
                    text_h = 10

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


def resize_image_for_canvas(pil_image, canvas_width, canvas_height, keep_pixel_style=True):
    """
    根據 canvas 尺寸縮放圖片，回傳新的 PIL.Image
    keep_pixel_style=True 時會使用 NEAREST，保留拼豆方塊感
    """
    max_w = max(50, canvas_width - 20)
    max_h = max(50, canvas_height - 20)

    img = pil_image.copy()

    ratio = min(max_w / img.width, max_h / img.height, 1)
    new_w = max(1, int(img.width * ratio))
    new_h = max(1, int(img.height * ratio))

    if keep_pixel_style:
        resample_method = Image.Resampling.NEAREST
    else:
        resample_method = Image.Resampling.LANCZOS

    return img.resize((new_w, new_h), resample_method)


def pil_image_to_tk(pil_image):
    """
    把 PIL.Image 轉成 tkinter 可顯示的 ImageTk.PhotoImage
    """
    return ImageTk.PhotoImage(pil_image)