#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""根据 berufe.json + zh_names.json 生成中文版职业 Markdown。"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BERUFE_JSON = ROOT / "data" / "berufe.json"
ZH_NAMES = ROOT / "data" / "zh_names.json"
OUT_DIR = ROOT / "berufe"
INDEX_MD = ROOT / "README.md"

ZUST_ZH = {
    "IH": "工商业（IHK）",
    "Hw": "手工业（HWK）",
    "Lw": "农业",
    "öD": "公共部门",
    "Hausw": "家政",
    "FB": "自由职业（相关行业协会）",
    "Seesch": "海运",
}

STRUCT_ZH = {
    "mono": "单一职业（无正式细分）",
    "schwerpunkt": "含重点方向（Schwerpunkt）",
    "fachrichtung": "含专业方向（Fachrichtung）",
    "wahlqualifikation": "含选修资格（Wahlqualifikation）",
    "zusatzqualifikation": "含附加资格（Zusatzqualifikation）",
    "einsatzgebiet": "含应用领域（Einsatzgebiet）",
    "gap": "采用分段结业考试（GAP）",
}

GROUP_ZH = {
    "11": "农牧林业职业",
    "12": "园艺与花艺",
    "21": "原料开采加工、玻璃与陶瓷",
    "22": "塑料与木材加工",
    "23": "造纸印刷与技术媒体设计",
    "24": "金属制造加工与金属结构",
    "25": "机械与车辆技术",
    "26": "机电、能源与电气",
    "27": "技术研发、设计与生产控制",
    "28": "纺织与皮革",
    "29": "食品制造与加工",
    "31": "建筑规划、建筑与测量",
    "32": "地上与地下建筑工程",
    "33": "室内装修类建筑职业",
    "34": "楼宇与供应技术",
    "41": "数理化生职业",
    "42": "地质地理与环保",
    "43": "信息技术与通信技术",
    "51": "交通与物流（不含驾驶）",
    "52": "车辆与运输设备驾驶",
    "53": "安保监控",
    "54": "清洁",
    "61": "采购销售与贸易",
    "62": "售卖",
    "63": "旅游酒店餐饮",
    "71": "企业管理与组织",
    "72": "金融、会计与税务",
    "73": "法律与行政",
    "81": "医疗健康",
    "82": "非医疗健康、美容康体与医疗技术",
    "83": "教育、社会家政与神学",
    "91": "语言人文社科与经济科学",
    "92": "广告营销与商业/编辑类媒体",
    "93": "艺术、手工艺术与设计",
    "94": "表演艺术与舞台技术",
}


INVALID = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
MULTI_SPACE = re.compile(r"\s+")


def short_de(name: str) -> str:
    return name.split("/")[0].strip()


def zh_of(name: str, mapping: dict[str, str]) -> str:
    key = short_de(name)
    return mapping.get(key, key)


def safe_part(text: str) -> str:
    t = text.strip()
    t = t.replace("/", "／").replace("\\", "＼")
    t = t.replace(":", "：").replace("*", "＊").replace("?", "？")
    t = t.replace('"', "“").replace("<", "＜").replace(">", "＞").replace("|", "｜")
    t = INVALID.sub("", t)
    t = MULTI_SPACE.sub(" ", t).strip(" .")
    return t


def make_filename(zh: str, de: str, used: dict[str, int]) -> str:
    fname = f"{safe_part(zh)}-{safe_part(de)}.md"
    if fname in used:
        used[fname] += 1
        return f"{fname[:-3]}-{used[fname]}.md"
    used[fname] = 1
    return fname


def zust_text(codes: list[str]) -> str:
    if not codes:
        return "见官方名录"
    return "；".join(ZUST_ZH.get(c, c) for c in codes)


def struct_text(types: list[str]) -> str:
    if not types:
        return "—"
    return "；".join(STRUCT_ZH.get(t, t) for t in types)


def group_text(groups: list[dict]) -> str:
    if not groups:
        return "未匹配到职业主组"
    parts = []
    for g in groups:
        code = g.get("code", "")
        de = g.get("name", "")
        zh = GROUP_ZH.get(code, de)
        parts.append(f"{code} {zh}" + (f"（{de}）" if de and zh != de else ""))
    return "；".join(parts)


