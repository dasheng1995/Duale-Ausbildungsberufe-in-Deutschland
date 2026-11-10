# -*- coding: utf-8 -*-
"""Inject Berufsschule curriculum section into all berufe/*.md files."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BERUFE_DIR = ROOT / "berufe"
DATA = ROOT / "data" / "berufe.json"

MARKER_START = "<!-- curriculum:start -->"
MARKER_END = "<!-- curriculum:end -->"

GENERAL_TABLE = """| 中文 | 德语常见名称 | 学什么 |
| --- | --- | --- |
| 德语 / 沟通 | Deutsch / Kommunikation | 报告、客户沟通、安全指令理解、书面表达 |
| 英语 | Englisch | 专业词汇、简单技术/商务沟通（部分州低年级为主） |
| 经济与社会常识 | Wirtschafts- und Sozialkunde（Wiso） | 劳动合同、社保、劳资、企业经济；**结业常单考** |
| 政治 / 共同体常识 | Politik / Gemeinschaftskunde | 民主制度、社会议题（州课表名称不一） |
| 体育 | Sport | 健康与负荷；部分州中高年级开设 |
| 宗教或伦理 | Religion / Ethik | 部分州必修或选修 |"""

# Group -> list of (zh, de) Lernfeld-style themes
GROUP_THEMES: dict[str, list[tuple[str, str]]] = {
    "Mechatronik-, Energie- und Elektroberufe": [
        ("分析电气/电子系统并排查故障", "Elektrotechnische Systeme analysieren und Fehler beheben"),
        ("规划与安装电气系统", "Elektrische Systeme planen und installieren"),
        ("分析并实现控制与调节", "Steuerungen und Regelungen analysieren und realisieren"),
        ("提供与配置信息技术系统", "Informationstechnische Systeme bereitstellen"),
        ("电能供给与电气安全", "Elektroenergieversorgung und Sicherheit"),
        ("能源转换 / 设备与系统投运", "Energiewandlung / Geräte und Systeme in Betrieb nehmen"),
        ("自动化或楼宇系统（按方向）", "Automatisierung / Gebäude- und Infrastruktursysteme"),
        ("维护、文档与优化", "Instandhaltung, Dokumentation und Optimierung"),
    ],
    "Maschinen- und Fahrzeugtechnikberufe": [
        ("分析车辆/机械系统结构与功能", "Fahrzeuge und Maschinen analysieren"),
        ("维护保养与检查", "Wartung und Inspektion"),
        ("故障诊断与修理", "Fehlerdiagnose und Instandsetzung"),
        ("机电一体 / 控制与传感器", "Mechatronik, Steuerung und Sensorik"),
        ("液压气动与驱动技术", "Hydraulik, Pneumatik und Antriebstechnik"),
        ("总装、试车与交付客户", "Montage, Inbetriebnahme und Kundenübergabe"),
        ("维修文档与质量保证", "Dokumentation und Qualitätssicherung"),
    ],
    "Gebäude- und versorgungstechnische Berufe": [
        ("识读图纸与施工准备", "Pläne lesen und Baustelle vorbereiten"),
        ("管道、管网与连接技术", "Rohrleitungen und Verbindungstechnik"),
        ("卫生 / 供暖 / 通风空调系统（按方向）", "Sanitär-, Heizungs-, Lüftungs- und Klimatechnik"),
        ("测量、调节与控制技术", "Mess-, Steuer- und Regelungstechnik"),
        ("投运、维护与故障排除", "Inbetriebnahme, Wartung und Störungsbeseitigung"),
        ("能效、可再生与环保要求", "Energieeffizienz und Umweltschutz"),
        ("客户沟通、文档与验收", "Kundenkommunikation und Dokumentation"),
    ],
    "Hoch- und Tiefbauberufe": [
        ("工地安全与施工准备", "Baustelleneinrichtung und Arbeitsschutz"),
        ("识图、放样与测量", "Pläne lesen, Abstecken und Vermessen"),
        ("土方、地基与结构施工（按工种）", "Erd-, Gründungs- und Rohbauarbeiten"),
        ("混凝土、砌体、沥青或钢轨等专业工艺", "Beton, Mauerwerk, Asphalt, Gleis o. Ä."),
        ("材料、机械与辅材使用", "Baustoffe und Baumaschinen"),
        ("质量检查、文档与交接", "Qualitätssicherung und Übergabe"),
        ("环保与现场组织", "Umweltschutz und Baustellenorganisation"),
    ],
    "(Innen-)Ausbauberufe": [
        ("工地准备与劳动保护", "Baustellenvorbereitung und Arbeitsschutz"),
        ("识图与材料计算", "Pläne lesen und Materialbedarf ermitteln"),
        ("隔墙、地面、抹灰、油漆等专业工艺（按工种）", "Ausbautechniken je nach Beruf"),
        ("保温、隔声、防火相关构造", "Wärme-, Schall- und Brandschutz"),
        ("表面处理与修补", "Oberflächenbehandlung und Nacharbeiten"),
        ("质量验收与客户交接", "Abnahme und Kundenübergabe"),
    ],
    "Metallerzeugung und -bearbeitung, Metallbauberufe": [
        ("识图与技术文件", "Technische Zeichnungen und Unterlagen"),
        ("材料知识与热处理基础", "Werkstoffe und Wärmebehandlung"),
        ("切削、成型、焊接或装配（按工种）", "Zerspanen, Umformen, Schweißen, Montieren"),
        ("测量技术与质量检验", "Messtechnik und Qualitätsprüfung"),
        ("机床/设备操作与程序基础", "Maschinenbedienung und Programmierung"),
        ("劳动安全与环保", "Arbeitssicherheit und Umweltschutz"),
        ("维护与文档", "Instandhaltung und Dokumentation"),
    ],
    "Land-, Tier- und Forstwirtschaftsberufe": [
        ("动植物/森林作为劳动对象", "Tiere, Pflanzen oder Wald als Arbeitsgegenstand"),
        ("场地、土壤或生境调查", "Standort- und Bestandsaufnahme"),
        ("饲养、栽培或营林技术", "Haltung, Kultur oder Waldbewirtschaftung"),
        ("机械、工具与安全操作", "Maschinen, Geräte und Arbeitssicherheit"),
        ("植保/防疫/自然保护相关规范", "Pflanzenschutz, Tiergesundheit, Naturschutz"),
        ("产品与服务营销或公共任务", "Vermarktung oder öffentliche Aufgaben"),
        ("经营与工作组织", "Betriebs- und Arbeitsorganisation"),
    ],
    "Gartenbauberufe und Floristik": [
        ("认识植物及其立地", "Pflanzen und Standorte erfassen"),
        ("土壤/基质与场地准备", "Böden, Substrate und Standortvorbereitung"),
        ("栽培、养护或花艺制作", "Kultur, Pflege oder floristische Gestaltung"),
        ("机械、工具与劳动保护", "Maschinen, Geräte und Arbeitsschutz"),
        ("病虫害与植物保护基础", "Pflanzenschutz"),
        ("产品展示与客户服务", "Vermarktung und Kundenberatung"),
        ("方向深化（园林施工/温室等）", "Fachrichtungsbezogene Vertiefung"),
    ],
    "Führer/-innen von Fahrzeug- und Transportgeräten": [
        ("交通法规与行车安全", "Straßenverkehrsrecht und Fahrsicherheit"),
        ("车辆技术与日常检查", "Fahrzeugtechnik und Kontrolle"),
        ("货物固定与装卸", "Ladungssicherung und Umschlag"),
        ("线路规划与时间管理", "Tourenplanung und Zeitmanagement"),
        ("危货/特殊货物规则（若适用）", "Gefahrgut / Spezialtransporte"),
        ("客户沟通与运输单据", "Kundenkommunikation und Frachtpapiere"),
        ("经济驾驶与企业组织", "Wirtschaftliches Fahren und Betriebsabläufe"),
    ],
    "Verkehrs- und Logistikberufe (außer Fahrzeugführung)": [
        ("物流流程与供应链基础", "Logistikprozesse und Lieferketten"),
        ("仓储收发与库存", "Wareneingang, Lagerung, Kommissionierung"),
        ("运输组织与单据", "Transportorganisation und Dokumente"),
        ("信息技术与仓储系统", "IT- und Lagersysteme"),
        ("危险品与安全规范", "Gefahrstoffe und Arbeitssicherheit"),
        ("质量、成本与客户服务", "Qualität, Kosten und Kundenservice"),
        ("外贸/口岸/铁路等方向模块（按职业）", "Spezialmodule je nach Beruf"),
    ],
    "Informatik-, Informations- und Kommunikationstechnologieberufe": [
        ("分析与规划 IT 系统", "IT-Systeme analysieren und planen"),
        ("安装、配置与管理软硬件", "Hard- und Software installieren und administrieren"),
        ("网络与安全基础", "Netzwerke und IT-Sicherheit"),
        ("编程 / 应用开发或系统集成（按方向）", "Programmieren / Systemintegration"),
        ("故障排除与用户支持", "Störungsbeseitigung und Support"),
        ("项目工作与文档", "Projektarbeit und Dokumentation"),
        ("数据保护与质量保证", "Datenschutz und Qualitätssicherung"),
    ],
    "Berufe in Recht und Verwaltung": [
        ("公法/私法基础与行政程序", "Rechtliche Grundlagen und Verwaltungsverfahren"),
        ("公文、档案与办公软件", "Schriftverkehr, Akten und Office-Anwendungen"),
        ("公民/客户接待与咨询", "Bürger- und Kundenberatung"),
        ("财务管理与预算基础", "Haushalts- und Finanzwesen"),
        ("组织与项目管理", "Organisation und Projektarbeit"),
        ("数据保护与信息安全", "Datenschutz und Informationssicherheit"),
        ("专业法领域深化（按机关）", "Fachrechtliche Vertiefung"),
    ],
    "Berufe in Finanzdienstleistungen, Rechnungswesen und Steuerberatung": [
        ("簿记与会计基础", "Buchführung und Rechnungswesen"),
        ("税法与申报流程", "Steuerrecht und Deklaration"),
        ("财务报表与成本核算", "Jahresabschluss und Kostenrechnung"),
        ("客户咨询与沟通", "Mandantenberatung"),
        ("办公组织与软件", "Büroorganisation und Software"),
        ("商法/民法相关要点", "Handels- und Zivilrecht"),
        ("数据保护与职业伦理", "Datenschutz und Berufsethik"),
    ],
    "Berufe in Unternehmensführung und -organisation": [
        ("企业管理与流程组织", "Unternehmensorganisation und Prozesse"),
        ("人事与劳动合同基础", "Personalwesen"),
        ("会计与控制入门", "Rechnungswesen und Controlling"),
        ("采购、销售或项目支持", "Einkauf, Vertrieb oder Projektassistenz"),
        ("商务沟通与会议组织", "Kommunikation und Meetingorganisation"),
        ("数字化办公与数据保护", "Digitale Tools und Datenschutz"),
    ],
    "Einkaufs-, Vertriebs- und Handelsberufe": [
        ("采购/销售流程", "Einkaufs- und Vertriebsprozesse"),
        ("商品与市场知识", "Waren- und Marktkenntnisse"),
        ("询价、谈判与合同", "Angebote, Verhandlung und Verträge"),
        ("仓储物流衔接", "Schnittstelle Lager und Logistik"),
        ("客户关系与售后", "Kundenbeziehung und After-Sales"),
        ("成本、价格与指标", "Kosten, Preise und Kennzahlen"),
        ("外贸与支付（若适用）", "Außenhandel und Zahlungsbedingungen"),
    ],
    "Verkaufsberufe": [
        ("商品与服务知识", "Waren- und Dienstleistungskenntnisse"),
        ("接待客户与销售对话", "Kundenberatung und Verkaufsgespräch"),
        ("收银、支付与投诉处理", "Kasse, Zahlung und Reklamation"),
        ("陈列、库存与补货", "Warenpräsentation und Bestand"),
        ("营销活动与促销", "Marketing und Verkaufsförderung"),
        ("劳动保护与卫生", "Arbeitsschutz und Hygiene"),
        ("企业经济基础", "Betriebswirtschaftliche Grundlagen"),
    ],
    "Tourismus-, Hotel- und Gaststättenberufe": [
        ("接待与预订流程", "Rezeption und Reservierung"),
        ("客房/餐饮服务标准", "Housekeeping / Food and Beverage"),
        ("旅游产品与目的地知识", "Reiseprodukte und Destinationen"),
        ("销售、咨询与投诉", "Verkauf, Beratung und Beschwerden"),
        ("卫生、安全与法规", "Hygiene, Sicherheit und Recht"),
        ("成本核算与企业组织", "Kalkulation und Betriebsorganisation"),
        ("外语与跨文化沟通", "Fremdsprachen und interkulturelle Kommunikation"),
    ],
    "Lebensmittelherstellung und -verarbeitung": [
        ("原料特性与质量", "Rohstoffe und Qualität"),
        ("配方、工艺与生产流程", "Rezepturen und Produktionsverfahren"),
        ("卫生、HACCP 与食品安全", "Hygiene und Lebensmittelsicherheit"),
        ("设备操作与清洁", "Anlagenbedienung und Reinigung"),
        ("包装、储存与物流衔接", "Verpackung und Lagerung"),
        ("感官评价与检验", "Sensorik und Prüfung"),
        ("成本与可持续生产", "Kosten und Nachhaltigkeit"),
    ],
    "Mathematik-, Biologie-, Chemie- und Physikberufe": [
        ("实验室安全与规范操作", "Laborsicherheit und gute Laborpraxis"),
        ("采样、制备与分析", "Probenahme, Vorbereitung und Analyse"),
        ("测量仪器与数据分析", "Messgeräte und Datenauswertung"),
        ("化学/生物/物理方法（按职业）", "Chemische, biologische oder physikalische Verfahren"),
        ("质量保证与文档", "Qualitätssicherung und Dokumentation"),
        ("环保与废弃物处理", "Umweltschutz und Entsorgung"),
        ("生产或研发衔接", "Schnittstelle Produktion / Forschung"),
    ],
    "Medizinische Gesundheitsberufe": [
        ("解剖生理与疾病基础", "Anatomie, Physiologie und Krankheitslehre"),
        ("检查辅助与治疗配合", "Untersuchungs- und Behandlungsassistenz"),
        ("卫生、感染防护与急救", "Hygiene, Infektionsschutz und Erste Hilfe"),
        ("患者沟通与文档", "Patientenkommunikation und Dokumentation"),
        ("器械、材料与药品管理", "Instrumente, Materialien und Arzneimittel"),
        ("账单/保险基础（助理类）", "Abrechnung und Versicherung"),
        ("数据保护与职业伦理", "Datenschutz und Berufsethik"),
    ],
    "Nichtmedizinische Gesundheits-, Körperpflege- und Wellnessberufe, Medizintechnik": [
        ("人体/材料相关专业知识", "Fachliche Grundlagen zu Körper/Material"),
        ("护理、治疗或技工工艺（按职业）", "Pflege-, Therapie- oder Technikverfahren"),
        ("卫生与感染防护", "Hygiene und Infektionsschutz"),
        ("客户/患者咨询", "Beratung"),
        ("设备、工具与安全", "Geräte, Werkzeuge und Sicherheit"),
        ("文档、账单与法规", "Dokumentation, Abrechnung und Recht"),
        ("产品知识与销售（若适用）", "Produktkenntnisse und Verkauf"),
    ],
    "Schutz-, Sicherheits- und Überwachungsberufe": [
        ("安全法规与职权边界", "Sicherheitsrecht und Befugnisse"),
        ("巡逻、值守与报警处置", "Streifendienst, Objektschutz und Alarm"),
        ("冲突处理与沟通", "Konfliktmanagement und Kommunikation"),
        ("急救与消防基础", "Erste Hilfe und Brandschutz"),
        ("安防技术与监控系统", "Sicherheitstechnik und Überwachung"),
        ("报告与证据固定", "Berichtswesen und Beweissicherung"),
        ("企业组织与服务质量", "Betriebsorganisation und Servicequalität"),
    ],
    "Reinigungsberufe": [
        ("清洁化学与材料知识", "Reinigungschemie und Materialien"),
        ("不同表面与对象清洁工艺", "Reinigungsverfahren"),
        ("卫生、感染防护与安全", "Hygiene und Arbeitssicherheit"),
        ("设备与机械操作", "Maschinen und Geräte"),
        ("质量检查与客户沟通", "Qualitätskontrolle und Kundenkontakt"),
        ("环保与废弃物", "Umweltschutz und Entsorgung"),
        ("工作组织与计时", "Arbeitsorganisation"),
    ],
    "Bauplanungs-, Architektur- und Vermessungsberufe": [
        ("识图、制图与 CAD", "Zeichnen, CAD und Planunterlagen"),
        ("测量技术与数据处理", "Vermessungstechnik und Datenverarbeitung"),
        ("建筑构造与规范基础", "Baukonstruktion und Normen"),
        ("外业测点 / 工地配合", "Außendienst und Baustellenkoordination"),
        ("地理信息或建筑文档（按职业）", "Geoinformation oder Baudokumentation"),
        ("质量、公差与验收", "Qualität, Toleranzen und Abnahme"),
        ("法律与环保相关要点", "Recht und Umweltschutz"),
    ],
    "Technische Forschungs-, Entwicklungs-, Konstruktions- und Produktionssteuerungsberufe": [
        ("技术制图与 CAD/CAM", "Technisches Zeichnen und CAD/CAM"),
        ("产品设计与材料选择", "Konstruktion und Werkstoffauswahl"),
        ("生产计划与流程控制", "Produktionsplanung und Steuerung"),
        ("原型、试验与优化", "Prototypen, Prüfung und Optimierung"),
        ("质量管理", "Qualitätsmanagement"),
        ("项目与文档", "Projektarbeit und Dokumentation"),
        ("数字化制造衔接", "Schnittstelle digitale Fertigung"),
    ],
    "Kunststoffherstellung und -verarbeitung, Holzbe- und -verarbeitung": [
        ("材料特性与选用", "Werkstoffe und Einsatzgebiete"),
        ("识图与下料计算", "Zeichnungen und Zuschnitt"),
        ("加工工艺（锯、铣、成型、连接等）", "Bearbeitungsverfahren"),
        ("表面处理与装配", "Oberflächen und Montage"),
        ("机床与安全操作", "Maschinen und Arbeitssicherheit"),
        ("质量检验", "Qualitätsprüfung"),
        ("客户订单与文档", "Auftragsbearbeitung und Dokumentation"),
    ],
    "Rohstoffgewinnung und -aufbereitung, Glas- und Keramikherstellung und -verarbeitung": [
        ("原料与配方", "Rohstoffe und Rezepturen"),
        ("成型、烧成或加工工艺", "Formgebung, Brennen oder Bearbeitung"),
        ("窑炉/设备操作与安全", "Anlagen und Arbeitssicherheit"),
        ("质量检验与缺陷分析", "Qualitätsprüfung und Fehleranalyse"),
        ("环保与排放", "Umweltschutz"),
        ("维护与生产组织", "Instandhaltung und Organisation"),
    ],
    "Textil- und Lederberufe": [
        ("材料与面辅料知识", "Textil- und Ledermaterialien"),
        ("裁剪、缝制或成型工艺", "Zuschneiden, Nähen oder Formen"),
        ("图案、样板与尺寸", "Schnitt und Maß"),
        ("设备操作与维护", "Maschinenbedienung"),
        ("质量与返修", "Qualität und Nacharbeit"),
        ("客户订单与产品开发衔接", "Aufträge und Produktentwicklung"),
        ("劳动保护与环保", "Arbeitsschutz und Umweltschutz"),
    ],
    "Papier- und Druckberufe, technische Mediengestaltung": [
        ("印前/设计或造纸工艺基础", "Druckvorstufe, Gestaltung oder Papiertechnik"),
        ("色彩、图文与数据准备", "Farbe, Bild und Daten"),
        ("印刷/加工设备操作", "Druck- und Verarbeitungsmaschinen"),
        ("质量与色彩管理", "Qualitäts- und Farbmanagement"),
        ("媒体设计项目流程（若适用）", "Mediengestalterische Projekte"),
        ("客户沟通与文档", "Kundenkommunikation und Dokumentation"),
        ("安全与环保", "Sicherheit und Umweltschutz"),
    ],
    "Produktdesign und kunsthandwerkliche Berufe, bildende Kunst, Musikinstrumentenbau": [
        ("材料、工具与传统工艺", "Werkstoffe, Werkzeuge und Handwerkstechniken"),
        ("设计草图与模型", "Entwurf und Modell"),
        ("制作与装配", "Herstellung und Montage"),
        ("表面与音质/外观精整（按职业）", "Oberfläche, Klang oder Finish"),
        ("修复与维护（若适用）", "Restaurierung und Pflege"),
        ("客户咨询与计价", "Kundenberatung und Kalkulation"),
        ("劳动安全与质量", "Arbeitssicherheit und Qualität"),
    ],
    "Werbung, Marketing, kaufmännische und redaktionelle Medienberufe": [
        ("营销与传播基础", "Marketing und Kommunikation"),
        ("文案、编辑或活动策划（按职业）", "Text, Redaktion oder Event"),
        ("媒体渠道与数据分析", "Medienkanäle und Analyse"),
        ("客户简报与提案", "Briefing und Angebot"),
        ("项目与预算", "Projekt und Budget"),
        ("版权与媒体法要点", "Urheber- und Medienrecht"),
        ("数字化工具", "Digitale Tools"),
    ],
    "Darstellende und unterhaltende Berufe": [
        ("专业表演/技术基础", "Fachliche Grundlagen der Darstellung/Technik"),
        ("排练、演出或活动流程", "Proben, Aufführung oder Veranstaltungsablauf"),
        ("舞台/场地安全", "Sicherheit auf Bühne und Veranstaltungsort"),
        ("团队协作与时间规划", "Teamarbeit und Zeitplanung"),
        ("客户与观众沟通", "Kommunikation mit Publikum/Kunden"),
        ("设备与材料维护", "Pflege von Technik und Material"),
    ],
    "Erziehung, soziale und hauswirtschaftliche Berufe, Theologie": [
        ("教育/照护或家务专业基础", "Pädagogik, Betreuung oder Hauswirtschaft"),
        ("服务对象沟通与关系", "Beziehungsgestaltung und Kommunikation"),
        ("健康、卫生与安全", "Gesundheit, Hygiene und Sicherheit"),
        ("活动/餐饮/家务组织（按职业）", "Organisation von Angeboten"),
        ("观察、文档与反思", "Beobachtung und Dokumentation"),
        ("法律与职业伦理", "Recht und Ethik"),
        ("团队合作与机构流程", "Teamarbeit und Einrichtung"),
    ],
    "Geologie-, Geografie- und Umweltschutzberufe": [
        ("环境与循环/给排水系统基础", "Umwelt- und Ver-/Entsorgungssysteme"),
        ("采样、监测与数据分析", "Probenahme, Monitoring und Auswertung"),
        ("厂站/管网运行与维护", "Betrieb und Instandhaltung von Anlagen"),
        ("法规、许可与文档", "Recht, Genehmigungen und Dokumentation"),
        ("劳动安全与应急", "Arbeitssicherheit und Notfall"),
        ("客户/公众沟通", "Kommunikation"),
        ("可持续与资源效率", "Nachhaltigkeit und Ressourceneffizienz"),
    ],
    "Sprach-, literatur-, geistes-, gesellschafts- und wirtschaftswissenschaftliche Berufe": [
        ("专业沟通与文本工作", "Fachkommunikation und Textarbeit"),
        ("信息检索与分析", "Recherche und Analyse"),
        ("项目与客户委托", "Projekte und Aufträge"),
        ("数字化工具", "Digitale Werkzeuge"),
        ("法律与伦理边界", "Recht und Ethik"),
        ("组织与质量保证", "Organisation und Qualität"),
    ],
}

# Exact Lernfelder for well-known occupations (override group themes)
EXACT: dict[str, list[tuple[str, str]]] = {
    "Elektroniker": [
        ("LF1 分析电气技术系统、检查功能并排除故障", "Elektrotechnische Systeme analysieren, Funktionen prüfen und Fehler beheben"),
        ("LF2 规划并安装电气系统", "Elektrische Systeme planen und installieren"),
        ("LF3 分析并实现控制与调节", "Steuerungen und Regelungen analysieren und realisieren"),
        ("LF4 提供信息技术系统", "Informationstechnische Systeme bereitstellen"),
        ("LF5 设计设备与装置的电能供给与安全", "Elektroenergieversorgung und Sicherheit von Anlagen und Geräten konzipieren"),
        ("LF6 分析并检验电气技术系统", "Elektrotechnische Systeme analysieren und prüfen"),
        ("LF7 为系统编程并实现控制与调节", "Steuerungen und Regelungen für Systeme programmieren und realisieren"),
        ("LF8 选择并集成能源转换系统", "Energiewandlungssysteme auswählen und integrieren"),
        ("LF9–13 按 Fachrichtung 深化（楼宇能源 或 自动化系统）", "Fachrichtung Energie- und Gebäudetechnik / Automatisierungs- und Systemtechnik"),
    ],
    "Gärtner": [
        ("认识植物作为劳动对象", "Pflanze als Arbeitsgegenstand erfassen"),
        ("调查并记录立地条件", "Standort aufnehmen"),
        ("理解园艺业地位与任务", "Bedeutung, Stellung und Aufgaben des Gartenbaus erschließen"),
        ("准备立地与基质", "Standort vorbereiten"),
        ("在露地/室内栽培植物", "Pflanzen auf Flächen und in Räumen kultivieren"),
        ("植物与服务的营销", "Pflanzen und Dienstleistungen vermarkten"),
        ("方向课：如园林施工、温室生产、苗圃等", "Fachrichtungsbezogene Lernfelder (z. B. GaLaBau, Zierpflanzen)"),
        ("生产或施工流程的实施与控制", "Produktions- bzw. Bauverfahren durchführen und kontrollieren"),
    ],
    "Kraftfahrzeugmechatroniker": [
        ("分析车辆系统并执行维护检查", "Fahrzeuge analysieren, warten und prüfen"),
        ("诊断并修理机电故障", "Fehler diagnostizieren und instand setzen"),
        ("机电一体、舒适与安全系统", "Mechatronik-, Komfort- und Sicherheitssysteme"),
        ("动力总成与排放相关系统（按重点）", "Antrieb und Abgas / Schwerpunkt"),
        ("高压/新能源相关内容（新能源方向）", "Hochvolt- / Elektromobilität (je nach Schwerpunkt)"),
        ("客户沟通、核算与文档", "Kundenberatung, Kalkulation und Dokumentation"),
    ],
    "Fachinformatiker": [
        ("分析并规划 IT 系统", "IT-Systeme analysieren und planen"),
        ("安装与配置软硬件", "Hard- und Software installieren und konfigurieren"),
        ("网络与安全", "Netzwerke und IT-Sicherheit"),
        ("应用开发或系统集成（按方向）", "Anwendungsentwicklung / Systemintegration"),
        ("数据保护与质量", "Datenschutz und Qualitätssicherung"),
        ("项目实施与文档", "Projekte durchführen und dokumentieren"),
        ("用户支持与故障排除", "Support und Störungsbeseitigung"),
    ],
    "Kaufmann für Büromanagement": [
        ("组织办公与信息流程", "Büro- und Informationsprozesse organisieren"),
        ("处理订单与客户沟通", "Aufträge bearbeiten und Kunden kommunizieren"),
        ("人事支持流程", "Personalwirtschaftliche Prozesse unterstützen"),
        ("会计与付款往来", "Rechnungswesen und Zahlungsverkehr"),
        ("项目与活动协助", "Projekte und Veranstaltungen assistieren"),
        ("材料与采购流程", "Materialbeschaffung und Lagerprozesse"),
        ("展示与汇报", "Präsentieren und berichten"),
    ],
    "Anlagenmechaniker für Sanitär-, Heizungs- und Klimatechnik": [
        ("规划并安装卫生技术系统", "Sanitärtechnische Anlagen planen und installieren"),
        ("规划并安装供暖系统", "Heizungstechnische Anlagen planen und installieren"),
        ("通风空调系统（按重点）", "Lüftungs- und Klimatechnik"),
        ("测量、控制与调节技术", "Mess-, Steuer- und Regelungstechnik"),
        ("可再生与节能技术", "Erneuerbare Energien und Effizienz"),
        ("投运、维护与客户交接", "Inbetriebnahme, Wartung und Übergabe"),
        ("识图、材料与劳动保护", "Pläne, Materialien und Arbeitsschutz"),
    ],
    "Maurer": [
        ("工地准备与安全", "Baustelle einrichten und sichern"),
        ("砌体结构施工", "Mauerwerksarbeiten ausführen"),
        ("混凝土与钢筋混凝土配合施工", "Beton- und Stahlbetonarbeiten mitwirken"),
        ("识图、放样与材料计算", "Pläne lesen, abstecken und berechnen"),
        ("保温与建筑物理相关构造", "Wärmeschutz und bauphysikalische Grundlagen"),
        ("质量检查与文档", "Qualitätssicherung und Dokumentation"),
    ],
    "Tischler": [
        ("木材与板材知识", "Holz und Holzwerkstoffe"),
        ("识图、下料与加工", "Zeichnungen, Zuschnitt und Bearbeitung"),
        ("家具与室内构件制作", "Möbel und Innenausbauelemente herstellen"),
        ("连接技术与装配", "Verbindungstechnik und Montage"),
        ("表面处理", "Oberflächenbehandlung"),
        ("机床、CNC 基础与安全", "Maschinen, CNC-Grundlagen und Sicherheit"),
        ("客户订单与计价", "Kundenauftrag und Kalkulation"),
    ],
    "Industriekaufmann": [
        ("工业商务流程总览", "Geschäftsprozesse im Industriebetrieb"),
        ("采购与仓储", "Beschaffung und Lagerwirtschaft"),
        ("生产计划支持", "Produktionswirtschaft"),
        ("销售与客户订单", "Marketing und Vertrieb"),
        ("人事管理支持", "Personalwirtschaft"),
        ("财务会计与控制", "Finanzbuchhaltung und Controlling"),
        ("项目与数字化流程", "Projekte und digitale Prozesse"),
    ],
    "Zimmerer": [
        ("木结构识图与放样", "Holzbauzeichnungen lesen und abbinden"),
        ("木结构连接与装配", "Holzverbindungen und Montage"),
        ("屋面与楼盖木作", "Dach- und Deckenkonstruktionen"),
        ("保温、隔汽与建筑物理", "Dämmung und Bauphysik"),
        ("工地安全与起重配合", "Arbeitsschutz und Hebetechnik"),
        ("材料计算与文档", "Materialberechnung und Dokumentation"),
    ],
    "Maler und Lackierer": [
        ("表面检查与基底处理", "Untergründe prüfen und vorbereiten"),
        ("涂料、油漆与喷涂工艺", "Beschichtungs- und Lackierverfahren"),
        ("室内外装饰与设计", "Gestaltung innen und außen"),
        ("保温与外立面相关工艺（按重点）", "Wärmedämmung / Fassade"),
        ("材料计算与环保", "Materialbedarf und Umweltschutz"),
        ("客户沟通与质量验收", "Kundenkommunikation und Abnahme"),
    ],
    "Koch": [
        ("厨房组织与卫生", "Küchenorganisation und Hygiene"),
        ("食材知识与仓储", "Lebensmittelkunde und Lagerung"),
        ("热菜、冷菜与基础烹饪法", "Garverfahren und Speisenzubereitung"),
        ("菜单与成本核算", "Speisekarte und Kalkulation"),
        ("宴会/餐饮服务衔接", "Service und Veranstaltungen"),
        ("营养与特殊饮食", "Ernährung und Sonderkost"),
    ],
    "Friseur": [
        ("头发与头皮护理基础", "Haar- und Kopfhautpflege"),
        ("剪裁、造型与吹风", "Schneiden, Formen und Föhnen"),
        ("染烫与化学处理", "Färben und Umformung"),
        ("顾客咨询与销售", "Kundenberatung und Verkauf"),
        ("卫生、劳动保护与形象", "Hygiene und Arbeitsschutz"),
        ("沙龙组织与计价", "Salonorganisation und Kalkulation"),
    ],
    "Zahnmedizinischer Fachangestellter": [
        ("口腔解剖与疾病基础", "Zahnmedizinische Grundlagen"),
        ("椅旁协助与器械准备", "Assistenz und Instrumentenkunde"),
        ("卫生、消毒与感染防护", "Hygiene und Infektionsschutz"),
        ("影像与材料辅助", "Röntgenassistenz und Materialien"),
        ("患者接待与预约", "Patientenaufnahme und Terminorganisation"),
        ("账单与保险基础", "Abrechnung"),
        ("数据保护与文档", "Datenschutz und Dokumentation"),
    ],
    "Medizinischer Fachangestellter": [
        ("医疗基础与常见病", "Medizinische Grundlagen"),
        ("诊室协助与采样", "Praxisassistenz und Probenentnahme"),
        ("卫生与急救", "Hygiene und Erste Hilfe"),
        ("患者沟通与文档", "Patientenkommunikation und Dokumentation"),
        ("账单与保险", "Abrechnung und Versicherung"),
        ("器械与药品管理", "Instrumente und Arzneimittel"),
        ("数据保护", "Datenschutz"),
    ],
    "Bankkaufmann": [
        ("银行业务与账户", "Kontoführung und Bankprodukte"),
        ("支付往来", "Zahlungsverkehr"),
        ("储蓄、投资与信贷基础", "Anlage, Finanzierung und Kredit"),
        ("客户咨询与合规", "Kundenberatung und Compliance"),
        ("风险管理入门", "Risikomanagement"),
        ("数字化银行服务", "Digitales Banking"),
        ("经济与金融市场", "Wirtschaft und Finanzmärkte"),
    ],
    "Steuerfachangestellter": [
        ("税法体系与申报", "Steuerarten und Deklaration"),
        ("簿记与年度决算协助", "Buchführung und Jahresabschluss"),
        ("所得税/增值税要点", "ESt und USt"),
        ("客户资料与沟通", "Mandantenunterlagen und Kommunikation"),
        ("办公组织与软件", "Kanzleiorganisation und Software"),
        ("程序法与期限", "Verfahrensrecht und Fristen"),
        ("数据保护", "Datenschutz"),
    ],
    "Kaufmann im Einzelhandel": [
        ("商品知识与陈列", "Warenkunde und Präsentation"),
        ("销售对话与咨询", "Verkaufsgespräch"),
        ("收银与投诉", "Kasse und Reklamation"),
        ("订货、收货与库存", "Bestellung, Wareneingang und Bestand"),
        ("营销与促销", "Marketing im Handel"),
        ("企业经济与指标", "Betriebswirtschaft und Kennzahlen"),
        ("电商衔接（若企业有）", "E-Commerce"),
    ],
    "Verkäufer": [
        ("商品与服务知识", "Waren- und Dienstleistungskenntnisse"),
        ("接待与销售对话", "Kundenempfang und Verkaufsgespräch"),
        ("收银与支付", "Kasse und Zahlungsarten"),
        ("陈列与补货", "Warenpräsentation und Nachfüllen"),
        ("投诉处理", "Reklamationsbearbeitung"),
        ("卫生与安全", "Hygiene und Sicherheit"),
    ],
    "Dachdecker": [
        ("屋面构造与材料", "Dachkonstruktionen und Werkstoffe"),
        ("防水、保温与通风层", "Abdichtung, Dämmung und Lüftung"),
        ("坡屋面 / 平屋面工艺", "Steil- und Flachdacharbeiten"),
        ("外立面相关覆盖（若适用）", "Fassadenbekleidung"),
        ("高空作业安全", "Absturzsicherung und Arbeitsschutz"),
        ("识图、计算与文档", "Pläne, Berechnung und Dokumentation"),
    ],
    "Straßenbauer": [
        ("道路结构层与材料", "Straßenaufbau und Baustoffe"),
        ("土方与路基", "Erd- und Unterbauarbeiten"),
        ("沥青与混凝土路面", "Asphalt- und Betonfahrbahnen"),
        ("排水与路缘", "Entwässerung und Randeinfassungen"),
        ("工地安全与交通导改", "Arbeitsschutz und Verkehrssicherung"),
        ("测量放样与质量检查", "Abstecken und Qualitätsprüfung"),
    ],
    "Mechatroniker": [
        ("机械、电气与控制基础", "Mechanik, Elektrotechnik und Steuerung"),
        ("组装机电系统", "Mechatronische Systeme montieren"),
        ("编程与调试（PLC 等）", "Programmieren und Inbetriebnehmen"),
        ("液压气动", "Hydraulik und Pneumatik"),
        ("维护与故障诊断", "Wartung und Fehlerdiagnose"),
        ("文档与质量", "Dokumentation und Qualität"),
    ],
    "Zerspanungsmechaniker": [
        ("识图与公差", "Zeichnungen und Toleranzen"),
        ("切削原理与刀具", "Zerspanungslehre und Werkzeuge"),
        ("车铣等机床操作", "Dreh- und Fräsmaschinen"),
        ("CNC 编程与设置", "CNC-Programmierung und Einrichten"),
        ("测量与质量保证", "Messtechnik und QS"),
        ("材料与冷却润滑", "Werkstoffe und Kühlschmierstoffe"),
        ("劳动安全", "Arbeitssicherheit"),
    ],
    "Elektroniker für Automatisierungstechnik": [
        ("电气系统分析与安装", "Elektrische Systeme analysieren und installieren"),
        ("控制与自动化组件", "Steuerungs- und Automatisierungskomponenten"),
        ("PLC 编程与总线通信", "SPS-Programmierung und Bussysteme"),
        ("驱动与传感技术", "Antriebs- und Sensortechnik"),
        ("系统投运与优化", "Inbetriebnahme und Optimierung"),
        ("安全技术与文档", "Sicherheitstechnik und Dokumentation"),
    ],
    "Elektroniker für Betriebstechnik": [
        ("电气装置规划与安装", "Elektrische Anlagen planen und installieren"),
        ("开关设备与配电", "Schaltanlagen und Energieverteilung"),
        ("驱动与控制技术", "Antriebs- und Steuerungstechnik"),
        ("厂房供电与安全", "Betriebsstromversorgung und Sicherheit"),
        ("维护与故障排除", "Instandhaltung und Störungsbeseitigung"),
        ("自动化系统衔接", "Automatisierungssysteme"),
    ],
    "Industrieelektriker": [
        ("电气安装与接线", "Elektroinstallation und Verdrahtung"),
        ("测量与安全检验", "Messen und Sicherheitsprüfung"),
        ("设备投运协助", "Mitwirken bei Inbetriebnahme"),
        ("维护与简单故障排除", "Wartung und einfache Störungsbeseitigung"),
        ("劳动保护与文档", "Arbeitsschutz und Dokumentation"),
    ],
    "Fachkraft für Lagerlogistik": [
        ("仓储流程与货位管理", "Lagerprozesse und Lagerorganisation"),
        ("收货、上架、拣选、出库", "Wareneingang, Kommissionierung, Versand"),
        ("叉车与输送技术（配合取证）", "Fördertechnik"),
        ("库存与库存差异", "Bestandsführung"),
        ("危险品与劳动保护", "Gefahrgut und Arbeitsschutz"),
        ("物流信息技术", "Lager-IT"),
        ("质量与客户导向", "Qualität und Kundenservice"),
    ],
    "Berufskraftfahrer": [
        ("驾驶与交通法规", "Fahren und Verkehrsrecht"),
        ("车辆技术与检查", "Fahrzeugtechnik und Kontrolle"),
        ("货物固定", "Ladungssicherung"),
        ("社会经济与运输法", "Sozialvorschriften und Transportrecht"),
        ("危货基础（若适用）", "Gefahrgut"),
        ("客户与单据", "Kunden und Frachtpapiere"),
        ("经济驾驶", "Wirtschaftliches Fahren"),
    ],
    "Landwirt": [
        ("植物生产或畜牧基础（按企业）", "Pflanzenbau oder Tierhaltung"),
        ("土壤、肥料与植保", "Boden, Düngung und Pflanzenschutz"),
        ("农业机械与安全", "Landtechnik und Arbeitssicherheit"),
        ("动物福利与饲养（畜牧）", "Tierwohl und Fütterung"),
        ("农场经营与核算", "Unternehmensführung"),
        ("营销与质量", "Vermarktung und Qualität"),
        ("环保与交叉合规", "Umweltschutz und Cross Compliance"),
    ],
    "Forstwirt": [
        ("森林生态与树种", "Waldbau und Baumarten"),
        ("采伐与集材技术", "Holzernte und Bringung"),
        ("森林保护与狩猎相关基础", "Waldschutz"),
        ("机械与安全（链锯等）", "Forsttechnik und Arbeitssicherheit"),
        ("更新造林与抚育", "Verjüngung und Pflege"),
        ("木材计量与质量", "Holzaufnahme und Qualität"),
        ("自然保护与公共任务", "Naturschutz und öffentliche Aufgaben"),
    ],
    "Pferdewirt": [
        ("马匹饲养与马厩管理", "Pferdehaltung und Stallmanagement"),
        ("饲养、健康与福利", "Fütterung, Gesundheit und Tierwohl"),
        ("训练/繁殖/马术运动（按方向）", "Fachrichtung Ausbildung, Zucht, Rennreiten u. a."),
        ("设施与机械", "Anlage und Technik"),
        ("客户与赛事组织基础", "Kunden und Veranstaltungen"),
        ("经营与安全", "Betriebsführung und Sicherheit"),
    ],
    "Revierjäger": [
        ("狩猎法与野生动物生态", "Jagdrecht und Wildbiologie"),
        ("猎区经营与生境照料", "Revieren und Lebensraumgestaltung"),
        ("狩猎实施与野生动物健康", "Jagdbetrieb und Wildgesundheit"),
        ("自然保护与冲突管理", "Naturschutz und Konfliktmanagement"),
        ("设施、犬只与安全", "Einrichtungen, Jagdhunde und Sicherheit"),
        ("公众沟通与文档", "Öffentlichkeitsarbeit und Dokumentation"),
    ],
    "Binnenschiffer": [
        ("船舶操纵与航行规则", "Schiffsführung und Verkehrsregeln"),
        ("轮机与甲板工作", "Maschinen- und Decksdienst"),
        ("货物装卸与安全", "Ladungsumschlag und Sicherheit"),
        ("通信与导航基础", "Kommunikation und Navigation"),
        ("环保与应急", "Umweltschutz und Notfälle"),
        ("船员值班与组织", "Wachdienst und Organisation"),
    ],
    "Schiffsmechaniker": [
        ("船舶机械系统", "Schiffsmaschinensysteme"),
        ("维护、检修与故障排除", "Wartung, Instandsetzung und Störungsbeseitigung"),
        ("电气与控制辅助", "Elektro- und Steuerungstechnik"),
        ("安全、消防与环保", "Sicherheit, Brandschutz und Umweltschutz"),
        ("值班与文档", "Wachdienst und Dokumentation"),
        ("港口与航行配合工作", "Betrieb im Hafen und auf See/Binnenfahrt"),
    ],
    "Umwelttechnologe für Wasserversorgung": [
        ("供水系统与水质", "Wasserversorgung und Wasserqualität"),
        ("取水、处理与输送", "Gewinnung, Aufbereitung und Verteilung"),
        ("厂站运行与维护", "Anlagenbetrieb und Instandhaltung"),
        ("采样、检测与文档", "Probenahme, Analytik und Dokumentation"),
        ("法规与劳动安全", "Recht und Arbeitssicherheit"),
        ("客户与应急供水", "Kunden und Notversorgung"),
    ],
    "Umwelttechnologe für Abwasserbewirtschaftung": [
        ("污水系统与处理工艺", "Abwasseranlagen und Verfahren"),
        ("管网与泵站运行", "Kanalnetz und Pumpwerke"),
        ("生化/物化处理控制", "Prozesskontrolle"),
        ("污泥与残渣处置", "Schlammbehandlung"),
        ("采样、检测与环保法规", "Analytik und Umweltrecht"),
        ("维护、安全与应急", "Instandhaltung, Sicherheit und Störfälle"),
    ],
    "Vermessungstechniker": [
        ("测量仪器与方法", "Vermessungsgeräte und Verfahren"),
        ("外业测点与放样", "Außendienst und Absteckung"),
        ("数据处理与绘图", "Datenverarbeitung und Planerstellung"),
        ("地籍/工程/摄影测量（按重点）", "Kataster-, Ingenieur- oder Photogrammetrie"),
        ("质量与公差", "Qualität und Genauigkeit"),
        ("法规与文档", "Recht und Dokumentation"),
    ],
    "Geomatiker": [
        ("地理数据采集", "Geodaten erfassen"),
        ("数据处理与数据库", "Geodaten verarbeiten und speichern"),
        ("可视化与制图", "Visualisieren und Kartographie"),
        ("遥感与激光扫描基础", "Fernerkundung und Laserscanning"),
        ("客户产品与质量", "Kundenprodukte und Qualität"),
        ("数据保护与标准", "Datenschutz und Standards"),
    ],
    "Florist": [
        ("植物与花材知识", "Pflanzen- und Werkstoffkunde"),
        ("花艺设计与制作", "Floristische Gestaltung"),
        ("销售与客户咨询", "Verkauf und Beratung"),
        ("店面陈列与活动", "Präsentation und Events"),
        ("采购、护理与损耗", "Einkauf, Pflege und Schwund"),
        ("计价与店务组织", "Kalkulation und Ladenorganisation"),
    ],
    "Winzer": [
        ("葡萄栽培与土壤", "Weinbau und Bodenkunde"),
        ("葡萄园机械与安全", "Weinbautechnik und Arbeitsschutz"),
        ("植保与品质管理", "Pflanzenschutz und Qualität"),
        ("收获与酿造衔接", "Lese und Kellerwirtschaft"),
        ("营销与品鉴基础", "Vermarktung und Sensorik"),
        ("经营与法规", "Betriebsführung und Recht"),
    ],
    "Tierwirt": [
        ("畜牧饲养与动物福利", "Tierhaltung und Tierwohl"),
        ("饲料与健康", "Fütterung und Tiergesundheit"),
        ("畜舍、机械与安全", "Stalltechnik und Arbeitsschutz"),
        ("繁殖与生产指标（按畜种）", "Zucht und Leistungsdaten"),
        ("产品与质量", "Produkte und Qualität"),
        ("经营与环保", "Betriebsführung und Umweltschutz"),
    ],
    "Fischwirt": [
        ("渔业与水域生态", "Fischerei und Gewässerökologie"),
        ("养殖或捕捞技术（按方向）", "Aquakultur oder Fischfang"),
        ("水质、饲料与鱼病", "Wasserqualität, Fütterung und Fischkrankheiten"),
        ("机械、网具与安全", "Technik und Arbeitsschutz"),
        ("加工、销售与法规", "Verarbeitung, Vermarktung und Recht"),
        ("自然保护相关任务", "Naturschutz"),
    ],
}


def match_exact_key(name: str, filename: str) -> str | None:
    """Match only when the German filename stem equals the EXACT key (or key before slash)."""
    keys = sorted(EXACT.keys(), key=len, reverse=True)
    stem = filename[:-3] if filename.endswith(".md") else filename
    de = stem.split("-", 1)[-1] if "-" in stem else stem
    de_base = de.split("/")[0].strip()
    for k in keys:
        if de == k or de_base == k:
            return k
    return None


def themes_for(rec: dict) -> tuple[list[tuple[str, str]], str]:
    name = rec.get("name") or ""
    filename = rec.get("filename") or ""
    exact = match_exact_key(name, filename)
    if exact:
        return EXACT[exact], "rahmenlehrplan_exact"

    groups = rec.get("groups") or []
    gname = groups[0]["name"] if groups else ""
    themes = list(GROUP_THEMES.get(gname, []))
    if not themes:
        themes = [
            ("专业理论基础与安全规范", "Fachtheorie und Arbeitssicherheit"),
            ("典型工作任务的计划—实施—检查", "Berufliche Handlungsabläufe"),
            ("材料、工具或软件应用", "Werkzeuge, Materialien oder Software"),
            ("质量保证与文档", "Qualitätssicherung und Dokumentation"),
            ("客户或协作沟通", "Kommunikation"),
            ("企业经济与组织基础", "Betriebsorganisation"),
        ]
    specs = rec.get("specializations") or []
    if specs:
        spec_s = "、".join(specs[:6])
        themes = themes + [
            (f"方向深化：{spec_s}", f"Vertiefung: {', '.join(specs[:6])}"),
        ]
    return themes, "group_template"


def build_section(rec: dict) -> str:
    themes, source = themes_for(rec)
    name_zh = rec.get("name_zh") or ""
    name = (rec.get("name") or "").split("/")[0].strip()
    rows = []
    for i, (zh, de) in enumerate(themes, 1):
        rows.append(f"| {i} | {zh} | {de} |")
    theme_table = "\n".join(rows)

    source_note = (
        "下列学习领域名称按 **KMK 框架教学计划**常见表述整理；学时与编号以你所在州课表为准。"
        if source == "rahmenlehrplan_exact"
        else "下列为按本职业主组与培训内容归纳的**专业主题**（对应学校「学习领域 Lernfelder」）；具体 LF 编号、名称与学时以所在州 Rahmenlehrplan / 职业学校课表为准。"
    )

    specs = rec.get("specializations") or []
    spec_line = ""
    if specs:
        spec_line = (
            f"\n本职业若分 Fachrichtung / Schwerpunkt / Wahlqualifikation"
            f"（如 {'、'.join(specs[:8])}{'…' if len(specs) > 8 else ''}），"
            f"**高年级专业课会按你合同方向分流**，低年级多为共通基础。\n"
        )

    return f"""
{MARKER_START}
### 职业学校（Berufsschule）上什么课

