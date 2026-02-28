import os
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    MessagingApiBlob,
    RichMenuRequest,
    RichMenuArea,
    RichMenuBounds,
    RichMenuSize,
    URIAction,
    MessageAction
)
from dotenv import load_dotenv

load_dotenv()

LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
LIFF_URL = os.getenv('LIFF_URL', '')

if not LINE_CHANNEL_ACCESS_TOKEN:
    print("錯誤：請設定 LINE_CHANNEL_ACCESS_TOKEN 到 .env 檔案中")
    exit(1)

if not LIFF_URL:
    print("錯誤：請設定 LIFF_URL 到 .env 檔案中 (例如: https://liff.line.me/xxxxxx-xxxxxx)")
    exit(1)

configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)

def create_and_set_rich_menu():
    print("開始設定圖文選單...")
    
    with ApiClient(configuration) as api_client:
        line_api = MessagingApi(api_client)
        line_api_blob = MessagingApiBlob(api_client)
        
        # 1. 建立圖文選單設定 (Rich Menu Object)
        # 設定為 2500x1686 的全版尺寸 (2x2 田字型)
        rich_menu_to_create = RichMenuRequest(
            size=RichMenuSize(width=2500, height=1686),
            selected=True,
            name="官方帳號綜合選單",
            chatBarText="選單功能",
            areas=[
                # 左上 (0,0): 退休金試算
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=0, width=1250, height=843),
                    action=URIAction(uri=LIFF_URL)
                ),
                # 右上 (1250,0): 財稅優化策略 (由 OA Manager 接管)
                RichMenuArea(
                    bounds=RichMenuBounds(x=1250, y=0, width=1250, height=843),
                    action=MessageAction(text="財稅優化策略")
                ),
                # 左下 (0,843): 資產傳承規劃 (由 OA Manager 接管)
                RichMenuArea(
                    bounds=RichMenuBounds(x=0, y=843, width=1250, height=843),
                    action=MessageAction(text="資產傳承規劃")
                ),
                # 右下 (1250,843): 預約會談
                RichMenuArea(
                    bounds=RichMenuBounds(x=1250, y=843, width=1250, height=843),
                    action=URIAction(uri="https://meet.google.com/") # 可替換為您的預約表單
                )
            ]
        )
        
        print("1. 正在向 LINE API 建立圖文選單物件...")
        try:
            rich_menu_response = line_api.create_rich_menu(rich_menu_to_create)
            rich_menu_id = rich_menu_response.rich_menu_id
            print(f" -> 成功建立圖文選單，ID: {rich_menu_id}")
        except Exception as e:
            print(f" -> 建立失敗: {e}")
            exit(1)
        
        # 2. 上傳測試圖片
        image_path = "rich_menu_placeholder.jpg"
        print("重新產生 2x2 測試圖片...")
        try:
            from PIL import Image, ImageDraw
            img = Image.new('RGB', (2500, 1686), color=(255, 255, 255))
            d = ImageDraw.Draw(img)
            
            # 左上: 退休金試算 (暖橘)
            d.rectangle([(0,0), (1250, 843)], fill=(253, 230, 138))
            # 右上: 財稅優化策略 (粉藍)
            d.rectangle([(1250,0), (2500, 843)], fill=(191, 219, 254))
            # 左下: 資產傳承規劃 (柔紫)
            d.rectangle([(0,843), (1250, 1686)], fill=(233, 213, 255))
            # 右下: 預約會談 (淺綠)
            d.rectangle([(1250,843), (2500, 1686)], fill=(167, 243, 208))
            
            # 畫分隔線
            d.line([(1250, 0), (1250, 1686)], fill=(255, 255, 255), width=10)
            d.line([(0, 843), (2500, 843)], fill=(255, 255, 255), width=10)
            
            # 壓縮存檔 (品質設定為 60，避免超過 1MB)
            img.save(image_path, "JPEG", quality=60)
            print(f" -> 已自動產生四色測試圖片 {image_path} (壓縮版)")
        except ImportError:
            print(" -> 錯誤：需要 Pillow 套件來產生圖片。")
            exit(1)

        print("2. 正在上傳圖文選單圖片...")
        try:
            with open(image_path, 'rb') as f:
                content = f.read()
                line_api_blob.set_rich_menu_image(
                    rich_menu_id=rich_menu_id,
                    body=content,
                    _headers={'Content-Type': 'image/jpeg'}
                )
            print(" -> 成功上傳圖片")
        except Exception as e:
            print(f" -> 圖片上傳失敗: {e}")
            exit(1)

        # 3. 將此圖文選單設定為該 LINE OA 的預設選單
        print("3. 將圖文選單設定為預設...")
        try:
            line_api.set_default_rich_menu(rich_menu_id)
            print(" -> 設定完成！請打開手機上的 LINE 官方帳號聊天室確認圖文選單是否出現。")
        except Exception as e:
            print(f" -> 設定預設失敗: {e}")

if __name__ == "__main__":
    create_and_set_rich_menu()
