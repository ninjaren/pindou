---
description: "拼豆圖案產生器 V2 任務清單"
feature: "001-beads-pattern-doc"
created: "2026-03-26"
---

# Tasks: 拼豆圖案產生器 V2

**輸入**: spec.md V2.0.0（7 個使用者故事，62 項功能需求）  
**組織方式**: 按使用者故事分組，每個故事可獨立實作和測試  
**技術架構**: Python 3.7+, Tkinter GUI, PIL/Pillow 圖片處理

## 格式：`- [ ] [ID] [P?] [Story?] 描述與檔案路徑`

- **[P]**: 可平行執行（不同檔案，無依賴）
- **[Story]**: 所屬使用者故事編號（如 US1、US2、US3）
- 所有描述包含明確的檔案路徑

---

## Phase 1: Setup（專案初始化）

**目的**: 專案結構與開發環境

- [ ] T001 驗證 Python 版本（需要 3.7+）並確認 Pillow、Tkinter 已安裝
- [ ] T002 建立專案目錄結構：根目錄包含功能模組、測試目錄（如需要）、文件目錄
- [ ] T003 [P] 設置 .gitignore 忽略 __pycache__/、*.pyc、.vscode/、測試圖片等臨時檔案
- [ ] T004 [P] 建立 README.md 包含專案簡介、安裝需求、執行方式

**檢查點**: 專案結構就緒，開發環境可用

---

## Phase 2: Foundational（核心基礎設施）

**目的**: 必須在任何使用者故事開始前完成的基礎功能

**⚠️ 關鍵**: 所有使用者故事依賴此階段完成

- [ ] T005 建立 palette_data.py 定義 24 色固定拼豆色盤（包含 name 和 rgb 欄位）
- [ ] T006 [P] 建立 beads_logic.py 實作核心演算法框架（檔案結構、匯入）
- [ ] T007 [P] 建立 preview_utils.py 實作預覽生成框架（檔案結構、匯入）
- [ ] T008 [P] 建立 export_utils.py 實作匯出工具框架（檔案結構、匯入）
- [ ] T009 建立 beads_gui_pretty.py 定義主視窗類別 BeadsGuiPretty 與基本 UI 結構（1280x860 視窗）
- [ ] T010 [P] 在 beads_gui_pretty.py 設定 ttk 樣式系統（clam 主題、卡片式設計、藍色主色調）
- [ ] T011 在 beads_gui_pretty.py 建立 UI 元件：header、toolbar、左側參數面板、右側雙預覽面板、底部顏色統計區
- [ ] T012 在 beads_gui_pretty.py 初始化狀態變數（grid_width、grid_height、cell_size、show_grid、show_number、keep_ratio）
- [ ] T013 建立 main.py 作為程式進入點（呼叫 BeadsGuiPretty 並啟動 mainloop）

**檢查點**: 基礎完成 - 可啟動程式看到 GUI 骨架（但功能尚未連接）

---

## Phase 3: User Story 5 - 固定拼豆色盤映射系統 (Priority: P1) 🎯 MVP 核心

**目標**: 實作 V2 核心功能 - 將圖片像素映射到 24 種真實存在的拼豆顏色

**獨立測試**: 手動建立測試圖片，呼叫 find_nearest_palette_color() 和 generate_beads_pattern()，驗證所有像素都映射到 palette_data.py 定義的 24 種顏色之一

### 實作 User Story 5

- [ ] T014 [P] [US5] 在 palette_data.py 定義完整的 BEADS_PALETTE（24 色：白、黑、灰階、紅、粉、橘、黃、綠、藍、紫、咖啡、膚色等）
- [ ] T015 [P] [US5] 在 beads_logic.py 實作 rgb_distance(c1, c2) 計算歐幾里得距離：sqrt((r1-r2)² + (g1-g2)² + (b1-b2)²)
- [ ] T016 [US5] 在 beads_logic.py 實作 find_nearest_palette_color(rgb, palette) 找出色盤中最近的顏色（回傳 dict 包含 name 和 rgb）
- [ ] T017 [US5] 在 beads_logic.py 實作 resize_image_for_beads(image, grid_width, grid_height, keep_ratio) 縮放圖片（支援比例維持、白色填充）
- [ ] T018 [US5] 在 beads_logic.py 實作 generate_beads_pattern() 主流程：縮放圖片 → 映射每個像素到色盤 → 產生 small_image、palette_map、color_counter
- [ ] T019 [US5] 在 beads_logic.py 實作 build_color_statistics(color_counter, palette) 整理統計資料為排序清單（按數量降序）
- [ ] T020 [US5] 驗證所有生成的顏色 100% 來自 BEADS_PALETTE（無任意 RGB 值）

