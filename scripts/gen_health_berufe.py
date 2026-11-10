# -*- coding: utf-8 -*-
"""Generate Gesundheitsfachberufe pages that pay Ausbildungsvergütung and allow self-application."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "berufe"


def netto(brutto: int) -> int:
    if brutto < 1600:
        return round(brutto * 0.79)
    if brutto < 3200:
        return round(brutto * 0.68)
    return round(brutto * 0.64)


def render(meta: dict) -> str:
    zh = meta["zh"]
    de_m = meta["de_m"]
    de_f = meta["de_f"]
    title_de = f"{de_m} / {de_f}"
    y1, y2, y3 = meta["verg"]
    entry_lo, entry_mid, entry_hi = meta["salary"]
    scale = meta["scale"]
    path = meta["path"]
    lines: list[str] = []
    a = lines.append

    a(f"# {zh}（{title_de}）")
    a("")
    a(f"> 调查基准：{meta['note_stats']}")
    a(
        "> 金额均为**月薪**；税后为单身、税级 I（Steuerklasse I）、无教会税、法定医保的近似估算，实际到手因联邦州、医保附加费率、有无子女而略有差异。"
    )
    a("> 文中人数若写作德语千分位写法（如 `59.400`），不是小数。")
    a("> 中文便于阅读；申请、合同、考试请以括号内**德语官方名称**为准。")
    a(
        "> **重要**：本页属卫生健康类学校教育职业（Gesundheitsfachberuf），法律路径与资料库主体「BBiG/HwO 双元制」不同，但同样可**自行向实践培训承担方申请**、签合同、拿**培训津贴（Ausbildungsvergütung）**，日常形态高度相似。"
    )
    a("> 第 1–9 节偏职业画像；找机构与生活账见第 10–12 节；第 13–14 节为核验与口径说明。")
    a("")
    a("---")
    a("")
    a("## 目录")
    a("")
    a("1. [一句话结论](#一句话结论)")
    a("2. [1. 职业是什么、学什么](#1-职业是什么学什么)")
    a("3. [2. 岗位规模、培训规模、通过率](#2-岗位规模培训规模通过率)")
    a("4. [3. 申请竞争难度](#3-申请竞争难度非-bbig-anr-口径)")
    a("5. [4. 培训期间到手工资](#4-培训期间到手工资ausbildungsvergütung)")
    a("6. [5. 毕业后税前 / 税后工资](#5-毕业后税前--税后工资)")
    a("7. [6. 职业发展路线](#6-职业发展路线能做什么考什么多少年)")
    a("8. [7. 值不值得读](#7-值不值得读综合判断)")
    a("9. [8. 为什么德国年轻人仍犹豫](#8-为什么德国年轻人仍犹豫纸面不错却招不满)")
    a("10. [9. 与相近职业对比](#9-与相近职业对比防选错)")
    a("11. [10. 怎么找机构与申请时间线](#10-怎么找机构与申请时间线)")
    a("12. [11. 培训日常节奏与考试节点](#11-培训日常节奏与考试节点)")
    a("13. [12. 培训期生活账](#12-培训期生活账到手够不够花)")
    a("14. [13. 一手交叉核验清单](#13-一手交叉核验清单防只看纸面)")
    a("15. [14. 信息来源与口径说明](#14-信息来源与口径说明无外链版)")
    a("")
    a("---")
    a("")
    a("## 一句话结论")
    a("")
    a(
        f"{zh}是国家承认的卫生健康类培训职业，官方名称 **{title_de}**，学制 **{meta['duration']} 个月**"
        f"（约 {meta['duration'] // 12} 年），资格框架约 **DQR {meta['dqr']}**。"
        f"{scale['one_liner']}年轻人常因**{meta['pain']}**犹豫。津贴与结业薪资见第 4–5 节。"
        f"**可自行申请**：向医院/护理机构/急救服务等实践培训承担方（Träger der praktischen Ausbildung）投递，签培训合同并领取津贴。"
    )
    a("")
    a("---")
    a("")
    a("## 1. 职业是什么、学什么")
    a("")
    a("| 项目 | 内容 |")
    a("| --- | --- |")
    a(f"| 官方名称 | {title_de} |")
    a(f"| 法律依据 | {meta['law']}；{meta['law_detail']} |")
    a("| 主管范围 | 卫生健康类学校教育（Gesundheitsfachberuf），**不是** BBiG/HwO 经典双元制 |")
    a(f"| 学制 | 通常 **{meta['duration']} 个月**；部分可部分时间制延长 |")
    a(f"| 资格等级 | 约 DQR **{meta['dqr']}**（以结业证书与州规定为准） |")
    a(f"| 学习形式 | {meta['form']} |")
    a(f"| 职业主组 | {meta['group']} |")
    a("")
    a("### 工作现实（签约前要想清楚）")
    a("")
    a(f"- **场景**：{meta['scene']}")
    a(f"- **典型任务**：{meta['tasks']}")
    a("- **体力 / 班次 / 客户压力**：常有轮班、夜班、节假日；情感劳动与责任重。结合第 8 节与试工/实习判断。")
    a("- **德语**：患者沟通、交接班、文件与安全指令，实务上多需 **B2**（部分机构硬性要求）。")
    a("- **学历**：常见为中等学历（约 10 年普通教育）或主体中学 + 至少两年职业培训/护理辅助前置；以招聘与学校招生条件为准。")
    a("- **健康与无犯罪证明**：通常需健康适宜证明（gesundheitliche Eignung）与无犯罪证明（Führungszeugnis）。")
    a("")
    a("### 职业学校 / 护理学校上什么课（主题粗览）")
    a("")
    a("| 序号 | 主题（中文） | 德语关键词 |")
    a("| --- | --- | --- |")
    for i, (zh_t, de_t) in enumerate(meta["curriculum"], 1):
        a(f"| {i} | {zh_t} | {de_t} |")
    a("")
    a("---")
    a("")
    a("## 2. 岗位规模、培训规模、通过率")
    a("")
    a("### 培训规模")
    a("")
    a("| 指标 | 数字 | 说明 |")
    a("| --- | --- | --- |")
    a(f"| 在训 / 库存 | **{scale['stock']}** | {scale['stock_note']} |")
    a(f"| 当年新签 / 入学 | **{scale['new']}** | {scale['new_note']} |")
    a(f"| 当年结业通过 | **{scale['grad']}** | {scale['grad_note']} |")
    a(f"| 性别结构粗感 | **{scale['gender']}** | 行业常见结构；急救岗男性占比通常更高 |")
    a("")
    a("### 中途退出与考试")
    a("")
    a(scale["pass_note"])
    a("")
    a("### 就业侧")
    a("")
    a(scale["job_note"])
    a("")
    a("---")
    a("")
    a("## 3. 申请竞争难度（非 BBiG ANR 口径）")
    a("")
    a(f"**总评：{meta['compete']}**")
    a("")
    a(
        "本职业**没有** BIBB Tabelle 59 那种 ANR 供需比。竞争看：**实践培训承担方是否招满、德语与健康门槛、是否完成规定实习（Praktikum）**。"
    )
    a("")
    a("| 读数要点 | 含义 |")
    a("| --- | --- |")
    a("| 行业缺人报道多 | 不等于「人人好进」；大医院/大城市仍挑人 |")
    a("| 实习与试工 | 手术室/护理/急救常要求事前实习，卡住一批申请人 |")
    a("| 德语 B2 | 外籍申请人实务硬门槛 |")
    a("| 班次接受度 | 书面愿意上夜班 ≠ 试工后仍愿意 |")
    a("")
    a("---")
    a("")
    a("## 4. 培训期间到手工资（Ausbildungsvergütung）")
    a("")
    a(
        "合同写的是**税前（brutto）**。下表以公共部门学徒劳资 **TVAöD Pflege**（约自 2025-04-01）为全国可核对的公开锚点；教会/私立集团可能接近或略有出入，**以书面合同为准**。"
    )
    a("")
    a("### 公共部门参考税前（TVAöD Pflege，约 2025-04）")
    a("")
    a("| 年级 | 税前月均（约） |")
    a("| --- | --- |")
    a(f"| 第 1 年 | **{y1} €** |")
    a(f"| 第 2 年 | **{y2} €** |")
    a(f"| 第 3 年 | **{y3} €** |")
    a("")
    a("### 税后到手（近似，税级 I）")
    a("")
    a("| 税前 | 约到手（netto） | 适用场景 |")
    a("| --- | --- | --- |")
    a(f"| {y1} € | **约 {netto(y1)} €** | 一年级参考 |")
    a(f"| {y2} € | **约 {netto(y2)} €** | 二年级参考 |")
    a(f"| {y3} € | **约 {netto(y3)} €** | 三年级参考 |")
    a("")
    a("另可能有：年终奖（Jahressonderzahlung）、结业奖金、交通/值班补贴——是否发放看劳资与机构，上表未计入。")
    a("")
    a("---")
    a("")
    a("## 5. 毕业后税前 / 税后工资")
    a("")
    a(
        "> 下列为**市场区间估算**（公共部门 TVöD/私立集团常见水平），用于建立数量级；同一职业东西部、班次、科室与劳资可差数百欧元。"
    )
    a("")
    a("| 口径 | 税前月薪 | 约税后（税级 I） |")
    a("| --- | --- | --- |")
    a(f"| 入门 / 偏低 | 约 **{entry_lo} €** | 约 **{netto(entry_lo)} €** |")
    a(f"| 常见中位附近 | 约 **{entry_mid} €** | 约 **{netto(entry_mid)} €** |")
    a(f"| 偏高 / 有经验 | 约 **{entry_hi} €** | 约 **{netto(entry_hi)} €** |")
    a(f"| 升阶后（专科/管理/教学） | 约 **{meta['salary_senior']}** | 随岗位波动 |")
    a("")
    a("**年薪粗算**：税前月薪 × 12；若有双薪/假期奖金，再加 0,5–1,5 个月。")
    a("")
    a("---")
    a("")
    a("## 6. 职业发展路线（能做什么、考什么、多少年）")
    a("")
    a("### 时间线示意")
    a("")
    a("| 阶段 | 大约时间 | 身份 / 证书 | 典型岗位 | 收入量级（税前/月） |")
    a("| --- | --- | --- | --- | --- |")
    a("| 0 | 培训期 | 在训生 / 卫生学校学员 | 跟班实践 | 见第 4 节 |")
    a(f"| 1 | 结业当年 | 国家承认结业 | {path[0]} | 约 {entry_lo}–{entry_mid} € |")
    a(f"| 2 | 结业后 1–3 年 | 有经验专员 | {path[1]} | 约 {entry_mid}–{entry_hi} € |")
    a(f"| 3 | 结业后 2–5 年+ | 专科/教学/协调 | {path[2]} | 约 {meta['salary_senior']} |")
    a("| 4 | 再往后 | 管理、高校路径、对口进修 | 部门协调或深造 | 波动大 |")
    a("")
    a("### 关键证书说明")
    a("")
    a("1. **国家结业考试**：通过后获职业执业资格相关结业（以本职业法律与州考试机构为准）。")
    a("2. **专科进修（Fachweiterbildung）**：重症、手术、急救、儿科、精神科等（视职业开放路径）。")
    a("3. **旁路**：部分可衔接护理/健康相关高校学士（含部分实践整合路径）。")
    a("")
    a("---")
    a("")
    a("## 7. 值不值得读（综合判断）")
    a("")
    a("| 维度 | 判断 |")
    a("| --- | --- |")
    a(f"| 好不好进 | {meta['verdict_enter']} |")
    a(f"| 好不好毕业 | {meta['verdict_grad']} |")
    a(f"| 培训期钱 | 一年级税前常见约 **{y1} €** 量级（公共部门锚点；以合同为准） |")
    a(f"| 毕业钱 | 税前常见约 **{entry_lo}–{entry_hi} €** 带 |")
    a("| 天花板 | 专科进修与管理岗可再高一截；不适合指望轻松坐班 |")
    a(f"| 适合谁 | {meta['fit']} |")
    a(f"| 不太适合谁 | {meta['unfit']} |")
    a("")
    a("---")
    a("")
    a("## 8. 为什么德国年轻人仍犹豫（纸面不错，却招不满）")
    a("")
    a(f"> 本节对齐行业缺人报道与学员/家长常见顾虑：{meta['pain']}。")
    a("")
    a(
        "听起来不错，通常是因为看到了**结果面**：有合同、有津贴、行业喊缺人、结业能就业。年轻人卡住的是**班次、身体与情感负荷、同学比较**。"
    )
    a("")
    a("### 为什么「纸面不错」，年轻人仍犹豫")
    a("")
    a(f"**1. 班次与责任**  \n{meta['pain']}——比「有没有饭碗」更影响志愿。")
    a("")
    a("**2. 家长期望与升学惯性**  \n部分家庭更推大学或「干净」办公岗；护理/急救/手术室形象常被低估。")
    a("")
    a(
        f"**3. 钱与体感**  \n培训期一年级约 **{y1} €** 税前已属卫生类偏高档；但结业后责任与班次对上工资后，仍常觉得「不值」。"
    )
    a("")
    a("**4. 信息不对称**  \n好机构靠实习才看得见；招人季与学生定方向时间错开。")
    a("")
    a("---")
    a("")
    a("## 9. 与相近职业对比（防选错）")
    a("")
    a("| 职业 | 德语 | 场景差异 | 体力/班次粗感 | 钱的粗感 |")
    a("| --- | --- | --- | --- | --- |")
    a(f"| {zh}（本职业） | {de_m} | 本表锚点 | 以实习为准 | 见第 4–5 节 |")
    for r in meta["related"]:
        a(f"| {r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]} |")
    a("")
    a("选职业时看**日常场景**是否符合预期，不要只看「好不好签合同」。")
    a("")
    a("---")
    a("")
    a("## 10. 怎么找机构与申请时间线")
    a("")
    a("### 去哪找（无外链，记渠道名）")
    a("")
    a(meta["apply"])
    a("")
    a("简历与邮件用德语；写明可到岗时间、德语级别、已完成/可安排的实习、是否接受轮班。")
    a("")
    a("### 建议时间线（常见春/秋开学）")
    a("")
    a("| 时间 | 做什么 |")
    a("| --- | --- |")
    a("| 开学前 **9–12 个月** | 德语冲到 B2；确定联邦州；联系 Träger + 学校 |")
    a("| 开学前 **6–9 个月** | 完成规定实习；试工；锁定意向机构 |")
    a("| 开学前 **3–6 个月** | 签合同、确认津贴与学校名额；准备健康证明与无犯罪证明 |")
    a("| 开学前 **1–3 个月** | 签证/租房缓冲（如适用）；确认排班与报道 |")
    a("")
    a("### 实习怎么用")
    a("")
    a("目标是双方确认你能否接受真实班次与场景。口头「可以」必须落到**书面培训合同**与津贴数字（对照第 4 节）。")
    a("")
    a("---")
    a("")
    a("## 11. 培训日常节奏与考试节点")
    a("")
    a("| 模块 | 典型情况 |")
    a("| --- | --- |")
    a("| 理论课 | 卫生学校 / 护理学校，常为集中授课块（Block） |")
    a("| 实践 | 在 Träger 及轮转机构；实践课时通常多于理论 |")
    a("| 工时与假期 | 青少年与成年规则不同；夜班/周末常见，看合同与劳资 |")
    a("")
    a("### 考试节点")
    a("")
    a(meta["exam"])
    a("")
    a("---")
    a("")
    a("## 12. 培训期生活账（到手够不够花）")
    a("")
    a(
        f"第 4 节到手是**收入起点**。一年级约 {netto(y1)} € 税后在小镇/合租更易打平；大城市仍可能紧张。"
    )
    a("")
    a("| 项目 | 较低成本地区 / 合租 | 高成本大城市 |")
    a("| --- | --- | --- |")
    a("| 房租+杂费 | 约 350–550 € | 约 550–900 €+ |")
    a("| 交通 | 约 50–100 € | 同左或更高 |")
    a("| 饮食+手机+日用 | 约 200–350 € | 约 250–400 € |")
    a("| **合计粗感** | 约 **650–1.000 €** | 约 **900–1.400 €+** |")
    a("")
    a("外籍建议在签合同前问清工作地邮编、是否协助找房，并自备数月缓冲金。")
    a("")
    a("---")
    a("")
    a("## 13. 一手交叉核验清单（防只看纸面）")
    a("")
    a(f"1. 用官方德语名 `{de_m}` 在就业局与 Ausbildung/医院招聘栏抽样近 20 条要求。")
    a("2. 完成该职业要求的实习天数，记录夜班/气味/压力是否可长期接受。")
    a("3. 合同对照第 4 节 TVAöD 锚点；长期含糊「以后再谈津贴」的慎重。")
    a("4. 确认合作学校名称、开课日期、是否已预留名额。")
    a("5. 核对德语证明、健康证明、无犯罪证明有效期。")
    a("6. 用工作地址查房租，拿预计 netto 估三个月现金流。")
    a("7. 若跨境赴德：提前核对签证类别是否覆盖此类卫生培训合同。")
    a("8. 对照第 8 节：若你卡在班次/情感劳动/血腥场景——解除或退学风险会落到你身上。")
    a("9. 问清结业后目标科室是否与培训轮转一致。")
    a("10. 数字口径：规模多取 Destatis/行业报道；津贴取 TVAöD 公开表；毕业薪资为区间估算。")
    a("")
    a("---")
    a("")
    a("## 14. 信息来源与口径说明（无外链版）")
    a("")
    a("- 法律与学制：各职业联邦法律（如 Pflegeberufegesetz、Notfallsanitätergesetz、ATA-OTA-G）及配套考试条例。")
    a("- 护理规模：联邦统计局（Destatis）护理培训统计（如 2024 新签约约 59.400、在训约 146.700、结业约 37.400）。")
    a(
        "- 培训津贴：公共部门 TVAöD Pflege 学徒表（约 2025-04 起：一年级约 1.416 €、二年级约 1.477 €、三年级约 1.578 €）。"
    )
    a("- 结业后市场薪资：就业市场常见区间与公共/私立医院招聘粗感（非个人报价）。")
    a("- 申请流程：向 Träger der praktischen Ausbildung 自申 + 合作卫生学校上课，为行业通行做法。")
    a("")
    a(
        "本页**刻意标注**其不属于 BBiG 经典双元制，以免与资料库其余职业混口径。阅读时勿把 ANR/DAZUBI 指标直接套用到本职业。"
    )
    a("")
    a("---")
    a("")
    a(
        "*本文按项目调查框架整理：含规模、申请、培训期到手、毕业税前税后、发展路线、具体金额、年轻人犹豫原因；全文中文并标注德语专名。*"
    )
    a("")
    return "\n".join(lines)


JOBS = [
    {
        "fname": "护理专员-Pflegefachmann.md",
        "zh": "护理专员",
        "de_m": "Pflegefachmann",
        "de_f": "Pflegefachfrau",
        "law": "《护理职业法》（Pflegeberufegesetz，PflBG）",
        "law_detail": "配套《护理职业培训与考试条例》（PflAPrV）",
        "duration": 36,
        "dqr": 4,
        "form": "护理学校（Pflegeschule）理论课 + 实践培训承担方（医院/养老/居家护理）及轮转实习；理论约 2.100 学时、实践约 2.500 学时",
        "group": "Gesundheits- und Pflegeberufe（卫生护理）",
        "note_stats": "本职业不属 BBiG/HwO 经典双元制 DAZUBI 口径；规模取 Destatis 护理培训统计 2024；津贴取公共部门 TVAöD Pflege（约 2025-04）。",
        "pain": "轮班夜班、情感劳动重、责任大与身体负荷",
        "scene": "医院病房、养老院、居家护理等，护理各年龄段患者",
        "tasks": "基础与专科护理、用药与观察、文档交接、患者与家属沟通、急救配合",
        "curriculum": [
            ("护理过程与沟通", "Pflegeprozess und Kommunikation"),
            ("解剖生理与疾病学基础", "Anatomie, Physiologie, Krankheitslehre"),
            ("药物与安全", "Pharmakologie und Patientensicherheit"),
            ("急危重症与急救基础", "Notfall und Intensivgrundlagen"),
            ("儿科/老年/精神科轮转主题", "Pädiatrie, Geriatrie, Psychiatrie"),
            ("法律、伦理与专业身份", "Recht, Ethik, Berufsrolle"),
        ],
        "scale": {
            "one_liner": "2024 年新签培训合同约 **59.400**，年末在训约 **146.700**，当年成功结业约 **37.400**。",
            "stock": "约 146.700 人",
            "stock_note": "Destatis 2024，各年级叠加",
            "new": "约 59.400 份",
            "new_note": "较 2023 约 +9%",
            "grad": "约 37.400 人",
            "grad_note": "通用护理结业占绝大多数",
            "gender": "女性约七成以上",
            "pass_note": "官方公开「解除率/考试成功率」口径与 BBiG 不同；实务上前两年因班次与压力退出并不少见，签约前务必实习。",
            "job_note": "结业后进入医院、养老、居家护理；行业持续缺人，但夜班与责任仍是留人关键。",
        },
        "compete": "整体机会多，但好医院/大城市仍挑德语、实习与抗压表现",
        "verg": (1416, 1477, 1578),
        "salary": (2800, 3400, 4200),
        "salary_senior": "4.500–5.800 €",
        "path": ["病房/居家护理专员", "责任护士/专科方向", "护理管理或教学"],
        "verdict_enter": "相对好找 Träger；硬门槛在德语、健康与实习",
        "verdict_grad": "能坚持轮转与考试者多数能过；真正难的是班次适应",
        "fit": "愿意轮班、能做身体护理与情绪劳动、想尽快就业",
        "unfit": "只想白天坐班、怕血/排泄物/冲突场景、德语听力不够的人",
        "related": [
            ("医疗助理", "Medizinischer Fachangestellter", "诊所行政+辅助，偏门诊", "较少夜班", "见 MFA 专页"),
            ("手术技术助理", "Operationstechnischer Assistent", "手术室无菌配合", "班次重", "津贴锚点接近"),
            ("急救卫生员", "Notfallsanitäter", "院前急救", "出车压力大", "津贴锚点接近"),
            ("麻醉技术助理", "Anästhesietechnischer Assistent", "麻醉配合与苏醒", "手术室节奏", "津贴锚点接近"),
        ],
        "apply": "- 医院、养老院、居家护理服务的「Ausbildung Pflegefachmann/-frau」招聘\n"
        "- 联邦就业局培训/就业市场栏；关键词用官方德语名\n"
        "- 护理学校招生页（有的代招，合同仍与 Träger 签）\n"
        "- 教会与公益集团（Caritas、Diakonie 等）培训广告",
        "exam": "1. **中期/过程考核**：培训中段有中间考试或过程评估。  \n"
        "2. **国家结业考试**：笔试、口试与实践考试；通过后获 Pflegefachmann/-frau 结业。",
    },
    {
        "fname": "急救卫生员-Notfallsanitäter.md",
        "zh": "急救卫生员",
        "de_m": "Notfallsanitäter",
        "de_f": "Notfallsanitäterin",
        "law": "《急救卫生员职业法》（Notfallsanitätergesetz，NotSanG）",
        "law_detail": "配套考试条例（NotSan-APrV）",
        "duration": 36,
        "dqr": 4,
        "form": "急救学校理论 + 急救服务/医院实践培训承担方；理论与实践交替，实践占大部分",
        "group": "Rettungsdienst / Notfallmedizin（急救与急诊）",
        "note_stats": "本职业不属 BBiG/HwO 经典双元制 DAZUBI 口径；津贴取公共部门 TVAöD Pflege（约 2025-04）；规模为行业报道量级（各州急救服务分散，无统一 DAZUBI 表）。",
        "pain": "出车高压、倒班、目击创伤与责任边界",
        "scene": "救护车、急救站、急诊衔接；院前急救为主",
        "tasks": "伤病评估、生命支持、药物与器械辅助、转运与交接、文书与团队沟通",
        "curriculum": [
            ("急救医学与解剖生理", "Notfallmedizin, Anatomie"),
            ("气道与循环支持", "Atemwegs- und Kreislaufmanagement"),
            ("创伤与内科急症", "Trauma und Innere Notfälle"),
            ("药理与急救算法", "Pharmakologie und Algorithmen"),
            ("法规与团队资源管理", "Recht und CRM"),
            ("医院急诊轮转主题", "Klinikpraktika Notaufnahme"),
        ],
        "scale": {
            "one_liner": "全国在训与岗位由各州急救服务分摊，公开统一库存不如护理；但行业长期报缺，招录持续进行。",
            "stock": "分州分散，全国无单一公开库存表",
            "stock_note": "以各州急救服务/学校招生为准",
            "new": "持续招生（春/秋常见）",
            "new_note": "看 Träger 配额",
            "grad": "以学校与州考试结果为准",
            "grad_note": "无全国单一公开结业人数表（本页不编造）",
            "gender": "男性占比相对护理更高",
            "pass_note": "考试含理论与实践技能；真正筛掉人的是出车压力、驾驶/轮班与场景耐受。",
            "job_note": "结业后进入急救服务、部分医院急诊相关岗；加班与节日班常见。",
        },
        "compete": "有缺人，但要求实习、抗压与（常）驾照/倒班接受度，不等于低门槛",
        "verg": (1416, 1477, 1578),
        "salary": (2500, 3200, 4000),
        "salary_senior": "4.200–5.200 €",
        "path": ["急救车上岗", "资深急救/带教", "急救管理或对口进修"],
        "verdict_enter": "有岗位，但实习与抗压筛选硬",
        "verdict_grad": "技能考试严；坚持到考的人多数能过",
        "fit": "喜欢行动导向、能处理突发、接受倒班",
        "unfit": "晕血、怕冲突场面、不能接受不规律作息的人",
        "related": [
            ("护理专员", "Pflegefachmann", "病房/居家护理", "班次重", "津贴锚点接近"),
            ("麻醉技术助理", "Anästhesietechnischer Assistent", "院内麻醉配合", "手术室", "津贴锚点接近"),
            ("医疗助理", "Medizinischer Fachangestellter", "诊所辅助", "较少出车", "见 MFA 专页"),
        ],
        "apply": "- 红十字会、工人撒玛利亚联合会、地方急救服务（Rettungsdienst）Ausbildung 招聘\n"
        "- 医院急救学校合作项目\n"
        "- 就业局与各州急救主管部门培训信息\n"
        "- 关键词：`Notfallsanitäter Ausbildung`",
        "exam": "1. **过程评估与技能考核**：贯穿三年。  \n"
        "2. **国家结业考试**：理论 + 实践；通过后获 Notfallsanitäter/-in 资格。",
    },
    {
        "fname": "手术技术助理-Operationstechnischer Assistent.md",
        "zh": "手术技术助理",
        "de_m": "Operationstechnischer Assistent",
        "de_f": "Operationstechnische Assistentin",
        "law": "《麻醉与手术技术助理法》（ATA-OTA-G）",
        "law_detail": "配套 ATA-OTA 培训与考试条例（ATA-OTA-APrV）",
        "duration": 36,
        "dqr": 4,
        "form": "卫生学校理论约 2.100 学时 + 医院手术相关实践约 2.500 学时（Block 交替）",
        "group": "OP-Funktionsdienst（手术功能服务）",
        "note_stats": "本职业不属 BBiG/HwO 经典双元制 DAZUBI 口径；津贴取公共部门 TVAöD Pflege（约 2025-04）；规模因医院配额分散，本页给津贴与申请口径，不编造全国库存。",
        "pain": "长时间站立、无菌高压、手术室封闭环境与班次",
        "scene": "手术室、介入/功能区；术前术后准备与术中配合",
        "tasks": "手术间准备、无菌台、器械传递、患者转运配合、器械与耗材管理",
        "curriculum": [
            ("无菌与感染防护", "Asepsis und Hygiene"),
            ("手术器械与流程", "Instrumentenkunde und OP-Ablauf"),
            ("解剖与手术专科", "Anatomie und Fachdisziplinen"),
            ("患者安全与文档", "Patientensicherheit und Dokumentation"),
            ("法律与职业角色", "Recht und Berufsrolle"),
            ("多专科轮转实践", "Praktika in OP-Bereichen"),
        ],
        "scale": {
            "one_liner": "岗位集中在有手术量的医院；公开全国统一在训表有限，招录以医院配额为主。",
            "stock": "医院配额制，无单一全国公开库存",
            "stock_note": "以各医院/学校招生为准",
            "new": "每年多轮开学（如 3/4 月、9/10 月）",
            "new_note": "看 Träger",
            "grad": "以学校与州考试为准",
            "grad_note": "本页不编造全国结业人数",
            "gender": "女性占多数，但男性也不少见",
            "pass_note": "常见硬门槛是**至少约 2 周手术室实习**；适应不了封闭与站立节奏者中途退出风险高。",
            "job_note": "结业后主要在医院手术室；专科手术中心需求稳定。",
        },
        "compete": "名额少于护理，但缺人；实习表现与抗压是关键",
        "verg": (1416, 1477, 1578),
        "salary": (2700, 3300, 4100),
        "salary_senior": "4.400–5.500 €",
        "path": ["手术室上岗", "专科手术组骨干", "带教或手术室协调"],
        "verdict_enter": "有缺人，但实习与名额限制明显",
        "verdict_grad": "理论+实践考试；站立与无菌纪律是日常筛选",
        "fit": "细心、能长时间站立、接受手术室节奏",
        "unfit": "晕血、不能站久、排斥封闭空间的人",
        "related": [
            ("麻醉技术助理", "Anästhesietechnischer Assistent", "麻醉侧配合", "同手术团队", "津贴同档"),
            ("护理专员", "Pflegefachmann", "病房护理", "接触面更广", "津贴同档"),
            ("医疗助理", "Medizinischer Fachangestellter", "诊所", "非手术室", "见 MFA 专页"),
        ],
        "apply": "- 医院「OTA Ausbildung」招聘与卫生学校合作项目\n"
        "- 大学医院/大型集团职业培训页\n"
        "- 就业局关键词：`Operationstechnischer Assistent` / `OTA`\n"
        "- 先预约手术室实习再投递更有效",
        "exam": "1. **过程成绩与实践评估**。  \n"
        "2. **国家结业考试**（笔试/口试/实践）：通过后获 OTA 结业。",
    },
    {
        "fname": "麻醉技术助理-Anästhesietechnischer Assistent.md",
        "zh": "麻醉技术助理",
        "de_m": "Anästhesietechnischer Assistent",
        "de_f": "Anästhesietechnische Assistentin",
        "law": "《麻醉与手术技术助理法》（ATA-OTA-G）",
        "law_detail": "配套 ATA-OTA 培训与考试条例（ATA-OTA-APrV）",
        "duration": 36,
        "dqr": 4,
        "form": "卫生学校理论约 2.100 学时 + 医院麻醉/苏醒等相关实践约 2.500 学时",
        "group": "Anästhesie-Funktionsdienst（麻醉功能服务）",
        "note_stats": "本职业不属 BBiG/HwO 经典双元制 DAZUBI 口径；津贴取公共部门 TVAöD Pflege（约 2025-04）；规模以医院配额为主。",
        "pain": "高责任监护、手术室压力、班次与突发情况",
        "scene": "麻醉准备、术中协助、苏醒室；与麻醉医师及手术团队协作",
        "tasks": "麻醉工作站准备、术中协助与监测配合、苏醒观察辅助、设备与耗材管理",
        "curriculum": [
            ("麻醉程序与监测", "Anästhesieverfahren und Monitoring"),
            ("气道管理基础", "Atemwegsmanagement"),
            ("药理与急症反应", "Pharmakologie und Notfälle"),
            ("苏醒与转运", "Aufwachraum und Verlegung"),
            ("无菌、安全与文档", "Hygiene, Sicherheit, Dokumentation"),
            ("手术麻醉轮转实践", "Praktika Anästhesie/OP"),
        ],
        "scale": {
            "one_liner": "与 OTA 同属医院功能服务培训，名额随手术麻醉需求配置。",
            "stock": "医院配额制，无单一全国公开库存",
            "stock_note": "以各医院/学校招生为准",
            "new": "每年多轮开学",
            "new_note": "看 Träger",
            "grad": "以学校与州考试为准",
            "grad_note": "本页不编造全国结业人数",
            "gender": "女性占多数",
            "pass_note": "常要求麻醉/手术相关实习；对突发与监护压力耐受不足者风险高。",
            "job_note": "结业后在医院麻醉科、手术麻醉团队；需求随手术量波动但总体稳定。",
        },
        "compete": "名额有限但缺人；实习与细心度是筛选点",
        "verg": (1416, 1477, 1578),
        "salary": (2700, 3300, 4100),
        "salary_senior": "4.400–5.500 €",
        "path": ["麻醉团队上岗", "专科麻醉/苏醒骨干", "带教或功能服务协调"],
        "verdict_enter": "有机会，但比护理更「名额制」",
        "verdict_grad": "考试严；日常筛选是责任与专注",
        "fit": "细心冷静、能配合团队、接受手术室班次",
        "unfit": "抗压差、不能接受封闭手术环境的人",
        "related": [
            ("手术技术助理", "Operationstechnischer Assistent", "器械无菌侧", "同台协作", "津贴同档"),
            ("急救卫生员", "Notfallsanitäter", "院前急救", "出车导向", "津贴同档"),
            ("护理专员", "Pflegefachmann", "病房护理", "场景更广", "津贴同档"),
        ],
        "apply": "- 医院「ATA Ausbildung」招聘\n"
        "- 与 OTA 常同一卫生学校招生窗口\n"
        "- 就业局关键词：`Anästhesietechnischer Assistent` / `ATA`\n"
        "- 先做麻醉/手术实习再申请",
        "exam": "1. **过程成绩与实践评估**。  \n"
        "2. **国家结业考试**：通过后获 ATA 结业。",
    },
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for job in JOBS:
        path = OUT / job["fname"]
        path.write_text(render(job), encoding="utf-8")
        print("wrote", path.name, path.stat().st_size)


if __name__ == "__main__":
    main()
