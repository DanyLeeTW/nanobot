---
name: project-inventory
description: 建立專案目錄表格 (Project Inventory Table Generator) - 掃描指定路徑下的專案，從 README.md 提取專案名稱、簡介和 URL，產生 Markdown 表格。
---

# 專案目錄表格生成器 (Project Inventory Table Generator)

掃描指定路徑下的專案，從 `README.md` 中提取專案名稱、簡介和 URL，並產生一個 Markdown 表格。

---

## 執行步驟

### 1. 掃描路徑

掃描以下路徑的所有專案目錄：
- `/Volumes/Work/Project` 底下的所有目錄
- `/Volumes/Work/Project/-*` 底下的所有一級子目錄

### 2. 排除規則

跳過以下類型的資料夾：
- 隱藏資料夾（以 `.` 開頭）
- 系統資料夾：`node_modules`, `.git`, `__pycache__`, `.venv`, `.pytest_cache`

### 3. 提取欄位

對每個專案目錄執行：

| 欄位 | 提取規則 |
|------|---------|
| **分類** | LLM 根據專案簡介語義分類（如 Agent, NLP, Web, Tool, Data, ML, API, CLI, Library, App, Other） |
| **專案名** | README 的第一個一級標題（`#`），若無則使用資料夾名稱 |
| **簡介** | 使用 LLM 總結 README.md 內容（限 50 字內），若無 README 則標記 `_無 README_` |
| **URL** | 提取 GitHub 連結（優先從 `.git/config` 或 README 中尋找），顯示為 `[GitHub](url)` |
| **Path** | 本地路徑，顯示為 `[📁](file://路徑)` 可點擊連結 |

### 4. 輸出格式

- **檔案名稱**：`/Users/danylee/Desktop/project-list.md`
- **格式**：Markdown 表格，按路徑排序

輸出表格範例：

```markdown
# 專案目錄

## Agent

| 專案名 | 簡介 | URL | Path |
|--------|------|-----|------|
| nanobot | AI agent framework | [GitHub](https://github.com/foo/nanobot) | [📁](file:///Volumes/Work/Project/---Agent/nanobot) |

## NER

| 專案名 | 簡介 | URL | Path |
|--------|------|-----|------|
| GPT-NER | Named Entity Recognition via LLM | [GitHub](https://github.com/foo/GPT-NER) | [📁](file:///Volumes/Work/Project/--NER/GPT-NER) |
```

> **分類規則**：LLM 根據專案簡介語義自動分類，常見分類包括 Agent, NLP, Web, Tool, Data, ML, API, CLI, Library, App, Other

---

## 執行腳本

完成掃描與提取後，執行以下命令生成表格：

```bash
python3 /tmp/gen_project_list.py
```

---

## 約束

- 掃描深度：`/Volumes/Work/Project` 為一級目錄，`/Volumes/Work/Project/-*` 為二級目錄（僅一級子目錄）
- 若 README.md 不存在，使用資料夾名稱作為專案名，簡介欄位標記為 `_無 README_`
- URL 提取順序：`.git/config` 的 remote origin URL → README 中的 GitHub 連結 → 無 URL 時留空
- 表格按分類分組，組內按專案名排序
- 簡介使用 LLM 總結 README 內容，限 50 字內，避免表格過寬
- 分類由 LLM 根據專案簡介語義判斷，分類名稱使用英文首字母大寫，不超過 15 字元