**檢查點**: 色盤映射系統完整，可程式化生成拼豆圖案資料

---

## Phase 4: User Story 1 - 圖片轉拼豆圖案基礎轉換 (Priority: P1) 🎯 MVP

**目標**: 使用者可開啟圖片、設定參數、產生拼豆圖、看到預覽

**獨立測試**: 啟動程式 → 點擊「開啟圖片」選擇 PNG 檔案 → 設定格數 52x52 → 點擊「產生拼豆圖」→ 看到右側預覽圖顯示像素化拼豆圖案

### 實作 User Story 1

- [ ] T021 [US1] 在 beads_gui_pretty.py 實作 open_image() 方法：開啟檔案對話框（支援 PNG/JPG/BMP/WEBP）
- [ ] T022 [US1] 在 beads_gui_pretty.py 的 open_image() 中載入圖片為 PIL Image 並轉換為 RGB 模式
- [ ] T023 [US1] 在 beads_gui_pretty.py 的 open_image() 中將原圖顯示於左側 Canvas（self.original_canvas）
- [ ] T024 [US1] 在 beads_gui_pretty.py 的 open_image() 中更新狀態列顯示檔案名稱和原始尺寸
- [ ] T025 [US1] 在 beads_gui_pretty.py 實作 generate_pattern() 方法骨架：檢查是否已載入圖片
- [ ] T026 [US1] 在 generate_pattern() 中呼叫 beads_logic.generate_beads_pattern()（讀取 grid_width、grid_height、keep_ratio 參數）
- [ ] T027 [US1] 在 generate_pattern() 中儲存回傳的 small_image、palette_map、color_counter 到實例變數
- [ ] T028 [US1] 在 generate_pattern() 中呼叫 preview_utils.build_preview_image() 產生放大預覽圖（使用 cell_size、show_grid 參數）
- [ ] T029 [US1] 在 generate_pattern() 中將預覽圖顯示於右側 Canvas（self.pattern_canvas）
- [ ] T030 [US1] 在 generate_pattern() 中更新狀態列顯示拼豆圖格數和完成訊息
- [ ] T031 [US1] 處理錯誤情況：未載入圖片時顯示警告「請先開啟圖片」
- [ ] T032 [US1] 處理錯誤情況：圖片開啟失敗時顯示錯誤訊息並保持 UI 穩定

**檢查點**: User Story 1 完整可用，可獨立操作圖片轉換和預覽

---

## Phase 5: User Story 2 - 顏色統計與用料計算 (Priority: P2)

**目標**: 自動統計每種拼豆顏色的數量，並在底部區域顯示

**獨立測試**: 產生拼豆圖後，檢查底部文字區域顯示總拼豆數、顏色種類數、以及每種顏色的名稱與數量（由多到少排序）

### 實作 User Story 2

- [ ] T033 [US2] 在 generate_pattern() 中呼叫 beads_logic.build_color_statistics() 產生排序後的顏色清單
- [ ] T034 [US2] 在 generate_pattern() 中格式化顏色統計文字：總拼豆數、顏色種類數
- [ ] T035 [US2] 在 generate_pattern() 中格式化每種顏色：「編號. 顏色名稱 | RGB(...) | N 顆」
- [ ] T036 [US2] 在 generate_pattern() 中將統計文字顯示於 self.color_text (Text widget)
- [ ] T037 [US2] 確保重新產生拼豆圖時，舊統計資料被清除並更新為新資料
- [ ] T038 [US2] 驗證統計準確率 100%（顏色名稱計數與 palette_map 像素統計完全一致）

**檢查點**: User Story 1 和 2 同時可用，顏色統計獨立正確

---

## Phase 6: User Story 6 - 符號編號顯示系統 (Priority: P2) 🆕 V2

**目標**: 在拼豆圖每個格子中顯示數字編號，方便製作時對照

**獨立測試**: 產生拼豆圖後，勾選「顯示符號」並重新產生 → 預覽圖中每個格子顯示數字（格子大小 ≥ 12px 時）→ 數字與底部顏色統計清單編號一致

### 實作 User Story 6

