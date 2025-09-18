"""
图表分析模块，负责绘制统计图表
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 支持中文
matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号
import pandas as pd

class ChartManager:
    def __init__(self, df):
        self.df = df

    def show_trend(self, year=None):
        df = self.df.copy()
        df["日期"] = pd.to_datetime(df["日期"])
        if year:
            df = df[df["日期"].dt.year == year]
        monthly_income = df[df["类别"]=="收入"].groupby(df["日期"].dt.month)["金额"].sum()
        monthly_expense = df[df["类别"]!="收入"].groupby(df["日期"].dt.month)["金额"].sum()
        plt.figure(figsize=(8,4))
        monthly_income.plot(marker='o', label='收入')
        monthly_expense.plot(marker='o', label='支出')
        plt.title(f"{year if year else '全部'}年度收支趋势")
        plt.xlabel("月份")
        plt.ylabel("金额")
        plt.grid(True)
        plt.legend()
        plt.show()

    def show_category_pie(self):
        df = self.df.copy()
        import colorsys
        # 收入饼图
        df_income = df[df["类别"] == "收入"].copy()
        df_income["分类"] = df_income["类别"] + "-" + df_income["备注"].fillna("")
        summary_income = df_income.groupby("分类")["金额"].sum()
        base_colors_income = ["#4B8ED9", "#FF8C8C", "#A3D977", "#FFD966", "#BCA0FF", "#FFB366", "#66FF99", "#FF66B2", "#A6A6A6"]
        all_categories_income = df_income["类别"].unique().tolist()
        color_map_income = {cat: base_colors_income[i % len(base_colors_income)] for i, cat in enumerate(all_categories_income)}
        def color_shift(hex_color, shift, scale=0.1):
            import colorsys
            rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16)/255.0 for i in (0,2,4))
            h, l, s = colorsys.rgb_to_hls(*rgb)
            l = min(1, max(0, l + (shift-0.5)*scale))
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            return '#%02x%02x%02x' % (int(r*255), int(g*255), int(b*255))
        cat_remark_count_income = {}
        for cat_remark in summary_income.index:
            cat = cat_remark.split('-')[0]
            cat_remark_count_income[cat] = cat_remark_count_income.get(cat, 0) + 1
        cat_remark_idx_income = {}
        pie_colors_income = []
        for cat_remark in summary_income.index:
            cat = cat_remark.split('-')[0]
            idx = cat_remark_idx_income.get(cat, 0)
            total = cat_remark_count_income[cat]
            shift = 0.2 + 0.6 * (idx / max(1,total-1)) if total > 1 else 0.5
            pie_colors_income.append(color_shift(color_map_income[cat], shift, scale=0.3))
            cat_remark_idx_income[cat] = idx + 1
        plt.figure(figsize=(6,6))
        plt.pie(summary_income, labels=summary_income.index, autopct='%1.1f%%', startangle=140, colors=pie_colors_income)
        plt.axis('equal')
        plt.title("收入分类饼图", pad=30)
        plt.show()
        # 支出饼图
        df_expense = df[df["类别"] != "收入"].copy()
        df_expense["分类"] = df_expense["类别"] + "-" + df_expense["备注"].fillna("")
        summary_expense = df_expense.groupby("分类")["金额"].sum()
        base_colors_expense = ["#FF8C8C", "#4B8ED9", "#A3D977", "#FFD966", "#BCA0FF", "#FFB366", "#66FF99", "#FF66B2", "#A6A6A6"]
        all_categories_expense = df_expense["类别"].unique().tolist()
        color_map_expense = {cat: base_colors_expense[i % len(base_colors_expense)] for i, cat in enumerate(all_categories_expense)}
        cat_remark_count_expense = {}
        for cat_remark in summary_expense.index:
            cat = cat_remark.split('-')[0]
            cat_remark_count_expense[cat] = cat_remark_count_expense.get(cat, 0) + 1
        cat_remark_idx_expense = {}
        pie_colors_expense = []
        for cat_remark in summary_expense.index:
            cat = cat_remark.split('-')[0]
            idx = cat_remark_idx_expense.get(cat, 0)
            total = cat_remark_count_expense[cat]
            shift = 0.2 + 0.6 * (idx / max(1,total-1)) if total > 1 else 0.5
            pie_colors_expense.append(color_shift(color_map_expense[cat], shift))
            cat_remark_idx_expense[cat] = idx + 1
        plt.figure(figsize=(6,6))
        plt.pie(summary_expense, labels=summary_expense.index, autopct='%1.1f%%', startangle=140, colors=pie_colors_expense)
        plt.axis('equal')
        plt.title("支出分类饼图", pad=30)
        plt.show()

   
