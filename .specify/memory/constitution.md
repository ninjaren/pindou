<!--
Sync Impact Report:
Version: 1.0.0 (Initial Constitution)
Created: 2026-03-25
Modified Principles:
  - All principles created (initial version)
Added Sections:
  - 核心原則 (Core Principles) - 7 principles
  - 開發流程規範 (Development Workflow Standards)
  - 安全與合規要求 (Security and Compliance Requirements)
Templates Status:
  ✅ spec-template.md - Verified compatible (user stories align with testing principles)
  ✅ plan-template.md - Verified compatible (constitution check section present)
  ✅ tasks-template.md - Verified compatible (supports test-driven and security tasks)
Follow-up TODOs: None
-->

# Pindou 專案憲章
**Python 後端安全開發規範**

## 核心原則

### 一、代碼品質與整潔原則 (Code Quality & Clean Code)

**必須遵守的規則**：

- **明確性優於簡潔**：變數、函數、類別命名必須清晰表達意圖，避免縮寫和模糊名稱
- **單一職責**：每個函數、類別只負責一項明確定義的工作
- **純函數優先**：優先使用無副作用的純函數，狀態變更必須明確且可追蹤
- **型別註解強制**：所有公開函數必須包含完整的型別提示 (type hints)，使用 `mypy --strict` 驗證
- **文檔字符串**：所有公開 API 必須包含 docstring，說明用途、參數、返回值及可能的例外
- **代碼複雜度限制**：
  - 單一函數不超過 50 行
  - 圈複雜度 (cyclomatic complexity) ≤ 10
  - 嵌套深度 ≤ 4 層

**理由**：可維護性是長期開發的基石。清晰的代碼減少認知負擔，降低錯誤率，提升團隊協作效率。型別註解和文檔使 IDE 智能提示更準確，降低新成員學習曲線。

---

### 二、安全優先開發 (Security-First Development) **【不可妥協】**

**必須遵守的規則**（基於 OWASP Top 10）：

- **注入攻擊防護 (A03: Injection)**：
  - 禁止使用字串拼接構建 SQL 語句，必須使用參數化查詢或 ORM
  - 執行系統命令時必須使用 `shlex.quote()` 或 `subprocess` 的陣列參數模式
  - 所有使用者輸入必須經過驗證和清理，使用 Pydantic 或類似工具進行結構化驗證

- **存取控制 (A01: Broken Access Control)**：
  - 預設拒絕策略：只有明確授權的操作才能執行
  - 最小權限原則：每個角色只擁有完成其任務所需的最小權限
  - 防止路徑穿越：處理檔案路徑時必須標準化並驗證在允許範圍內

- **密碼學失敗 (A02: Cryptographic Failures)**：
  - 密碼存儲必須使用 `argon2` 或 `bcrypt` 加鹽雜湊
  - 禁止硬編碼密鑰、密碼或 API 金鑰，必須使用環境變數或密鑰管理服務
  - 傳輸必須使用 HTTPS/TLS 1.2+
  - 敏感資料持久化必須使用 AES-256 或更強加密

- **安全配置 (A05: Security Misconfiguration)**：
  - 生產環境禁止 DEBUG 模式和詳細錯誤訊息
  - 必須設定安全標頭：`Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`
  - 定期執行 `pip-audit` 或 `safety` 檢查依賴漏洞

- **身份認證失敗 (A07: Authentication Failures)**：
  - 會話 Cookie 必須設定 `HttpOnly`, `Secure`, `SameSite=Strict`
  - 登入失敗後實施速率限制和帳號鎖定機制
  - 登入成功後必須重新生成會話 ID

- **反序列化安全 (A08: Data Integrity Failures)**：
  - 禁止反序列化不受信任的 `pickle` 資料
  - 優先使用 JSON，若需複雜序列化則使用 `msgpack` 並驗證型別

**理由**：安全漏洞的修復成本隨時間指數增長。預防性安全設計比事後修補更經濟。OWASP Top 10 涵蓋 90% 以上的常見攻擊向量。

---

### 三、測試驅動開發 (Test-Driven Development) **【不可妥協】**

**必須遵守的規則**：

- **TDD 循環強制執行**：
  1. 撰寫測試（測試必須失敗）
  2. 使用者或技術負責人批准測試覆蓋範圍
  3. 實作最小代碼使測試通過
  4. 重構並保持測試通過
  
- **測試覆蓋率要求**：
  - 整體覆蓋率 ≥ 90%
  - 關鍵業務邏輯覆蓋率 = 100%
  - 使用 `pytest-cov` 生成報告，CI/CD 管道強制驗證

- **測試分層**：
  - **單元測試**：快速（< 100ms/test），隔離依賴（使用 mock），覆蓋所有函數路徑
  - **整合測試**：測試模組間交互、資料庫操作、外部服務調用（使用 testcontainers）
  - **端到端測試**：關鍵使用者旅程的完整流程測試

