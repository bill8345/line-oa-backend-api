def calculate_retirement_plan(current_age: int, retire_age: int, monthly_expense: float, monthly_saving: float, current_saving: float):
    """
    計算退休規劃的資金需求、實際存款與缺口。
    假設：
    1. 活到 100 歲。
    2. 通膨率 3%，從目前年齡開始逐年計算。
    3. 存款利率 1.5%，每年複利。
    4. 存款僅在工作期間 (目前 -> 退休) 持續投入。
    """
    MAX_AGE = 100
    INFLATION_RATE = 0.03
    INTEREST_RATE = 0.015

    years_to_live = MAX_AGE - current_age
    years_to_retire = retire_age - current_age
    
    # 歷年變化陣列，用來畫圖
    history_ages = [current_age]
    history_funds = [current_saving]
    history_needs = [0] # 目前年齡的累積總需求為 0 或是可以顯示與目前存款同高(視為無缺口起始)，這邊以0累加
    
    total_fund = current_saving
    total_need = 0
    
    for y in range(1, years_to_live + 1):
        current_y_age = current_age + y
        
        # --- 計算存款軌跡 ---
        total_fund *= (1 + INTEREST_RATE)
        if y <= years_to_retire:
            total_fund += (monthly_saving * 12)
        
        # --- 計算需求軌跡 ---
        if y > years_to_retire:
            # 通膨從退休後才開始計算
            years_in_retirement = y - years_to_retire
            expense_this_year = (monthly_expense * 12) * ((1 + INFLATION_RATE) ** years_in_retirement)
            total_need += expense_this_year
            
        history_ages.append(current_y_age)
        history_funds.append(round(total_fund))
        history_needs.append(round(total_need))

    # 3. 資金缺口 = 總需求 - 實際存款
    gap = total_need - total_fund
    if gap < 0:
        gap = 0
        
    return {
        "total_need": round(total_need),
        "total_fund": round(total_fund),
        "gap": round(gap),
        "history": {
            "ages": history_ages,
            "funds": history_funds,
            "needs": history_needs
        }
    }

if __name__ == "__main__":
    # Test
    res = calculate_retirement_plan(
        current_age=30,
        retire_age=65,
        monthly_expense=50000,
        monthly_saving=20000,
        current_saving=1000000
    )
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))