- [ ] T039 [P] [US6] 在 preview_utils.py 實作 build_symbol_map(color_statistics) 產生「顏色名稱 → 編號字串」對映（按統計順序）
- [ ] T040 [P] [US6] 在 preview_utils.py 實作 get_text_color_by_background(rgb) 根據亮度選擇文字顏色（閾值 160）
- [ ] T041 [US6] 在 preview_utils.py 的 build_preview_image() 新增 show_symbol 參數
- [ ] T042 [US6] 在 build_preview_image() 中當 show_symbol=True 且 cell_size >= 12 時，繪製符號於每個格子中央
- [ ] T043 [US6] 在 build_preview_image() 中使用 get_text_color_by_background() 自動選擇符號文字顏色
- [ ] T044 [US6] 在 build_preview_image() 中確保符號置中對齊（使用 textbbox 計算文字寬高）
- [ ] T045 [US6] 在 beads_gui_pretty.py 的 generate_pattern() 中讀取 self.show_number 變數並傳入 build_preview_image()
- [ ] T046 [US6] 驗證符號編號與顏色統計清單 100% 一致

**檢查點**: 符號顯示系統完整，製作體驗大幅提升

---

## Phase 7: User Story 7 - 顏色名稱與採購指引 (Priority: P3) 🆕 V2

**目標**: 在顏色統計和 CSV 匯出中都包含中文顏色名稱

**獨立測試**: 產生拼豆圖後，檢查底部顏色統計顯示中文名稱（如「白色」「紅色」），格式清晰包含名稱、RGB、數量

### 實作 User Story 7

- [ ] T047 [US7] 在 generate_pattern() 中格式化顏色統計時，優先顯示顏色名稱（已在 T035 部分實作，此處驗證）
- [ ] T048 [US7] 在 generate_pattern() 的統計末尾新增提示訊息：「若有開啟『顯示符號』，上方清單順序就是符號編號。」
- [ ] T049 [US7] 在 generate_pattern() 的統計末尾新增符號對照範例：「例如：01 = [顏色名稱]，02 = [顏色名稱]...」
- [ ] T050 [US7] 驗證顏色名稱與 palette_data.py 定義 100% 一致

**檢查點**: 顏色名稱系統完整，降低非技術使用者門檻

---

## Phase 8: User Story 3 - 拼豆圖匯出與保存 (Priority: P3)

**目標**: 將生成的帶格線拼豆圖儲存為圖片檔案

**獨立測試**: 產生拼豆圖後 → 點擊「儲存拼豆圖」→ 選擇儲存路徑 → 系統儲存 PNG 檔案 → 用圖片檢視器開啟驗證正確

### 實作 User Story 3

- [ ] T051 [P] [US3] 在 export_utils.py 實作 save_image_file(image, file_path) 儲存 PIL Image 為檔案
- [ ] T052 [P] [US3] 在 save_image_file() 中處理錯誤：image 為 None、路徑無效、磁碟空間不足等
- [ ] T053 [US3] 在 beads_gui_pretty.py 實作 save_pattern() 方法：開啟儲存對話框（支援 PNG/JPG/BMP 格式）
- [ ] T054 [US3] 在 save_pattern() 中檢查是否已產生拼豆圖，未產生時顯示警告「請先產生拼豆圖」
- [ ] T055 [US3] 在 save_pattern() 中產生預設檔名：「原檔名_beads_pattern_v2.png」（無原檔名時用「beads_pattern_v2.png」）
- [ ] T056 [US3] 在 save_pattern() 中呼叫 export_utils.save_image_file() 儲存預覽圖
- [ ] T057 [US3] 在 save_pattern() 中處理儲存成功/失敗的提示訊息（使用 messagebox）
- [ ] T058 [US3] 處理邊緣情況：取消儲存對話框、唯讀目錄、檔名衝突等

**檢查點**: 圖片匯出功能完整，可列印參考

---

## Phase 9: User Story 4 - 顏色清單 CSV 匯出 (Priority: P4)

**目標**: 將顏色統計匯出為包含顏色名稱的 CSV 檔案

**獨立測試**: 產生拼豆圖後 → 點擊「匯出顏色統計 CSV」→ 選擇路徑 → 系統儲存 CSV → 用 Excel 開啟驗證包含 6 欄（編號、顏色名稱、R、G、B、數量）且中文正常顯示

### 實作 User Story 4

