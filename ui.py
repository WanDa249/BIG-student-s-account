"""
主界面UI模块，负责窗口布局和交互
"""
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from data_manager import DataManager, BookManager
from chart import ChartManager
import datetime
def run_app():
    import os
     # 自动检测并创建账本数据文件夹
    books_dir = "d:/project/account/books"
    if not os.path.exists(books_dir):
        os.makedirs(books_dir)
    def export_pdf_action():
        from tkinter import filedialog
        pdf_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF文件", "*.pdf")])
        if pdf_path:
            try:
                dm.export_pdf(pdf_path)
                messagebox.showinfo("导出成功", f"PDF已保存到：{pdf_path}")
            except Exception as e:
                messagebox.showerror("导出失败", str(e))
    app = tk.Tk()
    app.title("My记账")
    app.geometry("900x600")
    book_mgr = BookManager(data_path="d:/project/account/books")
    current_book_var = tk.StringVar(value=book_mgr.current_book)

    # 刷新账本下拉框
    def refresh_books():
        book_menu['values'] = book_mgr.list_books()
        current_book_var.set(book_mgr.current_book)

    # 切换账本
    def switch_book(event=None):
        try:
            book_mgr.switch_book(current_book_var.get().replace('.csv',''))
            dm.__init__(book_file=book_mgr.current_book)
            refresh_list()
            # 切换成功不再弹窗提示
        except Exception as e:
            messagebox.showerror("账本切换失败", str(e))

    # 新建账本
    def new_book():
        name = new_book_var.get().strip()
        if name:
            try:
                book_mgr.new_book(name)
                refresh_books()
                switch_book()
                new_book_var.set("")
                messagebox.showinfo("新建账本", f"账本 {name} 创建成功！")
            except Exception as e:
                messagebox.showerror("新建账本失败", str(e))

    # 删除账本
    def delete_book():
        name = current_book_var.get().replace('.csv','')
        if name:
            confirm = messagebox.askyesno("确认删除", f"确定要删除账本 {name} 吗？此操作不可恢复！")
            if not confirm:
                return
            try:
                book_mgr.delete_book(name)
                refresh_books()
                switch_book()
                messagebox.showinfo("删除账本", f"账本 {name} 已删除！")
            except Exception as e:
                messagebox.showerror("删除账本失败", str(e))

    book_frame = tk.Frame(app)
    book_frame.pack(fill=tk.X, padx=10, pady=5)
    tk.Label(book_frame, text="账本:").pack(side=tk.LEFT)
    book_menu = ttk.Combobox(book_frame, textvariable=current_book_var, state="readonly")
    book_menu.pack(side=tk.LEFT)
    book_menu.bind('<<ComboboxSelected>>', switch_book)
    new_book_var = tk.StringVar()
    tk.Entry(book_frame, textvariable=new_book_var, width=12).pack(side=tk.LEFT)
    tk.Button(book_frame, text="新建账本", command=new_book).pack(side=tk.LEFT, padx=5)
    tk.Button(book_frame, text="删除账本", command=delete_book).pack(side=tk.LEFT, padx=5)
    refresh_books()
    dm = DataManager()

    # 账本管理区
    # 在主账本管理区添加导出PDF按钮
    tk.Button(book_frame, text="导出PDF", command=export_pdf_action).pack(side=tk.RIGHT, padx=5)
    # ...账本管理区结束，后续为活动记账、图表分析、表单区等...



    # 图表分析入口
    def show_trend_chart():
        ChartManager(dm.df).show_trend()

    def show_category_pie():
        ChartManager(dm.df).show_category_pie()

    chart_frame = tk.Frame(app)
    chart_frame.pack(fill=tk.X, padx=10, pady=5)
    tk.Button(chart_frame, text="收支趋势图", command=show_trend_chart).pack(side=tk.LEFT, padx=5)
    tk.Button(chart_frame, text="分类饼图", command=show_category_pie).pack(side=tk.LEFT, padx=5)

    # 表单区
    form_frame = tk.Frame(app)
    form_frame.pack(fill=tk.X, padx=10, pady=5)
    # 冗余import已清理，datetime已全局导入
    tk.Label(form_frame, text="日期:").grid(row=0, column=0)
    # 冗余import已清理，datetime已全局导入
    date_var = tk.StringVar(value=datetime.date.today().strftime('%Y-%m-%d'))
    def update_date(*args):
        date_var.set(date_combo.get())
    date_list = [(datetime.date.today() - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(0, 365)]
    date_combo = ttk.Combobox(form_frame, textvariable=date_var, values=date_list, state="readonly", width=12)
    date_combo.grid(row=0, column=1)
    date_combo.bind('<<ComboboxSelected>>', update_date)
    tk.Label(form_frame, text="类别:").grid(row=0, column=2)
    # 固定类别选项，禁止自定义输入
    common_categories = [
        "餐饮", "购物", "交通", "学习", "娱乐", "通讯", "健康", "社交", "其他", "收入"
    ]
    category_var = tk.StringVar()
    category_combo = ttk.Combobox(form_frame, textvariable=category_var, width=12, state="readonly")
    category_combo['values'] = common_categories
    category_combo.grid(row=0, column=3)
    tk.Label(form_frame, text="金额:").grid(row=0, column=4)
    amount_var = tk.StringVar()
    tk.Entry(form_frame, textvariable=amount_var, width=10).grid(row=0, column=5)
    tk.Label(form_frame, text="备注:").grid(row=0, column=6)
    remark_var = tk.StringVar()
    tk.Entry(form_frame, textvariable=remark_var, width=20).grid(row=0, column=7)
    # 删除颜色相关控件
    # 删除图片相关控件

    # 添加收支记录
    def add_record():
        try:
            date = date_var.get()
            category = category_var.get().strip()
            if not category:
                messagebox.showwarning("类别必填", "请先选择类别！")
                return
            amount = float(amount_var.get())
            remark = remark_var.get()
            dm.add_record(date, category, amount, remark)
            refresh_list()
            date_var.set(datetime.date.today().strftime('%Y-%m-%d'))
            amount_var.set("")
            remark_var.set("")
            category_var.set("")
            # 禁止自定义类别，用户只能选不能填
            messagebox.showinfo("添加成功", "记录已添加！")
        except Exception as e:
            messagebox.showerror("添加失败", str(e))

    # 快捷键支持：Enter添加记录，Ctrl+F筛选
    app.bind('<Return>', lambda e: add_record())
    app.bind('<Control-f>', lambda e: filter_by_category())

    # 已用 Combobox 替代右键菜单，相关绑定代码已移除

    tk.Button(form_frame, text="添加记录", command=add_record).grid(row=0, column=8, padx=10)

    # 列表区
    list_frame = tk.Frame(app)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    columns = ("日期", "类别", "金额", "备注")
    tree = ttk.Treeview(list_frame, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    # 删除图片预览逻辑
    tree.pack(fill=tk.BOTH, expand=True)

    def refresh_list():
        for i in tree.get_children():
            tree.delete(i)
        for idx, row in dm.df.iterrows():
            tree.insert("", "end", iid=idx, values=(row["日期"], row["类别"], row["金额"], row["备注"]))

    refresh_list()

    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请选择要删除的记录")
            return
        try:
            idx_list = [int(i) for i in selected]
            dm.batch_delete(idx_list)
            refresh_list()
            messagebox.showinfo("删除成功", f"已删除 {len(idx_list)} 条记录！")
        except Exception as e:
            messagebox.showerror("删除失败", str(e))

    tk.Button(app, text="删除选中记录", command=delete_selected).pack(pady=5)

    # 筛选区（类别下拉选择）
    filter_frame = tk.Frame(app)
    filter_frame.pack(fill=tk.X, padx=10, pady=5)
    tk.Label(filter_frame, text="筛选类别:").pack(side=tk.LEFT)
    filter_category_var = tk.StringVar()
    filter_category_combo = ttk.Combobox(filter_frame, textvariable=filter_category_var, values=common_categories, state="readonly", width=12)
    filter_category_combo.pack(side=tk.LEFT)

    def filter_by_category():
        cat = filter_category_var.get()
        df = dm.get_records(category=cat) if cat else dm.df
        for i in tree.get_children():
            tree.delete(i)
        for idx, row in df.iterrows():
            tree.insert("", "end", iid=idx, values=(row["日期"], row["类别"], row["金额"], row["备注"]))

    tk.Button(filter_frame, text="筛选", command=filter_by_category).pack(side=tk.LEFT, padx=5)

    app.mainloop()

