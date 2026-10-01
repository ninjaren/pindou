from collections import Counter, deque
from PIL import Image, ImageFilter

from palette_data import BEADS_PALETTE


def rgb_distance(c1, c2):
    """
    Redmean 加權 RGB 距離——比普通歐式距離更符合人眼視覺感知。
    公式：sqrt((2 + r̄/256)*ΔR² + 4*ΔG² + (2 + (255-r̄)/256)*ΔB²)
    """
    r_mean = (c1[0] + c2[0]) / 2
    dr = c1[0] - c2[0]
    dg = c1[1] - c2[1]
    db = c1[2] - c2[2]
    return (
        (2 + r_mean / 256) * dr * dr
        + 4.0 * dg * dg
        + (2 + (255 - r_mean) / 256) * db * db
    ) ** 0.5


def find_nearest_palette_color(rgb, palette=None):
    """
    找出色盤中距離最近的拼豆顏色。
    回傳格式: {"name": "粉紅", "rgb": (255, 182, 193)}
    """
    if palette is None:
        palette = BEADS_PALETTE

    best_item = None
    best_distance = float("inf")

    for item in palette:
        dist = rgb_distance(rgb, item["rgb"])
        if dist < best_distance:
            best_distance = dist
            best_item = item

    return best_item


def replace_background_with_white(image, bg_type="black", tolerance=40):
    """
    從四個角落偵測背景色，用 BFS 氾水填充將背景換成白色。

    參數:
    - bg_type : 'black'（黑底）或 'white'（白底）
    - tolerance: 顏色判斷容差（各通道最大差值，0-255）
    """
    w, h = image.size
    src = image.load()

    corners = [
        src[0, 0][:3],
        src[w - 1, 0][:3],
        src[0, h - 1][:3],
        src[w - 1, h - 1][:3],
    ]

    if bg_type == "black":
        bg_ref = min(corners, key=lambda c: c[0] + c[1] + c[2])
    else:
        bg_ref = max(corners, key=lambda c: c[0] + c[1] + c[2])

    def is_similar(c):
        return max(abs(int(c[i]) - int(bg_ref[i])) for i in range(3)) <= tolerance

    visited = [[False] * w for _ in range(h)]
    queue = deque()

    for sx, sy in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if is_similar(src[sx, sy][:3]):
            queue.append((sx, sy))
            visited[sy][sx] = True

    result = image.copy()
    dst = result.load()

    while queue:
        x, y = queue.popleft()
        dst[x, y] = (255, 255, 255)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and not visited[ny][nx]:
                if is_similar(src[nx, ny][:3]):
                    visited[ny][nx] = True
                    queue.append((nx, ny))

    return result


def quantize_image(image, num_colors=12):
    """
    先對圖片做 Median Cut 減色，穩定色塊後再映射拼豆色盤。
    有效防止原圖細碎顏色導致映射亂跳。
    """
    q = image.quantize(colors=num_colors)
    return q.convert("RGB")


def smooth_color_blocks(image):
    """
    量化後多跑一道 Median Filter，將細碎的色塊邊緣整合。
    有效修復鋸齒所產生的中間色。
    """
    return image.filter(ImageFilter.MedianFilter(size=3))