- [ ] T059 [P] [US4] 在 export_utils.py 實作 export_color_statistics_csv(color_statistics, file_path)
- [ ] T060 [P] [US4] 在 export_color_statistics_csv() 中寫入標題列：「編號,顏色名稱,R,G,B,數量」
- [ ] T061 [P] [US4] 在 export_color_statistics_csv() 中寫入每列資料：編號、名稱、RGB 三個分量、數量（共 6 欄）
- [ ] T062 [P] [US4] 在 export_color_statistics_csv() 中使用 UTF-8-BOM 編碼確保 Windows Excel 中文正常顯示
- [ ] T063 [US4] 在 beads_gui_pretty.py 實作 export_colors() 方法：開啟儲存對話框（.csv 格式）
- [ ] T064 [US4] 在 export_colors() 中檢查是否已產生拼豆圖，未產生時顯示警告「請先產生拼豆圖」
- [ ] T065 [US4] 在 export_colors() 中產生預設檔名：「原檔名_beads_colors_v2.csv」（無原檔名時用「beads_colors_v2.csv」）
- [ ] T066 [US4] 在 export_colors() 中呼叫 beads_logic.build_color_statistics() 和 export_utils.export_color_statistics_csv()
- [ ] T067 [US4] 在 export_colors() 中處理匯出成功/失敗的提示訊息
- [ ] T068 [US4] 驗證 CSV 格式：可被 Excel 和 Google Sheets 正確開啟、中文顯示正常、資料完整

**檢查點**: CSV 匯出功能完整，可作為採購清單

---

## Phase 10: Polish & Cross-Cutting Concerns（優化與收尾）

**目的**: 跨使用者故事的改進和品質保證

- [ ] T069 [P] 在 beads_gui_pretty.py 實作參數變動即時反映：監聽 IntVar/BooleanVar 變化並更新狀態標籤
- [ ] T070 [P] 在 beads_gui_pretty.py 新增鍵盤快捷鍵：Ctrl+O 開啟圖片、Ctrl+G 產生、Ctrl+S 儲存
- [ ] T071 在 beads_gui_pretty.py 優化 Canvas 顯示：超大預覽圖自動縮放至適應面板（最大 560x560px）
- [ ] T072 [P] 在 preview_utils.py 優化繪圖效能：使用 ImageDraw 批次繪製格線（避免逐線繪製）
- [ ] T073 [P] 在 beads_logic.py 新增效能優化：快取色彩距離計算結果（避免重複計算）
- [ ] T074 處理超大圖片情況：圖片 > 5000x5000px 時顯示警告並建議降低格數
- [ ] T075 處理極小格數情況：格數 < 8x8 時顯示警告「建議至少 8x8 以獲得可辨識圖案」
- [ ] T076 [P] 新增錯誤日誌：將 Exception 寫入 error.log 方便除錯（production 模式）
- [ ] T077 [P] 更新 README.md：新增使用者手冊、常見問題、V2 新功能說明
- [ ] T078 [P] 建立 requirements.txt：列出 Pillow 版本需求（如 Pillow>=8.0.0）
- [ ] T079 建立範例圖片集：提供 3-5 張測試圖片（卡通角色、像素藝術、Logo）於 examples/ 目錄
- [ ] T080 完整功能測試：執行所有使用者故事的獨立測試和整合測試
- [ ] T081 效能驗證：確認 52x52 格圖案產生時間 < 5 秒（一般解析度圖片）
- [ ] T082 相容性測試：在 Windows 10/11 上測試（Python 3.7、3.8、3.10 版本）

**檢查點**: 產品品質達到發布標準

---

## 依賴關係與執行順序

### 階段依賴

- **Setup (Phase 1)**: 無依賴 - 可立即開始
- **Foundational (Phase 2)**: 依賴 Setup 完成 - **阻塞所有使用者故事**
- **User Stories (Phase 3-9)**: 所有故事依賴 Foundational 完成
  - 完成 Foundational 後，故事可平行執行（如有人力）
  - 或按優先順序序列執行（P1 → P2 → P3 → P4）
- **Polish (Phase 10)**: 依賴所有期望的使用者故事完成

### 使用者故事依賴

- **User Story 5 (P1)**: Foundational 後可開始 - 無其他故事依賴，但建議優先（色盤系統是 V2 核心）
- **User Story 1 (P1)**: 依賴 US5 完成（需要色盤映射功能）- **MVP 必須**
- **User Story 2 (P2)**: 依賴 US1 和 US5（需要 generate_beads_pattern 產生的資料）- 可獨立測試
- **User Story 6 (P2)**: 依賴 US2（需要顏色統計清單產生符號映射）- 可獨立測試
- **User Story 7 (P3)**: 依賴 US2（在統計顯示中整合顏色名稱）- 可獨立測試
- **User Story 3 (P3)**: 依賴 US1（需要預覽圖）- 可獨立測試
- **User Story 4 (P4)**: 依賴 US2 和 US7（CSV 需要完整的顏色統計含名稱）- 可獨立測試

