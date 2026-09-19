"""一次性委托文件生成器 - 启动程序后填写表单，一键生成合并文档。
运行： python3 app.py
依赖： pip install -r requirements.txt （只需 python-docx）
"""
import datetime
import json
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
import generator as G
from paths import ensure_config, app_dir

CONFIG_PATH = ensure_config()


def load_cfg():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def save_cfg(cfg):
    CONFIG_PATH.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("委托文件一键生成器 - 河北禄存律师事务所")
        self.geometry("720x860")
        self.cfg = load_cfg()
        self._build()

    def _build(self):
        pad = {"padx": 8, "pady": 4}
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(main, text="新委托案件信息（*为必填）", font=("PingFang SC", 13, "bold")).pack(anchor="w", pady=(0, 6))

        form = ttk.Frame(main)
        form.pack(fill="x")

        self.vars = {}
        def add_row(label, key, default="", width=52, row=None, tip=""):
            r = ttk.Frame(form)
            r.pack(fill="x", pady=2)
            ttk.Label(r, text=label, width=16, anchor="e").pack(side="left")
            v = tk.StringVar(value=default)
            e = ttk.Entry(r, textvariable=v, width=width)
            e.pack(side="left", fill="x", expand=True, padx=(6, 2))
            if tip:
                ttk.Label(r, text=tip, foreground="gray").pack(side="left")
            self.vars[key] = v
            return e

        today = datetime.date.today()
        # --- 委托人 ---
        ttk.Label(form, text="— 委托人 —", foreground="#555").pack(anchor="w", pady=(8, 2))
        add_row("委托人姓名 *", "client_names", tip="多人用顿号，如：叶建义、叶建海")
        add_row("身份证号 *", "client_ids", tip="多人用空格/顿号分隔")
        add_row("送达地址/住址 *", "client_addr", default="")
        add_row("联系电话 *", "client_phone", default="")

        # --- 案件 ---
        ttk.Label(form, text="— 对方与案由 —", foreground="#555").pack(anchor="w", pady=(8, 2))
        add_row("对方当事人 *", "opponent", tip="如：王艳萍")
        add_row("案由 *", "case_reason", tip="如：土地承包经营权转让合同（不用写“纠纷”）")
        add_row("管辖法院", "court", default=self.cfg.get("court_default", "大厂回族自治县人民法院"))
        add_row("案号（可选）", "case_no", tip="立案前可空着，后补")
        add_row("合同编号（可选）", "contract_no", tip="空=自动编号")
        # 有效期
        r = ttk.Frame(form); r.pack(fill="x", pady=2)
        ttk.Label(r, text="有效期至", width=16, anchor="e").pack(side="left")
        self.vars["valid_until"] = tk.StringVar(value=self.cfg.get("delegate_period_default", "一审终结之日止"))
        cb = ttk.Combobox(r, textvariable=self.vars["valid_until"], width=50,
                          values=["一审终结之日止", "二审终结之日止", "执行终结之日止", "再审终结之日止", "仲裁终结之日止"])
        cb.pack(side="left", fill="x", expand=True, padx=(6, 2))
        # 日期
        r2 = ttk.Frame(form); r2.pack(fill="x", pady=2)
        ttk.Label(r2, text="落款日期", width=16, anchor="e").pack(side="left")
        self.vars["date"] = tk.StringVar(value=today.isoformat())
        ttk.Entry(r2, textvariable=self.vars["date"], width=20).pack(side="left", padx=(6, 2))
        ttk.Label(r2, text="自动为今天，可改（格式2026-09-18）", foreground="gray").pack(side="left")

        # --- 费用 ---
        ttk.Label(form, text="— 费用 —", foreground="#555").pack(anchor="w", pady=(8, 2))
        add_row("代理费（元）*", "fee", default="6000")
        add_row("其他费用（元）", "other_fee", default="0")
        add_row("收费方式", "fee_method", default=self.cfg.get("fee_method", "现金"))
        add_row("支付方式", "pay_method", default=self.cfg.get("pay_method", "签订合同之日支付"))

        # --- 银行 ---
        ttk.Label(form, text="— 退费银行账户（法院退诉讼费用）—", foreground="#555").pack(anchor="w", pady=(8, 2))
        e_holder = add_row("户名 *", "bank_holder", tip="个人须一类账户")
        add_row("账号 *", "bank_account", default="")
        add_row("开户行 *", "bank_branch", tip="精确到支行/营业所")
        btn_row = ttk.Frame(form); btn_row.pack(fill="x", pady=2)
        ttk.Button(btn_row, text="户名同委托人", command=self._sync_holder).pack(side="left", padx=(130, 6))

        # --- 操作 ---
        op = ttk.Frame(main); op.pack(fill="x", pady=12)
        ttk.Button(op, text="★ 生成本案文件（6份独立+合一版）", command=self._generate).pack(side="left", padx=4, ipadx=8, ipady=4)
        ttk.Button(op, text="打开输出文件夹", command=self._open_out).pack(side="left", padx=4)
        ttk.Button(op, text="固定信息设置", command=self._open_settings).pack(side="left", padx=4)

        self.status = tk.StringVar(value="日期已自动填为今天；固定律所/律师信息保存在 config.json。")
        ttk.Label(main, textvariable=self.status, wraplength=680, foreground="#333").pack(anchor="w", pady=6)
        ttk.Label(main, text="生成结果为案件文件夹：6 份独立文档（签名留白手写，直接打印）+ 1 份合一版（无封面，每份另起一页、奇数页起始，双面打印即出 6 份）。\n原模板在 templates/ 文件夹，请勿删除；固定信息改一次即可。",
                  wraplength=680, foreground="gray").pack(anchor="w")

    def _sync_holder(self):
        self.vars["bank_holder"].set(self.vars["client_names"].get().strip())

    def _collect(self):
        d = {k: v.get().strip() for k, v in self.vars.items()}
        # date 解析
        try:
            d["date"] = datetime.date.fromisoformat(d["date"]) if d["date"] else datetime.date.today()
        except Exception:
            raise ValueError("落款日期格式不对，请用 2026-09-18 格式")
        if not d.get("bank_holder"):
            d["bank_holder"] = d.get("client_names", "")
        return d

    def _validate(self, d):
        need = [("client_names", "委托人姓名"), ("client_ids", "身份证号"),
                ("client_addr", "送达地址"), ("client_phone", "联系电话"),
                ("opponent", "对方当事人"), ("case_reason", "案由"),
                ("fee", "代理费"), ("bank_account", "银行账号"), ("bank_branch", "开户行")]
        miss = [n for k, n in need if not d.get(k)]
        if miss:
            raise ValueError("以下为必填项，请补全：\n" + "、".join(miss))
        if not d["fee"].replace(".", "").replace(",", "").isdigit():
            raise ValueError("代理费请填写数字，如 6000")

    def _generate(self):
        try:
            d = self._collect()
            self._validate(d)
            res = G.generate_case(d, self.cfg)
            names = "\n".join([p.name for p in res["parts"]])
            self.status.set(f"已生成到文件夹：{res['dir'].name}\n合一版：{res['merged'].name}")
            messagebox.showinfo("生成成功",
                f"已生成 6 份独立文档 + 1 份合一版：\n{res['dir']}\n\n独立文档（可直接打印）：\n{names}\n\n合一版：\n{res['merged'].name}")
        except Exception as e:
            messagebox.showerror("无法生成", str(e))

    def _open_out(self):
        p = G.OUTPUT_DIR
        p.mkdir(exist_ok=True)
        try:
            if sys.platform == "darwin":
                subprocess.run(["open", str(p)])
            elif sys.platform.startswith("win"):
                subprocess.run(["explorer", str(p)])
            else:
                subprocess.run(["xdg-open", str(p)])
        except Exception as e:
            messagebox.showinfo("输出文件夹", str(p))

    def _open_settings(self):
        w = tk.Toplevel(self)
        w.title("固定信息（改一次即可）")
        w.geometry("620x460")
        keys = [("law_firm", "律所名称"), ("lawyer", "承办律师"), ("lawyer_id", "律师身份证号"),
                ("lawyer_phone", "律师电话"), ("lawyer_addr", "律师送达地址"),
                ("office_addr", "接待地点"), ("court_default", "默认法院"),
                ("fee_standard", "收费标准"), ("fee_method", "默认收费方式"),
                ("delegate_period_default", "默认委托期限")]
        vs = {}
        for k, label in keys:
            r = ttk.Frame(w); r.pack(fill="x", padx=10, pady=3)
            ttk.Label(r, text=label, width=14, anchor="e").pack(side="left")
            v = tk.StringVar(value=self.cfg.get(k, ""))
            ttk.Entry(r, textvariable=v, width=48).pack(side="left", fill="x", expand=True, padx=6)
            vs[k] = v

        def _save():
            for k, v in vs.items():
                self.cfg[k] = v.get().strip()
            save_cfg(self.cfg)
            # 同步主界面默认值
            self.vars["court"].set(self.cfg.get("court_default", ""))
            self.vars["fee_method"].set(self.cfg.get("fee_method", ""))
            self.vars["valid_until"].set(self.cfg.get("delegate_period_default", ""))
            messagebox.showinfo("已保存", "固定信息已保存到 config.json")
            w.destroy()
        ttk.Button(w, text="保存", command=_save).pack(pady=12)


if __name__ == "__main__":
    # 打包版无控制台：未捕获异常写入 error.log，方便排查
    if getattr(sys, "frozen", False):
        import traceback

        def _hook(typ, val, tb):
            try:
                (app_dir() / "error.log").write_text(
                    traceback.format_exception(typ, val, tb), encoding="utf-8")
            except Exception:
                pass
            try:
                messagebox.showerror("出错", f"{val}\n详情见 error.log")
            except Exception:
                pass
        sys.excepthook = _hook
    App().mainloop()
