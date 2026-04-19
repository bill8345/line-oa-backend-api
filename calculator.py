def calculate_retirement_plan(current_age: int, retire_age: int, monthly_basic_expense: float, monthly_fun_expense: float, monthly_saving: float, current_saving: float, max_age: int = 100, interest_rate: float = 0.015):
    """
    計算退休規劃的資金需求、實際存款與缺口。
    假設：
    1. 活到 max_age 歲。
    2. 通膨率 3%，從目前年齡開始逐年計算。
    3. 存款利率 interest_rate，每年複利。
    4. 存款僅在工作期間 (目前 -> 退休) 持續投入。
    """
    INFLATION_RATE = 0.03

    years_to_live = max_age - current_age
    years_to_retire = retire_age - current_age
    
    # 歷年變化陣列，用來畫圖
    history_ages = [current_age]
    history_funds = [current_saving]
    history_needs_basic = [0]
    history_needs_with_fun = [0]
    
    total_fund = current_saving
    total_need_basic = 0
    total_need_with_fun = 0
    
    for y in range(1, years_to_live + 1):
        current_y_age = current_age + y
        
        # --- 計算存款軌跡 ---
        total_fund *= (1 + interest_rate)
        if y <= years_to_retire:
            total_fund += (monthly_saving * 12)
        
        # --- 計算需求軌跡 ---
        if y > years_to_retire:
            # 通膨從退休後才開始計算
            years_in_retirement = y - years_to_retire
            inflation_multiplier = (1 + INFLATION_RATE) ** years_in_retirement
            expense_basic_this_year = (monthly_basic_expense * 12) * inflation_multiplier
            expense_fun_this_year = (monthly_fun_expense * 12) * inflation_multiplier
            
            total_need_basic += expense_basic_this_year
            total_need_with_fun += (expense_basic_this_year + expense_fun_this_year)
            
        history_ages.append(current_y_age)
        history_funds.append(round(total_fund))
        history_needs_basic.append(round(total_need_basic))
        history_needs_with_fun.append(round(total_need_with_fun))

    # 3. 資金缺口 = 總需求(含娛樂) - 實際存款
    gap = total_need_with_fun - total_fund
    if gap < 0:
        gap = 0
    
    # 4. 找出交叉點：存款低於累積需求(含娛樂)的年齡
    crossover_age = None
    for i in range(1, len(history_ages)):
        if history_needs_with_fun[i] > 0 and history_needs_with_fun[i] >= history_funds[i]:
            crossover_age = history_ages[i]
            break
        
    return {
        "total_need_basic": round(total_need_basic),
        "total_need_with_fun": round(total_need_with_fun),
        "total_fund": round(total_fund),
        "gap": round(gap),
        "crossover_age": crossover_age,
        "history": {
            "ages": history_ages,
            "funds": history_funds,
            "needs_basic": history_needs_basic,
            "needs_with_fun": history_needs_with_fun
        }
    }

if __name__ == "__main__":
    # Test
    res = calculate_retirement_plan(
        current_age=30,
        retire_age=65,
        monthly_basic_expense=40000,
        monthly_fun_expense=10000,
        monthly_saving=20000,
        current_saving=1000000
    )
    import json
    print(json.dumps(res, indent=2, ensure_ascii=False))