### 故事內依賴

- 模組框架先於功能實作
- 核心演算法先於 UI 整合
- 錯誤處理在功能實作後補充
- 故事完成後再進入下一優先級

### 平行機會

- Phase 1 所有標記 [P] 的任務可平行
- Phase 2 所有標記 [P] 的任務可平行（T005-T008, T010）
- US5 的 T014、T015 可平行（palette_data 和 rgb_distance 獨立）
- US6 的 T039、T040 可平行（build_symbol_map 和 get_text_color 獨立）
- US3、US4 的 export_utils 功能可平行（不同函式）
- Phase 10 所有標記 [P] 的任務可平行

---

## 平行執行範例：User Story 5

```bash
# 平行建立獨立模組：
Task: "在 palette_data.py 定義完整的 BEADS_PALETTE（24 色）"
Task: "在 beads_logic.py 實作 rgb_distance(c1, c2) 計算歐幾里得距離"

# 序列執行依賴任務：
1. 完成上述兩個平行任務
2. Task: "在 beads_logic.py 實作 find_nearest_palette_color() 使用 rgb_distance"
3. Task: "在 beads_logic.py 實作 generate_beads_pattern() 使用 find_nearest_palette_color"
```

---

## 實作策略

### MVP First（僅 User Story 5 + 1）

1. 完成 Phase 1: Setup
2. 完成 Phase 2: Foundational（**關鍵 - 阻塞所有故事**）
3. 完成 Phase 3: User Story 5（色盤系統）
4. 完成 Phase 4: User Story 1（基礎轉換）
5. **停止並驗證**: 獨立測試圖片轉換功能
6. 準備就緒即可展示/部署

### 漸進式交付

1. 完成 Setup + Foundational → 基礎就緒
2. 新增 User Story 5 + 1 → 獨立測試 → 部署/展示（**MVP！**）
3. 新增 User Story 2 → 獨立測試 → 部署/展示（新增統計功能）
4. 新增 User Story 6 → 獨立測試 → 部署/展示（新增符號功能）
5. 新增 User Story 7 → 獨立測試 → 部署/展示（完善顏色名稱）
6. 新增 User Story 3 → 獨立測試 → 部署/展示（新增圖片匯出）
7. 新增 User Story 4 → 獨立測試 → 部署/展示（新增 CSV 匯出）
8. 每個故事都增加價值且不破壞已有功能

### 團隊平行策略

若有多位開發者：

1. 團隊一起完成 Setup + Foundational
2. Foundational 完成後：
   - 開發者 A: User Story 5（色盤系統）
   - 開發者 B: User Story 1（UI 整合，等待 US5）
   - 開發者 C: preview_utils 和 export_utils 框架
3. US5 完成後啟動整合測試
4. 後續故事可繼續平行（US2+US3、US6、US4、US7）

---

## 建議的 MVP 範圍

**最小可行產品（20 個任務，約 2-3 天）**：

```
Phase 1: Setup (T001-T004)                     → 4 tasks
Phase 2: Foundational (T005-T013)              → 9 tasks
Phase 3: User Story 5 (T014-T020)              → 7 tasks
Phase 4: User Story 1 (T021-T032)              → 12 tasks
---------------------------------------------------
Total: 32 tasks

功能：可開啟圖片、產生固定色盤拼豆圖、預覽顯示
```

**完整 V2 功能（所有 82 個任務，約 7-10 天）**：

包含所有 7 個使用者故事、完整錯誤處理、效能優化、文件更新

---

## 注意事項

- [P] 任務 = 不同檔案、無依賴，可平行執行
- [Story] 標籤將任務對映到特定使用者故事以便追蹤
- 每個使用者故事應可獨立完成和測試
- 在檢查點處停止並驗證故事獨立運作
- 避免：模糊任務、同檔案衝突、破壞故事獨立性的跨故事依賴
- 每完成邏輯任務組即提交 Git commit
- 使用 Git 分支管理：feature/us1-basic-conversion、feature/us5-palette-system 等

---

**總任務數**: 82  
**MVP 任務數**: 32  
**預估完整實作時間**: 7-10 個工作天（單人）  
**預估 MVP 時間**: 2-3 個工作天（單人）

---

**版本**: 1.0.0  
**生成日期**: 2026-03-26  
**基於**: spec.md V2.0.0（62 項功能需求，7 個使用者故事，15 項成功標準）
