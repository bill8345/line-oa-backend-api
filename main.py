import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from calculator import calculate_retirement_plan
from chart_util import generate_quickchart_url

# === LINE Bot SDK 相關 ===
from linebot.v3 import WebhookParser
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    PushMessageRequest,
    FlexMessage,
    FlexContainer
)
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
import os

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', '')

# 如果有設定 LINE Credential，就初始化 API Client
line_config = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
line_parser = WebhookParser(LINE_CHANNEL_SECRET)

app = FastAPI(title="財富規劃 Line OA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CalculateRequest(BaseModel):
    current_age: int
    retire_age: int
    monthly_basic_expense: float
    monthly_fun_expense: float = 0.0
    monthly_saving: float
    current_saving: float
    # 新增可選的 LINE User ID，若前端在 LIFF 中有抓到，就可以傳過來
    # 這樣後端算完可以直接 push_message 給這個 User
    user_id: str = None

class ProfileRequest(BaseModel):
    user_id: str
    profile_type: str
    image_url: str

def create_flex_message(result: dict, chart_url: str) -> dict:
    """建立 LINE Flex Message JSON 結構"""
    def format_money(val):
        return f"NT$ {val:,}"
        
    gap = result["gap"]
    gap_color = "#10b981" if gap <= 0 else "#ef4444"
    gap_text = "恭喜！已達成目標" if gap <= 0 else format_money(gap)
    
    flex_json = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "退休金試算結果",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#d97706"
                }
            ],
            "backgroundColor": "#fdfbf7"
        },
        "hero": {
            "type": "image",
            "url": chart_url,
            "size": "full",
            "aspectRatio": "3:2",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "退休總需求 (含娛樂)", "color": "#8c7e6c", "size": "sm"},
                        {"type": "text", "text": format_money(result["total_need_with_fun"]), "align": "end", "weight": "bold", "color": "#4a4036"}
                    ]
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "退休總需求 (僅生活)", "color": "#8c7e6c", "size": "sm"},
                        {"type": "text", "text": format_money(result["total_need_basic"]), "align": "end", "weight": "bold", "color": "#4a4036"}
                    ],
                    "margin": "md"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "預估實際存款累積", "color": "#8c7e6c", "size": "sm"},
                        {"type": "text", "text": format_money(result["total_fund"]), "align": "end", "weight": "bold", "color": "#4a4036"}
                    ],
                    "margin": "md"
                },
                {"type": "separator", "margin": "lg", "color": "#d1c7bc"},
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {"type": "text", "text": "資金缺口 (以含娛樂為準)", "color": "#8c7e6c", "size": "md", "weight": "bold"},
                        {"type": "text", "text": gap_text, "align": "end", "weight": "bold", "color": gap_color}
                    ],
                    "margin": "lg"
                }
            ],
            "backgroundColor": "#ffffff"
        }
    }
    return flex_json

@app.post("/api/calculate")
def calculate_api(req: CalculateRequest):
    # 計算資金缺口
    result = calculate_retirement_plan(
        current_age=req.current_age,
        retire_age=req.retire_age,
        monthly_basic_expense=req.monthly_basic_expense,
        monthly_fun_expense=req.monthly_fun_expense,
        monthly_saving=req.monthly_saving,
        current_saving=req.current_saving
    )
    
    # 若前端有傳遞 LINE User ID 且後端有設定好 Token，進行推播
    if req.user_id and LINE_CHANNEL_ACCESS_TOKEN:
        # 1. 產生 QuickChart 圖片網址
        chart_url = generate_quickchart_url(result["history"])
        
        # 2. 生成 Flex Message 內容
        flex_dict = create_flex_message(result, chart_url)
        flex_obj = FlexContainer.from_dict(flex_dict)
        flex_message = FlexMessage(alt_text="您的財富規劃試算結果出爐了！", contents=flex_obj)
        
        # 3. 推送給該 User
        with ApiClient(line_config) as api_client:
            line_api = MessagingApi(api_client)
            push_req = PushMessageRequest(
                to=req.user_id,
                messages=[flex_message]
            )
            try:
                line_api.push_message(push_req)
            except Exception as e:
                print("LINE Push Error:", e)

    return result

@app.post("/api/send_profile")
def send_profile_api(req: ProfileRequest):
    """接收前端傳來的理財人格，並發送專屬圖片給使用者"""
    if not LINE_CHANNEL_ACCESS_TOKEN or not req.user_id:
        return {"status": "skipped", "reason": "No LINE Token or user_id provided"}
    
    # 根據 profile_type 決定邊框顏色
    profile_color = "#f59e0b" # 預設穩健橘黃
    if req.profile_type == "積極型":
        profile_color = "#ef4444"
    elif req.profile_type == "保守型":
        profile_color = "#10b981"

    flex_dict = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "您的專屬理財人格",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#d97706"
                }
            ],
            "backgroundColor": "#fdfbf7"
        },
        "hero": {
            "type": "image",
            "url": req.image_url,
            "size": "full",
            "aspectRatio": "1024:1536",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": req.profile_type,
                    "weight": "bold",
                    "size": "xxl",
                    "color": profile_color,
                    "align": "center"
                }
            ],
            "backgroundColor": "#ffffff"
        }
    }

    flex_obj = FlexContainer.from_dict(flex_dict)
    flex_message = FlexMessage(alt_text=f"專屬理財類型分析結果：{req.profile_type}", contents=flex_obj)
    
    with ApiClient(line_config) as api_client:
        line_api = MessagingApi(api_client)
        push_req = PushMessageRequest(
            to=req.user_id,
            messages=[flex_message]
        )
        try:
            line_api.push_message(push_req)
        except Exception as e:
            print("LINE Push Profile Error:", e)

    return {"status": "success"}

@app.post("/webhook")
async def line_webhook(request: Request):
    """
    LINE Message API Webhook 進入點
    """
    signature = request.headers.get("X-Line-Signature", "")
    body = await request.body()
    body_str = body.decode("utf-8")

    if not LINE_CHANNEL_SECRET:
        return "Not configured"

    try:
        events = line_parser.parse(body_str, signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            # 目前階段一/二都是被動表單，如果在官方帳號內傳純文字，可以導引他打開表單
            pass

    return "OK"

@app.get("/")
def read_root():
    return {"message": "LINE OA Backend API is running."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
