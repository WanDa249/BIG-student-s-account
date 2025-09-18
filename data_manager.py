"""
数据管理模块，负责收支记录的增删查改和统计分析
"""
import pandas as pd
import os
import csv

DEFAULT_BOOK = "records.csv"

class BookManager:
    def __init__(self, data_path="d:/project/account/books"):
        self.data_path = data_path
        self.books = self.list_books()
        self.current_book = self.books[0] if self.books else DEFAULT_BOOK

    def list_books(self):
        return [f for f in os.listdir(self.data_path) if f.endswith('.csv')]

    def new_book(self, name):
        file = os.path.join(self.data_path, name + ".csv")
        if not os.path.exists(file):
            with open(file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["日期", "类别", "金额", "备注"])
        self.books.append(name + ".csv")
        self.current_book = name + ".csv"

    def switch_book(self, name):
        if name + ".csv" in self.books:
            self.current_book = name + ".csv"

    def delete_book(self, name):
        file = os.path.join(self.data_path, name + ".csv")
        if os.path.exists(file):
            os.remove(file)
            self.books.remove(name + ".csv")
            self.current_book = self.books[0] if self.books else DEFAULT_BOOK

class DataManager:
    def export_pdf(self, pdf_file):
        import pandas as pd
        from matplotlib import pyplot as plt
        from matplotlib.backends.backend_pdf import PdfPages
        import colorsys
        df = self.df.copy()
        df["分类"] = df["类别"] + "-" + df["备注"].fillna("")
        df_income = df[df["类别"] == "收入"].copy()
        df_expense = df[df["类别"] != "收入"].copy()
        summary_income = df_income.groupby("分类")["金额"].sum().sort_values(ascending=False)
        summary_expense = df_expense.groupby("分类")["金额"].sum().sort_values(ascending=False)
        with PdfPages(pdf_file) as pdf:
            # 统计表
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.axis('off')
            table_data = [[cat, f"{amt:.2f}"] for cat, amt in pd.concat([summary_income, summary_expense]).items()]
            table = ax.table(cellText=table_data, colLabels=["类别", "总金额"], loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(12)
            table.scale(1, 1.5)
            ax.set_title("收支统计", fontsize=14)
            pdf.savefig(fig)
            plt.close(fig)
            # 收入饼图
            base_colors_income = ["#4B8ED9", "#FF8C8C", "#A3D977", "#FFD966", "#BCA0FF", "#FFB366", "#66FF99", "#FF66B2", "#A6A6A6"]
            all_categories_income = df_income["类别"].unique().tolist()
            color_map_income = {cat: base_colors_income[i % len(base_colors_income)] for i, cat in enumerate(all_categories_income)}
            def color_shift(hex_color, shift):
                rgb = tuple(int(hex_color.lstrip('#')[i:i+2], 16)/255.0 for i in (0,2,4))
                import colorsys
                h, l, s = colorsys.rgb_to_hls(*rgb)
                l = min(1, max(0, l + (shift-0.5)*0.1))  # 亮度变化幅度减小
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
                pie_colors_income.append(color_shift(color_map_income[cat], shift))
                cat_remark_idx_income[cat] = idx + 1
            fig2, ax2 = plt.subplots(figsize=(6, 6))
            ax2.pie(summary_income, labels=summary_income.index, autopct='%1.1f%%', startangle=140, colors=pie_colors_income)
            ax2.set_title("收入分类饼图", fontsize=14)
            pdf.savefig(fig2)
            plt.close(fig2)
            # 支出饼图
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
            fig3, ax3 = plt.subplots(figsize=(6, 6))
            ax3.pie(summary_expense, labels=summary_expense.index, autopct='%1.1f%%', startangle=140, colors=pie_colors_expense)
            ax3.set_title("支出分类饼图", fontsize=14)
            pdf.savefig(fig3)
            plt.close(fig3)
            # 趋势折线图（收入/支出分开）
            self.df["日期"] = pd.to_datetime(self.df["日期"])
            monthly_income = self.df[self.df["类别"]=="收入"].groupby(self.df["日期"].dt.to_period("M"))["金额"].sum()
            monthly_expense = self.df[self.df["类别"]!="收入"].groupby(self.df["日期"].dt.to_period("M"))["金额"].sum()
            fig4, ax4 = plt.subplots(figsize=(8, 4))
            monthly_income.plot(ax=ax4, marker='o', label='收入')
            monthly_expense.plot(ax=ax4, marker='o', label='支出')
            ax4.set_title("月度收支趋势", fontsize=14)
            ax4.set_xlabel("月份")
            ax4.set_ylabel("金额")
            ax4.legend()
            pdf.savefig(fig4)
            plt.close(fig4)
        return pdf_file


    def __init__(self, data_path=".", book_file=None):
        self.data_path = data_path
        self.book_file = book_file or DEFAULT_BOOK
        self.file = os.path.join(data_path, self.book_file)
        if not os.path.exists(self.file):
            with open(self.file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["日期", "类别", "金额", "备注"])
        self.df = pd.read_csv(self.file)

    def add_record(self, date, category, amount, remark):
        new_row = {"日期": date, "类别": category, "金额": amount, "备注": remark}
        self.df = pd.concat([self.df, pd.DataFrame([new_row])], ignore_index=True)
        self.df.to_csv(self.file, index=False)

    def get_records(self, date_range=None, category=None, amount_range=None, remark_keyword=None):
        df = self.df.copy()
        if date_range:
            df = df[(df["日期"] >= date_range[0]) & (df["日期"] <= date_range[1])]
        if category:
            df = df[df["类别"] == category]
        if amount_range:
            df = df[(df["金额"] >= amount_range[0]) & (df["金额"] <= amount_range[1])]
        if remark_keyword:
            df = df[df["备注"].str.contains(remark_keyword, na=False)]
        return df

    def edit_record(self, idx, date=None, category=None, amount=None, remark=None):
        if idx < 0 or idx >= len(self.df):
            raise IndexError("记录索引超出范围")
        if date:
            self.df.at[idx, "日期"] = date
        if category:
            self.df.at[idx, "类别"] = category
        if amount:
            self.df.at[idx, "金额"] = amount
        if remark:
            self.df.at[idx, "备注"] = remark


    # 删除指定索引的记录
    def delete_record(self, idx):
        """删除指定索引的收支记录"""
        if idx < 0 or idx >= len(self.df):
            raise IndexError("记录索引超出范围")
        self.df = self.df.drop(idx).reset_index(drop=True)
        self.df.to_csv(self.file, index=False)

    # 批量删除记录
    def batch_delete(self, idx_list):
        """批量删除收支记录"""
        self.df = self.df.drop(idx_list).reset_index(drop=True)
        self.df.to_csv(self.file, index=False)

    # 导入CSV数据
    def import_csv(self, import_file):
        """导入CSV文件到当前账本"""
        import_df = pd.read_csv(import_file)
        self.df = pd.concat([self.df, import_df], ignore_index=True)
        self.df.to_csv(self.file, index=False)

    # 导出CSV数据
    def export_csv(self, export_file):
        """导出当前账本为CSV文件"""
        self.df.to_csv(export_file, index=False)

    # 月度收支统计
    def monthly_stats(self, year=None):
        """按月统计收支总额"""
        df = self.df.copy()
        df["日期"] = pd.to_datetime(df["日期"])
        if year:
            df = df[df["日期"].dt.year == year]
        stats = df.groupby(df["日期"].dt.month)["金额"].agg(["sum"])
        return stats

    # 年度收支统计
    def yearly_stats(self):
        """按年统计收支总额"""
        df = self.df.copy()
        df["日期"] = pd.to_datetime(df["日期"])
        stats = df.groupby(df["日期"].dt.year)["金额"].agg(["sum"])
        return stats

    # 按类别统计收支
    def category_stats(self):
        """按类别统计收支总额"""
        stats = self.df.groupby("类别")["金额"].agg(["sum"]).sort_values("sum", ascending=False)
        return stats
