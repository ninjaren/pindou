# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

基於《Pindou 專案憲章》的強制檢查項目：

### 一、代碼品質與整潔原則
- [ ] 所有公開函數已規劃型別註解 (type hints)
- [ ] 函數職責單一且明確，無複雜度超標風險
- [ ] 命名規範清晰，避免模糊縮寫

### 二、安全優先開發 **【不可妥協】**
- [ ] 已識別所有使用者輸入點並規劃驗證機制（Pydantic）
- [ ] SQL 查詢使用參數化或 ORM，無字串拼接
- [ ] 敏感資料（密碼、金鑰）不硬編碼，使用環境變數
- [ ] 身份認證與授權機制符合最小權限原則
- [ ] 已規劃安全標頭、HTTPS、Session 安全配置

### 三、測試驅動開發 **【不可妥協】**
- [ ] 測試策略已定義（單元/整合/端到端）
- [ ] 覆蓋率目標 ≥ 90%，關鍵邏輯 100%
- [ ] TDD 流程已納入開發計畫

### 四、RESTful API 設計標準
- [ ] API 端點設計符合資源導向原則（名詞複數、無動詞）
- [ ] HTTP 方法語義正確使用
- [ ] 狀態碼規範已定義
- [ ] 版本控制策略已制定（URI 路徑版本）
- [ ] 錯誤響應格式統一

### 五、最小依賴原則
- [ ] 依賴清單已審查，無不必要依賴
- [ ] 核心依賴 ≤ 15 個
- [ ] 所有依賴已評估維護狀態、安全記錄、授權

### 六、性能要求
- [ ] API 回應時間目標已定義（P95 < 200ms 簡單查詢）
- [ ] 資料庫查詢已規劃索引和優化策略（無 N+1）
- [ ] 快取策略已制定（如適用）
- [ ] 關鍵端點已規劃負載測試（1000 req/s）

### 七、使用者體驗一致性
- [ ] API 響應結構統一（data/meta/pagination）
- [ ] 錯誤訊息格式一致且可操作
- [ ] 命名規範統一（snake_case, ISO 8601）

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