def specs_md(specs: list[str]) -> str:
    if not specs:
        return "  - 无正式专业方向 / 重点方向（或为单一职业）"
    return "\n".join(f"  - {s}" for s in specs)


def related_md(names: list[str], mapping: dict[str, str]) -> str:
    if not names:
        return "- （同主组相关职业见索引）"
    lines = []
    for n in names:
        zh = zh_of(n, mapping)
        lines.append(f"- {zh}（{short_de(n)}）")
    return "\n".join(lines)


def berufenet_url(name: str) -> str:
    q = short_de(name).replace(" ", "%20")
    return f"https://web.arbeitsagentur.de/berufenet/ergebnisse?suchbegriff={q}"


def related_in_group(all_d: list[dict], d: dict, limit: int = 8) -> list[str]:
    if not d.get("groups"):
        return []
    codes = {g["code"] for g in d["groups"]}
    out = []
    for other in all_d:
        if other["nr"] == d["nr"]:
            continue
        if any(g.get("code") in codes for g in other.get("groups", [])):
            out.append(other["name"])
        if len(out) >= limit:
            break
    return out


def render(d: dict, mapping: dict[str, str], related: list[str]) -> str:
    de = d["name"]
    short = short_de(de)
    zh = zh_of(de, mapping)
    duration = (
        " / ".join(f"{m} 个月" for m in d.get("duration_months") or [])
        or "见培训条例（未解析到）"
    )
    dqr = " / ".join(d.get("dqr") or []) or "见 DQR 官方列表"
    azubi = (
        f"{d['azubi_2024']:,}".replace(",", ".")
        if d.get("azubi_2024") is not None
        else "无公开数字或未单独统计"
    )
    kldb = ", ".join(d.get("kldb") or []) or "—"
    legal = d.get("legal") or {}
    ao = legal.get("ausbildungsordnung") or "见系统目录法律依据"
    rlp = legal.get("rahmenlehrplan") or "见系统目录框架教学计划"
    legal_full = legal.get("legal_full") or "—"
    specs = d.get("specializations") or []

    return f"""# {zh}

**德语官方名称：** {de}

> 数据来源：德国联邦职业教育研究所（BIBB）《承认培训职业名录 2026》（截至 2025-10-01）  
> 官方出版物：<https://www.bibb.de/dienst/publikationen/de/21008>  
> 本页按「调查双元制职业」框架整理。**学制、主管机构、法规引用、在训人数等来自官方名录**；薪资与企业日常需另行核实。

## 元数据

| 字段 | 内容 |
| --- | --- |
| 名录编号 | {d['nr']} |
| 中文译名 | {zh} |
| 德语全称 | {de} |
| 检索简称 | {short} |
| 主管范围 | {zust_text(d.get('zust_codes') or [])} |
| 标准学制 | {duration} |
| DQR 等级 | {dqr} |
| KldB 2010 | {kldb} |
| 职业主组 | {group_text(d.get('groups') or [])} |
| 结构类型 | {struct_text(d.get('structure_types') or [])} |
| 在训人数（2024） | {azubi} |
| 文件名 | `{d.get('filename') or (d['slug'] + '.md')}` |

---

## 1. 官方定位

- **是否为国家承认的双元制职业**：是（依据《联邦职业教育法》BBiG / 《手工业条例》HwO）
- **主管考试机构方向**：{zust_text(d.get('zust_codes') or [])}
- **标准培训时长**：{duration}
- **德国资格框架（DQR）**：{dqr}
- **职业分类（KldB）**：{kldb}
- **结构类型**：{struct_text(d.get('structure_types') or [])}
- **细分方向**（原文保留德语，便于对照条例）：
{specs_md(specs)}

### 法律依据摘录

- **培训条例（Ausbildungsordnung）**：{ao}
- **框架教学计划（Rahmenlehrplan）**：{rlp}
- **原文合并字段**：{legal_full}

---

## 2. 学什么、怎么学

> 官方名录主要提供法规引用，不是完整技能清单。细节以培训条例中的培训框架计划 + 文教部长联席会议（KMK）框架教学计划为准。

- **学习地点**：企业（Betrieb）+ 职业学校（Berufsschule）；手工业常见跨企业培训课
- **已知细分 / 选修**：
{specs_md(specs)}
- **建议继续查阅**：
  - 完整培训条例与框架教学计划
  - 考试结构：期中考 / 结业考，或分段结业考试（GAP）
  - [德国联邦就业局 BERUFENET]({berufenet_url(de)})

---

## 3. 入学门槛

> 法律上通常**不强制**统一学历；实际门槛由企业招聘决定。

- **法定硬性学历**：一般无全国统一学历门槛（个别受管制行业另有规定）
- **企业常见要求**：主体中学 / 实科中学毕业，或文理高中毕业；相关实习加分
- **语言**：外籍申请者通常需职场德语（常见 B1–B2，视企业与签证而定）
- **其他**：健康证明、无犯罪记录等视职业而定（护理、食品、安保、驾驶类更常见）
- **待核实**：目标联邦州与目标企业近 12 个月招聘启事中的具体要求

---

## 4. 市场与钱

- **在训规模（BIBB 2024）**：{azubi}
- **培训津贴**：名录不含；请查所属劳资协议、当地工商会/手工业协会津贴统计，或 Ausbildung.de
- **结业起薪**：名录不含；对照结业后岗位招聘与劳资协议
- **供需**：在训人数仅反映规模，需结合空岗与竞争（联邦就业局、当地行业协会）

---

## 5. 企业侧现实

- **典型培训企业类型**：由主管范围暗示——工商业≈企业；手工业≈作坊/企业；农业≈农场；公共部门≈行政机关；自由职业≈事务所等
- **招聘信号**：企业是否具备培训资质、是否有合格培训师
- **工作现实（需一手核实）**：工时、轮班、体力、客户压力、出差——读招聘启事并尽量试工

---

## 6. 出路与天花板

- **结业证书**：按主管范围取得工商会 / 手工业协会结业证，或相应公共部门、自由职业结业证明
- **DQR 等级**：{dqr}（双元制结业多为 3 或 4 级）
- **常见进修方向**（需按职业核对）：
  - 师傅（Meister）/ 技术员（Techniker）/ 专业经营师（Fachwirt）等
  - 满足条件可衔接高校入学或相关专业学习
- **待核实**：是否强制师傅资格才能独立开业、是否有联邦统一进修条例

---

## 7. 相关职业对比

同职业主组内可优先对比：

{related_md(related, mapping)}

对比重点：学制、细分方向、主管协会、在训人数、结业后岗位是否重叠。

---

## 8. 一手验证清单

- [ ] 阅读完整**培训条例**（含培训框架计划）
- [ ] 阅读对应 **KMK 框架教学计划**
- [ ] 在 [BERUFENET]({berufenet_url(de)}) 核对职业描述
- [ ] 查看当地工商会 / 手工业协会页面与津贴信息
- [ ] 收集至少 10 条当前培训岗位招聘
- [ ] 收集至少 5 条结业后入门岗位招聘
- [ ] （可选）企业试工 / 体验日 / 与在训生交流

---

## 外部链接

- BIBB 名录 2026：<https://www.bibb.de/dienst/publikationen/de/21008>
- BERUFENET：<{berufenet_url(de)}>
- 德国资格框架 DQR：<https://www.dqr.de/>
- Make it in Germany：<https://www.make-it-in-germany.com/>

---

*由 `scripts/generate_zh_md.py` 生成。法规与统计如有出入，以 BIBB 官方 PDF / 联邦法律公报为准。中文译名为便于理解的常用译法，检索与签约请以德语官方名称为准。*
"""


