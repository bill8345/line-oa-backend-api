import urllib.parse
import json
import time

def generate_quickchart_url(history: dict) -> str:
    """
    將計算的歷年資料軌跡轉換為 QuickChart API 圖片網址。
    使用與前端高度相似的折線圖設定。
    """
    
    # 避免產生超過 1000 字元的超長 URL (LINE Message 限制：hero.action.uri 必須 < 1000 字元)
    # 取出約 8~10 個資料點當作圖表呈現
    raw_ages = history["ages"]
    raw_funds = history["funds"]
    raw_needs_basic = history["needs_basic"]
    raw_needs_with_fun = history["needs_with_fun"]
    
    total_points = len(raw_ages)
    step = max(1, total_points // 8)
    
    # 取樣出新的短陣列 (確保包含最後一點)
    indices = list(range(0, total_points, step))
    if indices[-1] != total_points - 1:
        indices.append(total_points - 1)
        
    ages = [raw_ages[i] for i in indices]
    funds = [round(raw_funds[i] / 10000, 1) for i in indices]
    needs_basic = [round(raw_needs_basic[i] / 10000, 1) for i in indices]
    needs_with_fun = [round(raw_needs_with_fun[i] / 10000, 1) for i in indices]
    
    # 設定 QuickChart 的 Chart.js 格式
    chart_config = {
        "type": "line",
        "data": {
            "labels": ages,
            "datasets": [
                {
                    "label": "預估實際存款",
                    "data": funds,
                    "borderColor": "rgb(16, 185, 129)",
                    "backgroundColor": "rgba(16, 185, 129, 0.15)",
                    "borderWidth": 3,
                    "fill": True,
                    "pointRadius": 0
                },
                {
                    "label": "退休總需求 (僅生活)",
                    "data": needs_basic,
                    "borderColor": "rgb(59, 130, 246)", # 藍色
                    "backgroundColor": "rgba(59, 130, 246, 0.15)",
                    "borderWidth": 3,
                    "borderDash": [3, 3],
                    "fill": True,
                    "pointRadius": 0
                },
                {
                    "label": "退休總需求 (含娛樂)",
                    "data": needs_with_fun,
                    "borderColor": "rgb(245, 158, 11)",
                    "backgroundColor": "rgba(245, 158, 11, 0.15)",
                    "borderWidth": 3,
                    "borderDash": [5, 5],
                    "fill": True,
                    "pointRadius": 0
                }
            ]
        },
        "options": {
            "title": {
                "display": True,
                "text": "退休金與存款趨勢圖 (單位：萬)",
                "fontColor": "#4a4036",
                "fontSize": 18,
                "fontFamily": "sans-serif"
            },
            "legend": {
                "labels": {
                    "fontColor": "#4a4036",
                    "fontFamily": "sans-serif"
                }
            },
            "scales": {
                "xAxes": [{
                    "gridLines": {"display": False},
                    "ticks": {"fontColor": "#8c7e6c", "maxTicksLimit": 10, "fontFamily": "sans-serif"}
                }],
                "yAxes": [{
                    "gridLines": {"color": "rgba(74, 64, 54, 0.05)", "borderDash": [4, 4]},
                    "ticks": {"fontColor": "#8c7e6c", "fontFamily": "sans-serif"}
                }]
            }
        }
    }
    
    # 轉換為 json 字串
    chart_json = json.dumps(chart_config)
    
    # 組裝 QuickChart 網址 (米白色紙張背景)
    # width=600, height=400
    base_url = "https://quickchart.io/chart"
    params = {
        "c": chart_json,
        "w": 600,
        "h": 400,
        "bkg": "rgb(253,251,247)",
        "f": "png"
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}&ts={int(time.time())}"
    return url

if __name__ == "__main__":
    # Test
    from calculator import calculate_retirement_plan
    res = calculate_retirement_plan(32, 65, 30000, 10000, 10000, 1000000)
    print("QuickChart URL:")
    print(generate_quickchart_url(res["history"]))