def remove_noise_from_palette_map(palette_map, grid_width, grid_height, palette, strength=2):
    """
    後處理：將孤立的鑑點格子替換成周圍多數色。

    原理：對每個格子檢查 8 鄰居的同色數量，
    如果 < strength，則視為雜點，替換成鄰居中最多數色。

    參數:
    - strength: 導果同色鄰居數小於此値則替換（預設 2）
    """
    name_to_item = {item["name"]: item for item in palette}
    new_map = [row[:] for row in palette_map]

    for y in range(grid_height):
        for x in range(grid_width):
            current_name = palette_map[y][x]["name"]

            neighbor_names = []
            for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1),
                           (-1, -1), (1, -1), (-1, 1), (1, 1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_width and 0 <= ny < grid_height:
                    neighbor_names.append(palette_map[ny][nx]["name"])

            if neighbor_names and neighbor_names.count(current_name) < strength:
                most_common_name = Counter(neighbor_names).most_common(1)[0][0]
                if most_common_name in name_to_item:
                    new_map[y][x] = name_to_item[most_common_name]

    return new_map


def resize_image_for_beads(image, grid_width, grid_height, keep_ratio=True):
    """
    把圖片縮成拼豆格數大小
    keep_ratio=True 時維持比例並以白色填充空白區域
    """
    img = image.copy().convert("RGB")

    if keep_ratio:
        img.thumbnail((grid_width, grid_height), Image.Resampling.LANCZOS)

        canvas = Image.new("RGB", (grid_width, grid_height), (255, 255, 255))
        paste_x = (grid_width - img.width) // 2
        paste_y = (grid_height - img.height) // 2
        canvas.paste(img, (paste_x, paste_y))
        return canvas

    return img.resize((grid_width, grid_height), Image.Resampling.LANCZOS)


def generate_beads_pattern(
    image,
    grid_width,
    grid_height,
    keep_ratio=True,
    palette=None,
    pre_quantize_colors=12,
    ignore_bg=None,
    bg_tolerance=40,
    noise_removal=True,
    noise_strength=2,
):
    """
    產生拼豆圖主流程（改良版）

    處理管線：
      1. 縮圖到格數大小
      2. 去除背景，換成白色（可選）
      3. 預先量化減色，穩定色塊（可選）
      4. Median Filter 平滑色塊邊緣，修復鋸齒中間色
      5. 映射每格到拼豆色盤
      6. 雜點消除：孤立格子替換成周圍多數色（可選）

    參數:
    - pre_quantize_colors: 量化色數（0 = 停用）
    - ignore_bg: None / 'black' / 'white'
    - bg_tolerance: 背景偵測容差
    - noise_removal: 是否啟用雜點消除
    - noise_strength: 同色鄰居數低於此值才會被視為雜點
    """
    if palette is None:
        palette = BEADS_PALETTE

    # Step 1: 縮圖
    resized = resize_image_for_beads(
        image=image,
        grid_width=grid_width,
        grid_height=grid_height,
        keep_ratio=keep_ratio,
    )

    # Step 2: 去除背景（換成白色）
    if ignore_bg in ("black", "white"):
        resized = replace_background_with_white(
            resized, bg_type=ignore_bg, tolerance=bg_tolerance
        )

    # Step 3: 預先量化，穩定色塊
    if pre_quantize_colors and pre_quantize_colors >= 2:
        resized = quantize_image(resized, num_colors=pre_quantize_colors)

    # Step 4: Median Filter 平滑色塊邊緣
    resized = smooth_color_blocks(resized)

    # Step 5: 映射到拼豆色盤
    mapped_image = Image.new("RGB", (grid_width, grid_height))
    palette_map = []
    color_counter = Counter()

    for y in range(grid_height):
        row = []
        for x in range(grid_width):
            rgb = resized.getpixel((x, y))
            nearest = find_nearest_palette_color(rgb, palette)
            mapped_image.putpixel((x, y), nearest["rgb"])
            row.append(nearest)
            color_counter[nearest["name"]] += 1
        palette_map.append(row)

    # Step 6: 雜點消除
    if noise_removal:
        palette_map = remove_noise_from_palette_map(
            palette_map, grid_width, grid_height, palette, strength=noise_strength
        )
        color_counter = Counter()
        for y in range(grid_height):
            for x in range(grid_width):
                item = palette_map[y][x]
                mapped_image.putpixel((x, y), item["rgb"])
                color_counter[item["name"]] += 1

    return {
        "small_image": mapped_image,
        "palette_map": palette_map,
        "color_counter": color_counter,
        "grid_width": grid_width,
        "grid_height": grid_height,
    }


def build_color_statistics(color_counter, palette=None):
    """
    把 Counter 整理成顯示/匯出格式，按數量降序排列。
    """
    if palette is None:
        palette = BEADS_PALETTE

    results = []

    for item in palette:
        name = item["name"]
        if name in color_counter:
            results.append({
                "name": name,
                "rgb": item["rgb"],
                "count": color_counter[name],
            })

    results.sort(key=lambda x: x["count"], reverse=True)
    return results


def merge_similar_colors(palette_map, color_statistics, threshold_pct, palette=None):
    """
    將相似色距離在閾值內的顏色合併成使用量較大的那個，減少實際用色種類。

    參數:
    - threshold_pct: 0-100，越大合併越濃。0 = 停用
    - 回傳: (new_palette_map, new_color_statistics)
    """
    if palette is None:
        palette = BEADS_PALETTE
    if threshold_pct <= 0 or not color_statistics:
        return palette_map, color_statistics

    # Redmean 最大距離（白 → 黑）約 765，將 0-100 映射到有意義的距離區間
    max_dist = 765.0
    threshold_dist = threshold_pct / 100.0 * max_dist

    name_to_item = {item["name"]: item for item in palette}

    # 按使用量由大到小排序，大色優先保留
    stats_sorted = sorted(color_statistics, key=lambda x: x["count"], reverse=True)

    # 建立「小色 → 合併目標色」對映表
    merge_map = {}  # small_name -> big_name
    for i, big in enumerate(stats_sorted):
        for small in stats_sorted[i + 1:]:
            small_name = small["name"]
            if small_name in merge_map:
                continue
            if rgb_distance(big["rgb"], small["rgb"]) <= threshold_dist:
                merge_map[small_name] = big["name"]

    if not merge_map:
        return palette_map, color_statistics

    # 套用合併到 palette_map
    new_counter = Counter()
    new_map = []
    for row in palette_map:
        new_row = []
        for item in row:
            target_name = merge_map.get(item["name"], item["name"])
            new_row.append(name_to_item.get(target_name, item))
            new_counter[target_name] += 1
        new_map.append(new_row)

    # 重建 color_statistics
    new_stats = []
    for item in palette:
        if item["name"] in new_counter:
            new_stats.append({
                "name": item["name"],
                "rgb": item["rgb"],
                "count": new_counter[item["name"]],
            })
    new_stats.sort(key=lambda x: x["count"], reverse=True)

    return new_map, new_stats
