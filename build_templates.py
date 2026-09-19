"""01 号合同模板重建工具（02~06 号模板已定稿冻结，无需再跑）。

用法：用户在 WPS 中更新「原始模板/法律事务聘请律师合同--高卫华.docx」后，
运行 `python3 build_templates.py`，即以该文件为底（版式字体表格原样不动），
仅做文字占位符替换，生成 templates/01_聘请律师合同.docx。
"""
from pathlib import Path
import shutil
from docx import Document

from paths import BASE
TPL = BASE / "templates"
TPL.mkdir(exist_ok=True)

SRC_01 = BASE / "原始模板" / "法律事务聘请律师合同--高卫华.docx"
DST_01 = TPL / "01_聘请律师合同.docx"


def build_01_contract():
    """以用户转好的 docx 为底，仅替换文字为占位符。"""
    if not SRC_01.exists():
        print("根目录没有转好文件，保留现有 01 模板")
        return
    shutil.copy(str(SRC_01), str(DST_01))
    doc = Document(str(DST_01))
    pairs = [
        ("叶建义 叶建海 廊坊中新包装材料有限公司", "{{client_names}}"),
        ("与孙玉成提供劳务者受害责任纠纷", "{{vs_text}}"),
        ("高卫华", "{{lawyer}}"),
        ("河北禄存律师事务所", "{{law_firm}}"),
        ("（2026）冀禄律   字第    号", "{{contract_no}}"),
        ("本协议签订之日起至一审终结之日止", "本协议签订之日起至{{valid_until}}"),
        ("现金", "{{fee_method}}"),
        ("冀律协2016第7号", "{{fee_standard}}"),
        ("人民币：陆仟元整（￥ 6000元）", "人民币：{{fee_cn}}（￥{{fee}}元）"),
        ("签订合同之日支付", "{{pay_method}}"),
    ]

    def do_para(p):
        import re as _re
        full = "".join(r.text for r in p.runs)
        new = full
        for old, newv in pairs:
            if old and old in new:
                new = new.replace(old, newv)
        s = new.strip()
        # 签名行一律留白、手写：委托人 / 承接律师只留冒号，日期自动填写
        if s == "委托人：" or s == "委托人：{{client_names}}":
            new = "委托人："
        elif s == "承接律师：" or s == "承接律师：{{lawyer}}":
            new = "承接律师："
        elif _re.fullmatch(r"年\s+月\s+日", s):
            new = "{{date_str}}"
        if new != full:
            if not p.runs:
                p.add_run(new)
            else:
                p.runs[0].text = new
                for r in p.runs[1:]:
                    r.text = ""
            return True
        return False

    for p in doc.paragraphs:
        do_para(p)
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    do_para(p)
    for s in doc.sections:
        for p in list(s.header.paragraphs) + list(s.footer.paragraphs):
            do_para(p)

    def fill_cell(ri, ci, text):
        c = doc.tables[1].rows[ri].cells[ci]
        if c.text.strip():
            return
        if c.paragraphs[0].runs:
            c.paragraphs[0].runs[0].text = text
        else:
            c.paragraphs[0].add_run(text)

    fill_cell(0, 12, "{{client_ids}}")
    fill_cell(1, 3, "{{client_names}}  电话：{{client_phone}}")
    doc.save(str(DST_01))
    print("ok 01（基于转好文件，仅替换文字，版式不动）")


if __name__ == "__main__":
    build_01_contract()
    print("当前模板：", sorted(p.name for p in TPL.glob("*.docx")))