def render_index(dossiers: list[dict], mapping: dict[str, str]) -> str:
    by_letter: dict[str, list[dict]] = defaultdict(list)
    for d in dossiers:
        letter = short_de(d["name"])[0].upper()
        letter = {"Ä": "A", "Ö": "O", "Ü": "U"}.get(letter, letter)
        by_letter[letter].append(d)

    lines = [
        "# 德国双元制承认培训职业资料库（中文版）",
        "",
        "> 基于德国联邦职业教育研究所（BIBB）《承认培训职业名录 **2026**》（截至 2025-10-01）整理。",
        f"> 共 **{len(dossiers)}** 个承认 / 视同承认的双元制培训职业。",
        "",
        "## 说明",
        "",
        "- 每个职业一份 Markdown，结构对应调查框架：官方定位 / 学什么 / 门槛 / 市场 / 企业 / 出路 / 相关职业 / 一手验证。",
        "- **已写入官方字段**：德语名称、中文译名、主管范围、学制、DQR、KldB、法律依据引用、结构类型、细分方向、2024 在训人数。",
        "- **名录不含**：具体薪资、企业日常、个人录取把握——见各职业页第 3–5、8 节继续核查。",
        "- **中文译名**便于阅读；申请、合同与考试请始终使用**德语官方名称**。",
        "- 结构化数据：`data/berufe.json`；译名表：`data/zh_names.json`。",
        "- 官方 PDF：<https://www.bibb.de/dienst/publikationen/de/21008>",
        "",
        "## 按字母索引（德语）",
        "",
    ]

    for letter in sorted(by_letter.keys()):
        lines.append(f"### {letter}")
        lines.append("")
        for d in by_letter[letter]:
            zh = zh_of(d["name"], mapping)
            dur = (
                "/".join(d.get("duration_months") or []) + "个月"
                if d.get("duration_months")
                else "?"
            )
            zust = ",".join(d.get("zust_codes") or []) or "?"
            fname = d.get("filename") or f"{d['slug']}.md"
            de = short_de(d["name"])
            href = f"berufe/{fname}"
            # Angle-bracket destinations keep spaces/parentheses clickable on GitHub.
            lines.append(
                f"- [{zh}](<{href}>) · [{de}](<{href}>) · {dur} · {zust} · #{d['nr']}"
            )
        lines.append("")

    lines.append("## 按职业主组")
    lines.append("")
    by_group: dict[str, list[dict]] = defaultdict(list)
    for d in dossiers:
        if d.get("groups"):
            g = d["groups"][0]
            code = g.get("code", "")
            title = f"{code} {GROUP_ZH.get(code, g.get('name', ''))}"
            by_group[title].append(d)
        else:
            by_group["未分组"].append(d)
    for gname in sorted(by_group.keys(), key=lambda x: (x.startswith("未"), x)):
        lines.append(f"### {gname}")
        lines.append("")
        for d in by_group[gname]:
            zh = zh_of(d["name"], mapping)
            fname = d.get("filename") or f"{d['slug']}.md"
            href = f"berufe/{fname}"
            lines.append(f"- [{zh}](<{href}>）（{short_de(d['name'])}）")
        lines.append("")

    lines.append("## 重新生成")
    lines.append("")
    lines.append("```bash")
    lines.append("python scripts/generate_zh_md.py")
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    dossiers = json.loads(BERUFE_JSON.read_text(encoding="utf-8"))
    mapping = json.loads(ZH_NAMES.read_text(encoding="utf-8"))

    missing = [short_de(d["name"]) for d in dossiers if short_de(d["name"]) not in mapping]
    if missing:
        print("WARNING missing translations:", len(missing))
        for m in missing[:20]:
            print(" ", m)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for old in OUT_DIR.glob("*.md"):
        old.unlink()

    used: dict[str, int] = {}
    for d in dossiers:
        zh = zh_of(d["name"], mapping)
        de = short_de(d["name"])
        fname = make_filename(zh, de, used)
        d["name_zh"] = zh
        d["filename"] = fname
        related = related_in_group(dossiers, d)
        md = render(d, mapping, related)
        (OUT_DIR / fname).write_text(md, encoding="utf-8")

    BERUFE_JSON.write_text(
        json.dumps(dossiers, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    INDEX_MD.write_text(render_index(dossiers, mapping), encoding="utf-8")
    print(f"Wrote {len(dossiers)} Chinese markdown files to {OUT_DIR}")
    print(f"Index: {INDEX_MD}")


if __name__ == "__main__":
    main()
