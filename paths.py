"""跨平台路径与便携布局。

- 源码运行：以本文件所在目录为程序目录。
- 打包 exe 运行：以 exe 所在目录为程序目录（保证 config.json 可改、输出可写）。
- templates：优先用程序目录下的（可自行替换），没有则回退到包内自带。
"""
import sys
from pathlib import Path


def app_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def bundle_dir() -> Path:
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        return Path(meipass)
    return app_dir()


BASE = app_dir()


def templates_dir() -> Path:
    for cand in (app_dir() / "templates", bundle_dir() / "templates"):
        if cand.exists():
            return cand
    raise FileNotFoundError("找不到 templates 文件夹，请确认安装完整")


def output_dir() -> Path:
    d = app_dir() / "输出"
    d.mkdir(parents=True, exist_ok=True)
    return d


DEFAULT_CONFIG = {
    "_说明": "固定信息只需填写一次，保存在此文件中。每次新案件无需重复填写。",
    "law_firm": "河北禄存律师事务所",
    "lawyer": "高卫华",
    "lawyer_id": "132823197803202919",
    "lawyer_phone": "17332694563",
    "lawyer_addr": "河北省廊坊市香河县自在城小区底商2-0-007号（三强水厂营业厅西侧）",
    "office_addr": "河北禄存律师事务所办公室",
    "court_default": "大厂回族自治县人民法院",
    "fee_standard": "冀律协2016第7号",
    "fee_method": "现金",
    "pay_method": "签订合同之日支付",
    "delegate_period_default": "一审终结之日止",
    "contract_no_prefix": "（2026）冀禄律民字第",
}


def config_path() -> Path:
    return app_dir() / "config.json"


def ensure_config() -> Path:
    """exe 首次运行时若 exe 旁没有 config.json，则释放一份默认的。"""
    p = config_path()
    if not p.exists():
        import json
        bundled = bundle_dir() / "config.json"
        if bundled.exists():
            p.write_bytes(bundled.read_bytes())
        else:
            p.write_text(json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2), encoding="utf-8")
    return p
