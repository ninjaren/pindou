import csv


def save_image_file(image, file_path):
    """
    儲存圖片檔案

    參數:
    - image: PIL.Image
    - file_path: 要儲存的完整路徑
    """
    if image is None:
        raise ValueError("image 不可為 None")

    image.save(file_path)


def export_color_statistics_csv(color_statistics, file_path):
    """
    匯出顏色統計 CSV

    color_statistics 格式範例:
    [
        {"name": "白色", "rgb": (255, 255, 255), "count": 300},
        {"name": "黑色", "rgb": (0, 0, 0), "count": 120},
    ]
    """
    if color_statistics is None:
        raise ValueError("color_statistics 不可為 None")

    with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["編號", "顏色名稱", "R", "G", "B", "數量"])

        for idx, item in enumerate(color_statistics, start=1):
            rgb = item["rgb"]
            writer.writerow([
                idx,
                item["name"],
                rgb[0],
                rgb[1],
                rgb[2],
                item["count"]
            ])