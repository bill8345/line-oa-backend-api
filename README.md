# 💰 WealthBlueprint — LINE OA 退休財務規劃機器人（後端）

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LINE_Messaging_API-00C300?style=for-the-badge&logo=line&logoColor=white" />
  <img src="https://img.shields.io/badge/Google_Sheets-34A853?style=for-the-badge&logo=googlesheets&logoColor=white" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white" />
</p>

## 📌 專案簡介

**WealthBlueprint** 是一款整合 LINE 官方帳號 (OA) 的退休財務規劃工具。  
使用者透過 LINE 聊天室即可完成資金缺口試算與理財人格測驗，後端自動將結果推播回 LINE 聊天室，並同步記錄至 Google Sheets，協助財務顧問追蹤客戶資訊。

### 🎯 核心功能

| 功能 | 說明 |
|------|------|
| 🧮 **退休金缺口試算** | 根據年齡、花費、存款等參數，計算退休金需求與資金缺口 |
| 📊 **動態折線圖生成** | 透過 QuickChart API 自動產生存款 vs 需求的視覺化折線圖 |
| 🧠 **理財人格測驗** | 依據資產配置偏好（股票/基金/保險/活存/定存）判斷投資風格 |
| 📲 **LINE Flex Message 推播** | 試算結果與人格圖卡直接推送回使用者的 LINE 聊天室 |
| 📋 **Google Sheets 自動記錄** | 使用者的輸入資料、試算結果、理財人格與資產分配比例，全部自動存入試算表 |
| 🖼️ **Rich Menu 圖文選單** | 4 格田字型選單：退休試算 / 財稅策略 / 資產傳承 / 預約會談 |

---

## 🏗️ 系統架構

```
┌─────────────────────────────────────────────────────┐
│                    LINE App (手機)                    │
│  ┌───────────┐  ┌───────────┐  ┌──────────────────┐ │
│  │ Rich Menu │→ │   LIFF    │→ │ Flex Message 回傳 │ │
│  └───────────┘  └─────┬─────┘  └──────────────────┘ │
└───────────────────────┼─────────────────────────────┘
                        │ HTTPS
           ┌────────────▼────────────┐
           │   FastAPI Backend       │
           │   (Render)              │
           │                         │
           │  /api/calculate         │──→ calculator.py
           │  /api/send_result       │──→ chart_util.py → QuickChart API
           │  /api/send_profile      │──→ LINE Messaging API
           │  /webhook               │──→ sheets_util.py → Google Sheets
           └─────────────────────────┘
```

---

## 📂 專案結構

```
backend/
├── main.py                  # FastAPI 主程式，定義所有 API 路由
├── calculator.py            # 退休金缺口計算引擎（通膨率、複利模擬）
├── chart_util.py            # QuickChart 折線圖生成（POST 短網址 API）
├── sheets_util.py           # Google Sheets 讀寫工具（gspread）
├── setup_rich_menu.py       # LINE Rich Menu 建立與上傳腳本
├── requirements.txt         # Python 套件依賴
├── .env                     # 環境變數（LINE Token、Google 金鑰路徑等）
└── google_credentials.json  # Google Service Account 金鑰（未上傳至 Git）
```

---

## 🔧 技術棧

| 層級 | 技術 | 用途 |
|------|------|------|
| **後端框架** | FastAPI | RESTful API、Webhook 接收、BackgroundTasks 非同步作業 |
| **LINE 整合** | LINE Messaging API v3 | Webhook、Push Message、Flex Message、Rich Menu |
| **前端** | LIFF (LINE Front-end Framework) | 嵌入於 LINE 內的互動表單 (另一個 Repo) |
| **圖表** | QuickChart API | 動態折線圖生成（POST 短網址避免 URL 過長問題） |
| **資料儲存** | Google Sheets API (gspread) | 自動記錄使用者試算資料與理財人格 |
| **部署** | Render | 自動從 GitHub 部署 |
| **驗證** | Google OAuth2 Service Account | Google Sheets API 憑證認證 |

---

## 🚀 快速開始

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

### 2. 設定環境變數

建立 `.env` 檔案，填入以下資訊：

```env
LINE_CHANNEL_ACCESS_TOKEN=你的_LINE_Channel_Access_Token
LINE_CHANNEL_SECRET=你的_LINE_Channel_Secret
LIFF_URL=https://liff.line.me/你的_LIFF_ID
GOOGLE_APPLICATION_CREDENTIALS=google_credentials.json
GOOGLE_SHEET_URL=https://docs.google.com/spreadsheets/d/你的試算表ID/edit
```

### 3. 啟動伺服器

```bash
uvicorn main:app --reload --port 8000
```

### 4. 設定 Rich Menu（選用）

```bash
python setup_rich_menu.py
```

---

## 📊 Google Sheets 自動記錄欄位

每位使用者完成試算後，後端會自動將資訊寫入同一列：

| 欄位 | 說明 | 寫入時機 |
|------|------|---------|
| 時間 | 試算時間戳記 | 第一階段 |
| LINE User ID | 使用者唯一識別碼 | 第一階段 |
| LINE 暱稱 | 使用者的 LINE 顯示名稱 | 第一階段 |
| 目前年齡 ~ 目前存款 | 使用者輸入的財務資料 | 第一階段 |
| 退休總需求 / 存款累積 / 缺口 | 計算結果 | 第一階段 |
| 理財人格 | 積極型 / 穩健型 / 保守型 | 第二階段（更新同列） |
| 股票% ~ 定存% | 資產配置偏好 | 第二階段（更新同列） |

---

## 🔑 API 端點

| Method | Endpoint | 說明 |
|--------|----------|------|
| `POST` | `/api/calculate` | 接收表單資料，回傳退休金試算結果 |
| `POST` | `/api/send_result` | 推送折線圖與 Flex Message 至 LINE |
| `POST` | `/api/send_profile` | 推送理財人格結果至 LINE，並更新 Google Sheets |
| `POST` | `/webhook` | 接收 LINE Webhook 事件 |
| `GET`  | `/health` | 健康檢查 |

---

## 📎 相關 Repo

| Repo | 說明 |
|------|------|
| **[line-oa-backend-api](https://github.com/bill8345/line-oa-backend-api)** | 後端 API（本 Repo） |
| **[line-oa-insurance-development](https://github.com/bill8345/line-oa-insurance-development)** | 前端 LIFF 頁面（GitHub Pages） |

---

## 📄 License

MIT License
