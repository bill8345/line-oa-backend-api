import urllib.parse
import json

def generate_quickchart_url(history: dict) -> str:
    """
    將計算的歷年資料軌跡轉換為 QuickChart API 圖片網址。
    使用與前端高度相似的折線圖設定。
    """
    
    # 避免產生超過 1000 字元的超長 URL (LINE Message 限制：hero.action.uri 必須 < 1000 字元)
    # 取出約 8~10 個資料點當作圖表呈現
    raw_ages = history["ages"]
    raw_funds = history["funds"]
    raw_needs = history["needs"]
    
    total_points = len(raw_ages)
    step = max(1, total_points // 8)
    
    # 取樣出新的短陣列 (確保包含最後一點)
    indices = list(range(0, total_points, step))
    if indices[-1] != total_points - 1:
        indices.append(total_points - 1)
        
    ages = [raw_ages[i] for i in indices]
    funds = [raw_funds[i] for i in indices]
    needs = [raw_needs[i] for i in indices]
    
    # 設定 QuickChart 的 Chart.js 格式
    chart_config = {
        "type": "line",
        "data": {
            "labels": ages,
            "datasets": [
                {
                    "label": "預估實際存款",
                    "data": funds,
                    "borderColor": "rgb(0, 195, 0)",
                    "backgroundColor": "rgba(0, 195, 0, 0.1)",
                    "borderWidth": 2,
                    "fill": True,
                    "pointRadius": 0
                },
                {
                    "label": "退休總需求",
                    "data": needs,
                    "borderColor": "rgb(54, 162, 235)",
                    "backgroundColor": "rgba(54, 162, 235, 0.1)",
                    "borderWidth": 2,
                    "fill": True,
                    "pointRadius": 0
                }
            ]
        },
        "options": {
            "title": {
                "display": True,
                "text": "資金缺口與存款歷年趨勢圖",
                "fontColor": "#ffffff",
                "fontSize": 16
            },
            "legend": {
                "labels": {
                    "fontColor": "#ffffff"
                }
            },
            "scales": {
                "xAxes": [{
                    "gridLines": {"display": False},
                    "ticks": {"fontColor": "#cccccc", "maxTicksLimit": 10}
                }],
                "yAxes": [{
                    "gridLines": {"color": "rgba(255, 255, 255, 0.2)"},
                    "ticks": {"fontColor": "#cccccc"}
                }]
            }
        }
    }
    
    # 轉換為 json 字串
    chart_json = json.dumps(chart_config)
    
    # 組裝 QuickChart 網址 (黑色背景 bkg=1e1e1e)
    # width=600, height=400
    base_url = "https://quickchart.io/chart"
    params = {
        "c": chart_json,
        "w": 600,
        "h": 400,
        "bkg": "rgb(20,20,20)",
        "f": "png"
    }
    
    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return url

if __name__ == "__main__":
    # Test
    from calculator import calculate_retirement_plan
    res = calculate_retirement_plan(32, 65, 30000, 10000, 10)
    print("QuickChart URL:")
    print(generate_quickchart_url(res["history"]))