- **測試可讀性**：
  - 使用 **Given-When-Then** 或 **Arrange-Act-Assert** 結構
  - 測試名稱描述行為：`test_user_login_with_invalid_password_returns_401()`

**理由**：測試是需求的可執行文檔。TDD 強制思考介面設計和邊界條件，減少返工。高覆蓋率在重構時提供安全網，降低迴歸風險。

---

### 四、RESTful API 設計標準 (RESTful API Design) **【嚴格遵守】**

**必須遵守的規則**：

- **資源導向設計**：
  - URI 表示資源（名詞），使用複數形式：`/api/v1/users`, `/api/v1/orders`
  - 禁止在 URI 中使用動詞：❌ `/api/getUser` ✅ `GET /api/v1/users/{id}`

- **HTTP 方法語義**：
  - `GET`：查詢（冪等、安全、可快取）
  - `POST`：建立資源或非冪等操作
  - `PUT`：完整更新（冪等）
  - `PATCH`：部分更新（冪等）
  - `DELETE`：刪除資源（冪等）

- **狀態碼規範**：
  - **2xx 成功**：`200 OK`, `201 Created`, `204 No Content`
  - **4xx 客戶端錯誤**：`400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`
  - **5xx 伺服器錯誤**：`500 Internal Server Error`, `503 Service Unavailable`

- **版本控制**：
  - 使用 URI 路徑版本：`/api/v1/`, `/api/v2/`
  - 向後相容的變更不增加主版本（增加欄位、新端點）
  - 破壞性變更（刪除欄位、更改資料型別）必須升級主版本並維護舊版本至少 6 個月

- **分頁與過濾**：
  - 分頁：`?page=1&size=20` 或 `?offset=0&limit=20`
  - 排序：`?sort=created_at:desc`
  - 過濾：`?status=active&role=admin`

- **錯誤響應格式**：
  ```json
  {
    "error": {
      "code": "VALIDATION_ERROR",
      "message": "輸入資料驗證失敗",
      "details": [
        {"field": "email", "message": "格式不正確"}
      ]
    }
  }
  ```

- **HATEOAS 鼓勵但不強制**：對於複雜 API，在響應中包含相關資源的連結

**理由**：統一的 API 設計降低學習成本，提升開發者體驗。RESTful 原則經過大規模驗證，工具鏈成熟，有助於快取、負載平衡和監控。

---

### 五、最小依賴原則 (Minimal Dependency Principle)

**必須遵守的規則**：

- **依賴審查流程**：
  - 新增依賴前必須評估：
    1. 是否可用標準庫替代？
    2. 維護狀態（最後更新時間、issue 處理速度、star/fork 數）
    3. 安全記錄（CVE 歷史）
    4. 授權相容性（MIT/Apache/BSD 優先，避免 GPL）
    5. 依賴鏈深度（避免依賴樹過深）

- **核心依賴限制**：
  - 生產依賴應控制在 15 個以內（不含遞迴依賴）
  - 優先選擇成熟且單一職責的庫：FastAPI > Flask, Pydantic, SQLAlchemy, httpx

- **依賴鎖定**：
  - 使用 `poetry` 或 `pip-tools` 鎖定版本
  - `requirements.txt` 必須包含確切版本號（`==`），不允許範圍版本（`>=`）

- **定期更新與審計**：
  - 每季度審查依賴更新
  - 安全性更新必須在發佈後 7 天內應用

**理由**：依賴是攻擊面和技術債的來源。每個依賴引入維護成本、潛在漏洞和供應鏈風險。最小化依賴提升可控性，減少「左墊 (left-pad)」式災難。

---

### 六、性能要求 (Performance Requirements)

**必須遵守的規則**：

- **回應時間**：
  - API 端點 P95 延遲 < 200ms（簡單查詢）
  - API 端點 P95 延遲 < 500ms（複雜查詢或聚合）
  - 批量操作延遲與資料量線性成長，不可出現 O(n²) 操作

- **資源使用**：
  - 單個請求記憶體消耗 < 100MB
  - 背景任務必須使用非同步處理（Celery, rq）或訊息佇列（RabbitMQ, Redis）

- **資料庫查詢優化**：
  - N+1 查詢問題必須消除，使用 ORM 的 `select_related`, `prefetch_related` 或 JOIN
  - 所有外鍵必須建立索引
  - 查詢執行計畫 (EXPLAIN) 必須審查，避免全表掃描
  - 大數據集必須分頁，禁止返回超過 1000 筆無分頁資料

- **快取策略**：
  - 熱點資料使用 Redis 快取，TTL 根據變更頻率設定
  - HTTP 快取標頭必須正確設定 (`Cache-Control`, `ETag`)

- **性能測試**：
  - 使用 `locust` 或 `k6` 進行負載測試
  - 關鍵端點必須通過 1000 req/s 壓力測試（P95 < 500ms）

**理由**：性能是使用者體驗的核心。緩慢的 API 導致使用者流失和資源浪費。性能問題發現越晚，修復成本越高。明確標準促使設計階段考慮可擴展性。

---

### 七、使用者體驗一致性 (User Experience Consistency)