双元制里，职业学校课程通常分两块：**普通课（跨职业）** + **专业学习领域（Lernfelder，本职业）**。企业实训教现场操作；学校课补理论、计算、图纸/规范、安全与结业笔试相关内容。各州科目名称与周学时略有差异。

#### 普通课（多数职业共通）

{GENERAL_TABLE}

数学、物理、化学、制图等常**嵌入专业学习领域**，不一定单独成课。

#### 本职业专业课主题（{name_zh or name}）

{source_note}
{spec_line}
| 序号 | 主题（中文） | 德语关键词 |
| --- | --- | --- |
{theme_table}

此外常见：**劳动保护与环保**贯穿各学习领域；手工业/部分工业还有**跨企业培训课（überbetriebliche Lehrgänge）**补学校与企业都覆盖不足的模块。排课是「每周固定几天」还是 **Blockunterricht（集中授课块）**，见[第 13 节](#13-培训日常节奏与考试节点)。
{MARKER_END}
""".strip()


def inject_into_markdown(text: str, section: str) -> str:
    # Remove previous injection
    if MARKER_START in text and MARKER_END in text:
        text = re.sub(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END) + r"\n?",
            "",
            text,
            flags=re.S,
        )

    # Prefer insert after 工作现实 block, before --- then ## 2.
    # Gärtner uses "### 工作现实（选方向前要想清楚）"; templates use "### 工作现实（签约前要想清楚）"
    patterns = [
        # After 工作现实 section: find next --- before ## 2
        (r"(### 工作现实[^\n]*\n.*?)(\n---\n\n## 2\.)", re.S),
        # After 官方细分 if no 工作现实 edge case
        (r"(报名与合同时确认你的方向名称[^\n]*\n)(\n---\n\n## 2\.)", re.S),
        # Fallback: before ## 2
        (r"(\n)(## 2\.)", re.S),
    ]

    block = "\n\n" + section + "\n"
    for pat, flags in patterns:
        new_text, n = re.subn(pat, r"\1" + block + r"\2", text, count=1, flags=flags)
        if n:
            return new_text

    # Last resort: append before ## 13
    if "## 13." in text:
        return text.replace("## 13.", section + "\n\n## 13.", 1)
    return text + "\n\n" + section + "\n"


def main() -> None:
    records = json.loads(DATA.read_text(encoding="utf-8"))
    by_file = {r["filename"]: r for r in records if r.get("filename")}

    updated = 0
    missing = []
    for path in sorted(BERUFE_DIR.glob("*.md")):
        rec = by_file.get(path.name)
        if not rec:
            # fuzzy: match by ending german part
            stem = path.name
            rec = next((r for r in records if r.get("filename") == stem), None)
        if not rec:
            # build minimal rec from filename
            rec = {
                "filename": path.name,
                "name": path.stem.split("-", 1)[-1] if "-" in path.stem else path.stem,
                "name_zh": path.stem.split("-", 1)[0] if "-" in path.stem else path.stem,
                "groups": [],
                "specializations": [],
            }
            missing.append(path.name)

        section = build_section(rec)
        text = path.read_text(encoding="utf-8")
        new_text = inject_into_markdown(text, section)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8", newline="\n")
            updated += 1

    print(f"updated={updated} total_md={len(list(BERUFE_DIR.glob('*.md')))} fuzzy_or_minimal={len(missing)}")
    if missing[:10]:
        print("minimal examples:", missing[:10])


if __name__ == "__main__":
    main()
