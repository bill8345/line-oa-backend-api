import os
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import pytz

# 設定時區為台北
tz = pytz.timezone('Asia/Taipei')

# 設定 Google API Scope
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def append_to_sheet(user_id: str, request_data: dict, result_data: dict):
    """
    將使用者的填答與計算結果寫入 Google Sheet。
    """
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    sheet_url = os.getenv("GOOGLE_SHEET_URL")
    
    if not cred_path or not sheet_url:
        print("警告: 尚未設定 GOOGLE_APPLICATION_CREDENTIALS 或 GOOGLE_SHEET_URL，跳過寫入。")
        return
        
    if not os.path.exists(cred_path):
        print(f"警告: 找不到 Google 金鑰檔案 {cred_path}，跳過寫入。")
        return

    try:
        # 初始化驗證
        credentials = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
        gc = gspread.authorize(credentials)
        
        # 開啟試算表與工作表
        sheet = gc.open_by_url(sheet_url).sheet1
        
        # 準備要寫入的資料
        current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
        
        # 提取欄位
        row_data = [
            current_time,                         # 紀錄時間
            user_id or "未提供",                   # LINE User ID
            request_data.get('current_age', ''),  # 目前年齡
            request_data.get('retire_age', ''),   # 預計退休年齡
            request_data.get('monthly_basic_expense', ''), # 基本生活費
            request_data.get('monthly_fun_expense', ''),   # 娛樂費用
            request_data.get('current_saving', ''),        # 目前存款
            result_data.get('total_need_basic', ''),       # 總需求 (基本)
            result_data.get('total_need_with_fun', ''),    # 總需求 (含娛樂)
            result_data.get('expected_saving_at_retire', ''), # 退休時累積存款
            result_data.get('gap', '')                     # 資金缺口 (以含娛樂為準)
        ]
        
        # 如果是第一列沒有標題，可以先塞標題 (這裡簡單直接 Append)
        # 如果 sheet 是空的，append_row 會從第一列開始寫
        if sheet.row_count == 0 or len(sheet.get_all_values()) == 0:
            headers = [
                "時間", "LINE User ID", "目前年齡", "退休年齡", "預計月基本花費", 
                "預計月娛樂花費", "目前存款", "退休總需求(基本)", "退休總需求(含娛樂)", 
                "退休時累積存款", "資金缺口"
            ]
            sheet.append_row(headers)
            
        sheet.append_row(row_data)
        print("成功將資料寫入 Google Sheet！")
        
    except Exception as e:
        print(f"寫入 Google Sheet 失敗: {e}")