**必須遵守的規則**：

- **API 響應一致性**：
  - 成功響應統一結構：
    ```json
    {
      "data": {...},
      "meta": {"timestamp": "2026-03-25T10:30:00Z"}
    }
    ```
  - 分頁響應統一結構：
    ```json
    {
      "data": [...],
      "pagination": {
        "page": 1,
        "size": 20,
        "total": 150,
        "total_pages": 8
      }
    }
    ```

- **錯誤訊息國際化**：
  - 錯誤訊息必須清晰、可操作
  - 提供 `error.code` 供前端國際化
  - 包含 `error.details` 詳細說明驗證失敗的欄位

- **命名規範**：
  - JSON 欄位使用 `snake_case`（與 Python 慣例一致）
  - 日期時間統一使用 ISO 8601 格式（UTC），欄位名稱使用 `_at` 結尾：`created_at`, `updated_at`

- **行為一致性**：
  - 相同業務邏輯在不同端點必須保持一致（如權限檢查、資料驗證）
  - 軟刪除與硬刪除策略全專案統一

**理由**：一致性降低前端開發複雜度和錯誤率。預測性強的 API 提升開發者滿意度，減少技術支援負擔。

---

## 開發流程規範

### 代碼審查 (Code Review)

- **強制審查**：所有程式碼合併前必須通過至少一位資深開發者審查
- **檢查清單**：
  - [ ] 符合憲章所有核心原則
  - [ ] 測試覆蓋率達標且測試通過
  - [ ] 無安全漏洞（Bandit, Safety 掃描通過）
  - [ ] 型別檢查通過（mypy --strict）
  - [ ] 程式碼格式化（Black, isort）
  - [ ] 文檔字符串完整
  - [ ] 效能測試通過（如適用）

### 分支策略

- **主分支**：`main` - 隨時可部署到生產
- **功能分支**：`###-feature-name` - 從 `main` 分出，完成後合併回 `main`
- **熱修復分支**：`hotfix-###-description` - 緊急修復直接從 `main` 分出

### 提交訊息規範

遵循 Conventional Commits：

- `feat: 新增使用者登入 API`
- `fix: 修復密碼重設郵件未發送問題`
- `docs: 更新 API 文檔`
- `test: 增加訂單取消流程測試`
- `refactor: 重構使用者服務層`
- `perf: 優化查詢性能`
- `security: 修復 SQL 注入漏洞 (CVE-2026-XXXX)`

### 持續整合/持續部署 (CI/CD)

- **CI 管道必須檢查**：
  1. 單元測試和整合測試
  2. 覆蓋率報告（≥ 90%）
  3. 型別檢查（mypy）
  4. 安全掃描（Bandit, pip-audit）
  5. 程式碼風格（Flake8, Black）
  6. 依賴漏洞檢查

- **部署前置條件**：
  - CI 管道全部通過
  - 代碼審查批准
  - 功能測試在 staging 環境通過

---

## 安全與合規要求

### 日誌與監控

- **結構化日誌**：使用 `structlog`，JSON 格式
- **敏感資料脫敏**：日誌中禁止記錄密碼、金鑰、完整信用卡號
- **日誌等級**：
  - `DEBUG`：開發環境
  - `INFO`：應用關鍵事件（登入、訂單建立）
  - `WARNING`：可恢復錯誤（重試成功）
  - `ERROR`：需要介入的錯誤
  - `CRITICAL`：系統級故障

### 事件回應

- 安全事件（疑似攻擊、未授權存取）必須在 1 小時內通報
- 資料外洩事件必須立即啟動事件回應流程

### 合規性

- 如處理個人資訊，必須符合相關隱私法規（如 GDPR, CCPA）
- 實施資料最小化原則：只收集必要資料
- 提供使用者資料匯出和刪除機制

---

## 治理

### 憲章優先級

本憲章凌駕於所有其他開發實踐文件之上。任何衝突以本憲章為準。

### 修訂流程

1. 提出修訂提案（書面說明理由、影響範圍、遷移計畫）
2. 團隊審查與討論（至少 3 個工作日）
3. 投票表決（需 2/3 多數同意）
4. 更新憲章版本號（遵循語義化版本）
5. 更新所有相關模板和文檔
6. 公告並培訓團隊

### 版本控制規則

- **主版本 (MAJOR)**：移除或重新定義核心原則（破壞性變更）
- **次版本 (MINOR)**：新增原則或章節（功能性變更）
- **修訂版本 (PATCH)**：文字修正、澄清說明（非語義變更）

### 合規檢查

- 所有 Pull Request 必須驗證憲章合規性
- 每季度進行一次憲章合規審計
- 違反核心原則的程式碼必須拒絕合併或立即修復

### 例外處理

- 任何違反原則的例外必須文檔化並經過技術負責人批准
- 例外必須包含：理由、風險評估、補償措施、計畫移除時間

---

**版本**: 1.0.0 | **批准日期**: 2026-03-25 | **最後修訂**: 2026-03-25
