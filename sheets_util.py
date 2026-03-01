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

HEADERS = [
    "時間", "LINE User ID", "LINE 暱稱", "目前年齡", "退休年齡",
    "預計月基本花費", "預計月娛樂花費", "目前存款",
    "退休總需求(基本)", "退休總需求(含娛樂)", "預估實際存款累積", "資金缺口",
    "理財人格", "股票%", "基金%", "保險%", "活存%", "定存%"
]

def _get_sheet():
    """取得 Google Sheet 工作表物件"""
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    sheet_url = os.getenv("GOOGLE_SHEET_URL")

    if not cred_path or not sheet_url:
        print("警告: 尚未設定 GOOGLE_APPLICATION_CREDENTIALS 或 GOOGLE_SHEET_URL，跳過寫入。")
        return None

    if not os.path.exists(cred_path):
        print(f"警告: 找不到 Google 金鑰檔案 {cred_path}，跳過寫入。")
        return None

    credentials = Credentials.from_service_account_file(cred_path, scopes=SCOPES)
    gc = gspread.authorize(credentials)
    sheet = gc.open_by_url(sheet_url).sheet1

    # 確保標題列存在
    first_row = sheet.row_values(1)
    if not first_row or first_row[0] != "時間":
        sheet.insert_row(HEADERS, 1)

    return sheet


def append_to_sheet(user_id: str, user_name: str, request_data: dict, result_data: dict):
    """
    第一階段：將使用者的填答與計算結果寫入 Google Sheet（新增一行）。
    """
    try:
        sheet = _get_sheet()
        if not sheet:
            return

        current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

        row_data = [
            current_time,                                      # 時間
            user_id or "未提供ID",                             # LINE User ID
            user_name or "未提供暱稱",                         # LINE 暱稱
            request_data.get('current_age', ''),               # 目前年齡
            request_data.get('retire_age', ''),                # 退休年齡
            request_data.get('monthly_basic_expense', ''),     # 預計月基本花費
            request_data.get('monthly_fun_expense', ''),       # 預計月娛樂花費
            request_data.get('current_saving', ''),            # 目前存款
            result_data.get('total_need_basic', ''),           # 退休總需求(基本)
            result_data.get('total_need_with_fun', ''),        # 退休總需求(含娛樂)
            result_data.get('total_fund', ''),                 # 預估實際存款累積
            result_data.get('gap', ''),                        # 資金缺口
            '',                                                # 理財人格 (第二階段填入)
            '',                                                # 股票%
            '',                                                # 基金%
            '',                                                # 保險%
            '',                                                # 活存%
            '',                                                # 定存%
        ]

        sheet.append_row(row_data)
        print("第一階段：成功將試算資料寫入 Google Sheet！")

    except Exception as e:
        print(f"第一階段寫入 Google Sheet 失敗: {e}")


def update_profile_in_sheet(user_id: str, profile_type: str, allocations: dict):
    """
    第二階段：找到該 user_id 最近一筆紀錄，在同一行更新理財人格與資金分配比例。
    """
    try:
        sheet = _get_sheet()
        if not sheet:
            return

        # 找到 LINE User ID 欄 (B 欄) 中符合的最後一列
        all_values = sheet.get_all_values()
        target_row = None
        for i in range(len(all_values) - 1, 0, -1):  # 從最後一列往回找，跳過標題列
            if all_values[i][1] == user_id:  # B 欄 = LINE User ID
                target_row = i + 1  # gspread 是 1-indexed
                break

        if not target_row:
            print(f"找不到 user_id={user_id} 的紀錄，無法更新理財人格。")
            return

        # 更新 M 欄 (理財人格, col 13) 到 R 欄 (定存%, col 18)
        profile_data = [
            profile_type,
            allocations.get('stock', ''),
            allocations.get('fund', ''),
            allocations.get('insurance', ''),
            allocations.get('demand', ''),
            allocations.get('time', ''),
        ]

        # 批次更新 M~R 欄 (col 13~18)
        cell_range = f"M{target_row}:R{target_row}"
        sheet.update(cell_range, [profile_data])

        print(f"第二階段：成功更新第 {target_row} 列的理財人格與資金分配！")

    except Exception as e:
        print(f"第二階段更新 Google Sheet 失敗: {e}")
