"""浏览器版 - 不依赖 tkinter，解决老 Tk 白屏问题。
运行： python3 app_web.py
然后浏览器自动打开 http://127.0.0.1:8000 ，填写后点生成即可。
只用标准库，无需额外安装。
"""
import datetime
import html
import json
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
import sys

BASE = Path(__file__).parent
sys.path.insert(0, str(BASE))
import generator as G
from paths import ensure_config

CONFIG_PATH = ensure_config()
PORT = 8000


def load_cfg():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def esc(s):
    return html.escape(s or "", quote=True)


def form_html(cfg, msg="", download="", case_dir="", parts=None):
    today = datetime.date.today().isoformat()
    msg_html = f'<div class="msg">{msg}</div>' if msg else ""
    dl_html = ""
    if download:
        items = "".join(
            f'<li><a href="/download?file={urllib.parse.quote(case_dir + "/" + n)}">{esc(n)}</a></li>'
            for n in (parts or []))
        dl_html = (f'<div class="msg ok">已生成到文件夹 <b>{esc(case_dir)}</b>：'
            f'<ol>{items}</ol>'
            f'另有合一版：<a href="/download?file={urllib.parse.quote(case_dir + "/" + download)}">{esc(download)}</a>'
            f'（合一版每份另起一页、奇数页起始，双面打印每份都从正面开始；独立文档可直接打印）</div>')
    return f"""<!doctype html>
<html lang="zh"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>委托文件一键生成器</title>
<style>
body{{font-family:-apple-system,PingFang SC,Microsoft YaHei,sans-serif;max-width:760px;margin:24px auto;padding:0 16px;background:#f6f7f9;color:#222}}
.card{{background:#fff;border-radius:12px;padding:20px 22px;box-shadow:0 2px 12px rgba(0,0,0,.06);margin-bottom:16px}}
h1{{font-size:20px;margin:0 0 4px}} .sub{{color:#666;font-size:13px;margin-bottom:12px}}
h2{{font-size:15px;margin:18px 0 8px;color:#444;border-left:4px solid #2b7fff;padding-left:8px}}
label{{display:block;font-size:13px;margin:10px 0 4px;color:#333}} label b{{color:#d00}}
input,select{{width:100%;font-size:15px;padding:9px 10px;border:1px solid #ccd;border-radius:8px;box-sizing:border-box}}
.row2{{display:flex;gap:10px}} .row2>div{{flex:1}}
.btn{{display:inline-block;background:#2b7fff;color:#fff;border:0;border-radius:10px;font-size:17px;padding:12px 26px;cursor:pointer;margin-top:14px}}
.btn:active{{background:#1f66d6}}
.msg{{background:#fff7e6;border:1px solid #ffd88a;border-radius:10px;padding:10px 12px;margin-bottom:12px;font-size:14px}}
.msg.ok{{background:#e9f7ee;border-color:#9ed7ae}}
.tip{{color:#888;font-size:12px}} a{{color:#2b7fff}}
</style></head><body>
<h1>委托文件一键生成器</h1>
<div class="sub">河北禄存律师事务所 · 填一次表单 → 生成6份独立文档（直接打印）+ 1份合一版 · 日期自动为今天 · 原模板格式不动</div>
{msg_html}{dl_html}
<form method="post" action="/generate" class="card">
<h2>一、委托人</h2>
<label>委托人姓名 <b>*</b> <span class="tip">多人用顿号，如：叶建义、叶建海</span></label>
<input name="client_names" required placeholder="如：王廷艳">
<label>身份证号 <b>*</b> <span class="tip">多人用空格/顿号分隔</span></label>
<input name="client_ids" required placeholder="如：132822196408053545">
<label>送达地址/住址 <b>*</b></label>
<input name="client_addr" required placeholder="如：河北省廊坊市大厂回族自治县祁各庄镇田各庄村9排56号">
<label>联系电话 <b>*</b></label>
<input name="client_phone" required placeholder="如：13323060586">

<h2>二、对方与案由</h2>
<label>对方当事人 <b>*</b></label>
<input name="opponent" required placeholder="如：王艳萍">
<label>案由 <b>*</b> <span class="tip">不用写“纠纷”二字，如：土地承包经营权转让合同</span></label>
<input name="case_reason" required placeholder="如：土地承包经营权转让合同">
<div class="row2"><div>
<label>管辖法院</label>
<input name="court" value="{esc(cfg.get('court_default','大厂回族自治县人民法院'))}">
</div><div>
<label>案号（可选，立案前可空）</label>
<input name="case_no" placeholder="如：(2026)冀1024民初123号">
</div></div>
<div class="row2"><div>
<label>合同编号（可选，空=自动）</label>
<input name="contract_no" placeholder="空=自动编号">
</div><div>
<label>有效期至</label>
<select name="valid_until">
<option>一审终结之日止</option><option>二审终结之日止</option>
<option>执行终结之日止</option><option>再审终结之日止</option><option>仲裁终结之日止</option>
</select>
</div></div>
<label>落款日期（自动为今天，可改）</label>
<input name="date" value="{today}">

<h2>三、费用</h2>
<div class="row2"><div>
<label>代理费（元）<b>*</b></label>
<input name="fee" value="6000" required>
</div><div>
<label>其他费用（元）</label>
<input name="other_fee" value="0">
</div></div>
<div class="row2"><div>
<label>收费方式</label>
<input name="fee_method" value="{esc(cfg.get('fee_method','现金'))}">
</div><div>
<label>支付方式</label>
<input name="pay_method" value="{esc(cfg.get('pay_method','签订合同之日支付'))}">
</div></div>

<h2>四、退费银行账户（法院退诉讼费）</h2>
<label>户名 <b>*</b> <span class="tip">默认同委托人，可空=自动同委托人；个人须一类账户</span></label>
<input name="bank_holder" placeholder="空=同委托人">
<label>账号 <b>*</b></label>
<input name="bank_account" required placeholder="如：6217991460009948721">
<label>开户行 <b>*</b> <span class="tip">精确到支行/营业所</span></label>
<input name="bank_branch" required placeholder="如：中国邮政储蓄银行股份有限公司大厂回族自治县大安东街营业所">

<button class="btn" type="submit">★ 生成本案文件（6份独立 + 合一版）</button>
</form>
<div class="card tip">生成结果为“输出/委托人与对方案由_日期/”文件夹，内含 6 份独立文档（签名处留白手写，可直接分别打印）+ 1 份合一版（无封面，每份另起一页，奇数页起始，可直接双面打印出 6 份独立文件）。<br>
固定信息（律所/律师/电话地址）保存在 config.json，如需修改请用记事本打开该文件改一次即可。</div>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body: bytes, ctype="text/html; charset=utf-8", status=200):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        cfg = load_cfg()
        if self.path.startswith("/download"):
            q = urllib.parse.urlparse(self.path).query
            fname = urllib.parse.parse_qs(q).get("file", [""])[0]
            # 允许“案件文件夹/文件名”形式，逐段取 basename 防目录穿越
            parts = [Path(p).name for p in fname.split("/") if p not in ("", ".", "..")]
            f = G.OUTPUT_DIR.joinpath(*parts) if parts else G.OUTPUT_DIR
            try:
                f = f.resolve()
                f.relative_to(G.OUTPUT_DIR.resolve())
            except Exception:
                self._send("非法路径".encode(), status=400)
                return
            if not f.is_file():
                self._send("文件不存在".encode(), status=404)
                return
            safe = f.name
            data = f.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{urllib.parse.quote(safe)}")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self._send(form_html(cfg).encode("utf-8"))

    def do_POST(self):
        cfg = load_cfg()
        if self.path == "/generate":
            ln = int(self.headers.get("Content-Length", 0))
            fields = urllib.parse.parse_qs(self.rfile.read(ln).decode("utf-8"), keep_blank_values=True)
            d = {k: v[0].strip() for k, v in fields.items()}
            # 校验
            need = {"client_names": "委托人姓名", "client_ids": "身份证号", "client_addr": "送达地址",
                    "opponent": "对方当事人", "case_reason": "案由", "client_phone": "联系电话",
                    "fee": "代理费", "bank_account": "银行账号", "bank_branch": "开户行"}
            miss = [n for k, n in need.items() if not d.get(k)]
            if miss:
                self._send(form_html(cfg, msg="缺少必填项：" + "、".join(miss)).encode("utf-8"))
                return
            try:
                d["date"] = datetime.date.fromisoformat(d.get("date") or datetime.date.today().isoformat())
            except Exception:
                self._send(form_html(cfg, msg="日期格式不对，请用 2026-09-18 格式").encode("utf-8"))
                return
            if not d.get("bank_holder"):
                d["bank_holder"] = d.get("client_names", "")
            try:
                res = G.generate_case(d, cfg)
                self._send(form_html(cfg, download=res["merged"].name, case_dir=res["dir"].name, parts=[p.name for p in res["parts"]]).encode("utf-8"))
            except Exception as e:
                self._send(form_html(cfg, msg="生成失败：" + html.escape(str(e))).encode("utf-8"))
            return
        self._send(b"not found", status=404)


if __name__ == "__main__":
    try:
        import docx  # noqa: F401
    except ImportError:
        print("缺少 python-docx，请先运行：")
        print(f"  {sys.executable} -m pip install -r requirements.txt")
        sys.exit(1)
    # 8000 被占用时自动顺延，避免“拒绝访问”其实是端口冲突
    srv = None
    url = ""
    for port in range(8000, 8011):
        try:
            HTTPServer.allow_reuse_address = True
            srv = HTTPServer(("127.0.0.1", port), Handler)
            url = f"http://127.0.0.1:{port}"
            break
        except OSError:
            continue
    if srv is None:
        print("8000-8010 端口都被占用，请先关掉其他服务再试。")
        sys.exit(1)
    print(f"已启动：{url}  （浏览器会自动打开；若没有请手动复制地址到浏览器，Ctrl+C 退出）")
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n已退出。")
