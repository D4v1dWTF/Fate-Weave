#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
《命運織網》—— RPG 人生模擬
版本 0.2.0
- 新增圖鑑系統：記錄已解鎖的結局與隱藏事件
- 顯示解鎖條件
- 三段式介面：資訊欄 | 事件監視器 | 動作面板
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import json
import os
import random
import urllib.request
import urllib.error
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime

# =============================================================================
# 版本資訊
# =============================================================================
VERSION = "0.2.0"

# =============================================================================
# 1. 世界觀與故事背景
# =============================================================================

WORLD_BACKGROUND = f"""
🌍 世界觀：《命運織網》 v{VERSION}
宇宙是一張由「命運絲線」編織的巨網，每個生命都是網上的一個節點。
三種原力交織其中：織線之力（秩序）、裂變之力（變化）、靈韻之力（生命）
你是一名「節點行者」，能夠感知並影響命運絲線的流動。
"""

KEY_NPCS = {
    "weaver_elder": {"name": "織老", "description": "織世者長老", "personality": "睿智、沉穩", "faction": "秩序", "initial_rep": 0},
    "rift_walker": {"name": "裂隙行者", "description": "自由不羈的裂變者", "personality": "自由、激進", "faction": "變化", "initial_rep": 10},
    "gearwright": {"name": "齒輪師", "description": "機械改造專家", "personality": "務實、創新", "faction": "中立", "initial_rep": 0},
    "foreseer": {"name": "預見者", "description": "能望穿命運絲線", "personality": "神秘、深邃", "faction": "變化", "initial_rep": -10},
    "bulwark_commander": {"name": "壁壘統帥", "description": "鐵血領袖", "personality": "威嚴、鐵面", "faction": "秩序", "initial_rep": -5}
}

SCENE_FRAMEWORK = {
    "origin": {"name": "命運起點", "description": "你從虛無中醒來，命運之網剛為你展開第一個節點。", "npcs": ["weaver_elder"]},
    "village": {"name": "織網小鎮", "description": "古老村落，隱藏織世者的秘密。", "npcs": ["weaver_elder", "rift_walker"]},
    "forest": {"name": "靈韻森林", "description": "樹木參天，靈韻之力湧動。", "npcs": ["rift_walker", "gearwright"]},
    "city": {"name": "織法之城", "description": "科技與神秘交融的都市。", "npcs": ["bulwark_commander", "foreseer"]},
    "ruins": {"name": "星隕遺跡", "description": "失落文明的最後痕跡。", "npcs": ["gearwright", "foreseer"]},
    "rift_realm": {"name": "裂變之境", "description": "秩序薄弱之地，命運絲線扭曲交織。", "npcs": ["foreseer", "rift_walker"]},
    "core": {"name": "世界之核", "description": "三種原力交匯的終極節點。", "npcs": []}
}

# 商店物品
SHOP_ITEMS = [
    {"id": "potion", "name": "治療藥水", "desc": "恢復 20 點健康", "price": 100, "effect": {"health": 20}},
    {"id": "mana_potion", "name": "能量藥水", "desc": "恢復 15 點理智", "price": 120, "effect": {"sanity": 15}},
    {"id": "strength_ring", "name": "力量指環", "desc": "永久力量 +5", "price": 500, "effect": {"strength": 5}},
    {"id": "wisdom_book", "name": "智慧之書", "desc": "永久智力 +5", "price": 500, "effect": {"intelligence": 5}},
    {"id": "lucky_charm", "name": "幸運護符", "desc": "永久運氣 +5", "price": 500, "effect": {"luck": 5}},
    {"id": "cyber_arm", "name": "基礎義肢", "desc": "力量 +10，但有隱藏風險", "price": 2000, "effect": {"strength": 10}, "flag": "installed_prosthetic", "hidden_effect": "50歲後可能失控"},
]

# 科技樹
TECH_TREE = [
    {"age": 30, "name": "絲線義肢", "desc": "提升力量與健康", "cost": 2000, "effects": {"strength": 20, "health": 20},
     "side_effect": "50歲後可能絲線紊亂", "flag": "installed_prosthetic", "hidden_event_age": 50,
     "hidden_event_desc": "你感到義肢傳來異樣的震動…",
     "solution": "你可以定期前往機械師處檢修（消耗信用點 500，健康 +5）",
     "solution_effects": {"health": 5, "credits": -500}},
    {"age": 35, "name": "記憶織網", "desc": "記憶備份", "cost": 3000, "effects": {},
     "side_effect": "駭客可能竊取記憶", "flag": "memory_web",
     "hidden_event_desc": "你的記憶雲端遭到不明存取…",
     "solution": "更換加密協議（消耗信用點 800）",
     "solution_effects": {"credits": -800}},
    {"age": 40, "name": "腦機織接", "desc": "提升智力與創造力", "cost": 3000, "effects": {"intelligence": 15, "creativity": 15},
     "side_effect": "資訊過載(-10理智)", "flag": "brain_weave",
     "hidden_event_desc": "你接收了太多雜訊，思緒開始混亂…",
     "solution": "進行冥想調節（消耗 1 行動點，理智 +10）",
     "solution_effects": {"sanity": 10}},
    {"age": 50, "name": "基因編織", "desc": "延長壽命20年", "cost": 5000, "effects": {"health": 20},
     "side_effect": "隨機屬性-20", "flag": "gene_weave",
     "hidden_event_desc": "你的基因開始出現不穩定跡象…",
     "solution": "接受基因穩定治療（消耗信用點 3000）",
     "solution_effects": {"health": 10, "credits": -3000}},
    {"age": 60, "name": "奈米織護", "desc": "持續修復身體", "cost": 8000, "effects": {"health": 30},
     "side_effect": "奈米失控(死亡)", "flag": "nano_weave",
     "hidden_event_desc": "你體內的奈米機器人開始自我複製…",
     "solution": "緊急關閉系統（消耗信用點 5000，理智 -10）",
     "solution_effects": {"credits": -5000, "sanity": -10}},
]

# =============================================================================
# 2. 結局定義（用於圖鑑）
# =============================================================================

ENDING_DEFINITIONS = {
    "legend": {
        "name": "命運織主",
        "description": "你活了100歲且財富滔天，成為命運之網的主宰者。",
        "condition_text": "活到 100 歲 且 財富 ≥ 100,000"
    },
    "madman": {
        "name": "裂變狂人",
        "description": "你在瘋狂中活到80歲，成為裂變之力的化身。",
        "condition_text": "理智 < 10 且 活到 80 歲"
    },
    "tycoon": {
        "name": "織網巨鱷",
        "description": "你累積了驚人的財富，成為命運之網的樞紐。",
        "condition_text": "財富 ≥ 500,000"
    },
    "hermit": {
        "name": "絲線隱者",
        "description": "你遠離人群，孤獨終老，與命運絲線獨處。",
        "condition_text": "活到 60 歲 且 所有人際關係總和 < 10"
    },
    "digital_ghost": {
        "name": "織網幽靈",
        "description": "你的意識融入命運網絡，成為永恆的數據生命。",
        "condition_text": "擁有旗標 'consciousness_web'（安裝意識織網科技）"
    },
    "time_rogue": {
        "name": "時空織者",
        "description": "你不斷穿梭時間，修復或創造命運節點。",
        "condition_text": "擁有旗標 'time_weave'（安裝時空織旅科技）"
    },
    "balance": {
        "name": "織網平衡者",
        "description": "你調和三種原力，世界因你而和諧。",
        "condition_text": "實力等級 ≥ '半神' 且 擁有 ≥ 10 個旗標 且 活到 60 歲"
    },
    "default": {
        "name": "凡人織者",
        "description": "你度過了一段普通而真實的人生。",
        "condition_text": "未滿足上述任何條件"
    }
}

# 隱藏事件定義（用於圖鑑）
HIDDEN_EVENT_DEFINITIONS = {
    "prosthetic_adapt": {
        "name": "義肢適應",
        "description": "你的身體完全適應了義肢，動作變得更加流暢。",
        "condition_text": "安裝絲線義肢後，40歲前小概率觸發",
        "is_positive": True
    },
    "brain_optimize": {
        "name": "腦機優化",
        "description": "你的腦機介面自動優化了神經連結，思維更加清晰。",
        "condition_text": "安裝腦機織接後，45歲前小概率觸發",
        "is_positive": True
    },
    "memory_boost": {
        "name": "記憶強化",
        "description": "你的記憶雲端自動整理，喚醒了遺忘的靈感。",
        "condition_text": "安裝記憶織網後，隨機觸發",
        "is_positive": True
    },
    "prosthetic_malfunction": {
        "name": "義肢異常",
        "description": "義肢傳來異樣的震動，似乎有自主意識…",
        "condition_text": "安裝絲線義肢後，50歲後小概率觸發",
        "is_positive": False
    },
    "brain_overload": {
        "name": "腦機過載",
        "description": "你接收到不屬於自己的記憶片段，腦中一片混亂。",
        "condition_text": "安裝腦機織接後，45歲後小概率觸發",
        "is_positive": False
    }
}

# =============================================================================
# 3. 結局敘事（每個結局 4 種版本）
# =============================================================================

ENDING_NARRATIVES = {
    "legend": {
        "versions": [
            {"name": "財富傳奇", "condition": lambda p: p.credits >= 1000000,
             "text": "你以無可匹敵的財富統治了命運之網，你的名字被刻在每一條絲線上，成為永恆的傳說。",
             "world_reaction": "你的財富帝國的影響力持續了數百年，後人為你建立了黃金紀念碑。"},
            {"name": "健康傳奇", "condition": lambda p: p.health >= 90,
             "text": "你以強健的體魄與驚人的財富，活成了所有人羨慕的模樣。你的晚年仍然充滿活力，直到最後一刻都在影響世界。",
             "world_reaction": "你的健康秘訣被世代傳承，人們稱你為『不朽織者』。"},
            {"name": "智慧傳奇", "condition": lambda p: p.intelligence >= 90,
             "text": "你的智慧與財富並存，你建立了自己的學派，培養了一代又一代的織網者。你的思想比你的財富更長久。",
             "world_reaction": "你的學派延續了千年，你的著作被奉為織網聖經。"},
            {"name": "默認傳奇", "condition": lambda p: True,
             "text": "你活了百年，富可敵國。當你離世時，整個世界都在哀悼，你的傳奇故事被傳頌了數百年。",
             "world_reaction": "每年你的忌日，全世界的織網者都會為你點亮一根蠟燭。"}
        ]
    },
    "madman": {
        "versions": [
            {"name": "瘋狂創世", "condition": lambda p: p.creativity >= 90,
             "text": "你以瘋狂的創造力撕裂了現實的邊界，你的藝術與思想成為裂變之力的最高展現，後人稱你為『瘋狂先知』。",
             "world_reaction": "你的作品被陳列在裂變神殿中，成為所有裂變者的精神圖騰。"},
            {"name": "瘋狂力量", "condition": lambda p: p.strength >= 80,
             "text": "你的瘋狂化為無可阻擋的力量，你一拳打碎了命運之網的枷鎖，成為裂變者們永遠的精神領袖。",
             "world_reaction": "裂變者們將你的拳頭視為聖物，你的傳說激勵了無數追求自由的人。"},
            {"name": "百年瘋狂", "condition": lambda p: p.age >= 100,
             "text": "你在瘋狂中活了整整百年，人們已經分不清你是瘋子還是天才，你早已超越人類的理解範圍。",
             "world_reaction": "你的百年瘋狂成為了傳奇，有人說你是神，有人說你是惡魔，但沒人能否認你的偉大。"},
            {"name": "默認瘋狂", "condition": lambda p: True,
             "text": "你的理智在 80 歲時徹底崩潰，但你留下的混亂與變革，永遠改變了這個世界的走向。",
             "world_reaction": "你的混亂遺產持續影響著世界，裂變者們視你為啟蒙者。"}
        ]
    },
    "tycoon": {
        "versions": [
            {"name": "魅力巨鱷", "condition": lambda p: p.charisma >= 90,
             "text": "你用魅力與金錢征服了所有人，你的商業帝國橫跨整個命運之網，無人能撼動你的地位。",
             "world_reaction": "你的商業帝國的影響力持續了數個世紀，你的商業法則被奉為圭臬。"},
            {"name": "智慧巨鱷", "condition": lambda p: p.intelligence >= 80,
             "text": "你以超凡的商業頭腦累積了驚人財富，你的投資策略成為後世教材，你的名字是『智慧』的代名詞。",
             "world_reaction": "你的投資理論被寫入各大商學院教材，你的財富故事激勵了無數創業者。"},
            {"name": "長壽巨鱷", "condition": lambda p: p.age >= 80,
             "text": "你從年輕時就開始積累財富，到老時已是富可敵國。你的葬禮上，人們為你立了黃金雕像。",
             "world_reaction": "你的黃金雕像至今仍矗立在商業中心，成為所有商人的朝聖地。"},
            {"name": "默認巨鱷", "condition": lambda p: True,
             "text": "你成為了命運之網最有錢的人。當你離去時，你的財富成為了傳說，無數人追尋你的足跡。",
             "world_reaction": "你的財富引發了一場持續數十年的尋寶熱潮，你的遺產成為了一個時代的象徵。"}
        ]
    },
    "hermit": {
        "versions": [
            {"name": "智慧隱者", "condition": lambda p: p.intelligence >= 90,
             "text": "你獨自一人在山中修行了數十年，你的智慧通達天地，成為隱士中的隱士，傳說中的傳說。",
             "world_reaction": "你的智慧語錄被世人傳頌，隱士們將你的山洞視為聖地。"},
            {"name": "健康隱者", "condition": lambda p: p.health >= 80,
             "text": "你遠離人群，過著與世無爭的生活，身體健朗地活到了高齡。你與命運絲線共舞了一生。",
             "world_reaction": "你的養生秘訣被後人記錄，成為追求健康者的聖經。"},
            {"name": "長壽隱者", "condition": lambda p: p.age >= 80,
             "text": "你孤獨地活了八十年，從未與任何人建立深刻的連結。但你與自己和解了，這也是一種圓滿。",
             "world_reaction": "你的孤獨哲學影響了無數人，人們開始反思現代生活對真實連結的意義。"},
            {"name": "默認隱者", "condition": lambda p: True,
             "text": "你一生都在逃避人群，最終在孤獨中老去。但你與命運絲線的對話，比任何人都深刻。",
             "world_reaction": "你的日記被發現後出版，成為了解內心世界的經典著作。"}
        ]
    },
    "digital_ghost": {
        "versions": [
            {"name": "智慧幽靈", "condition": lambda p: p.intelligence >= 90,
             "text": "你的意識上傳至命運網絡後，你以超乎想像的速度學習與進化，成為了網絡中的神明。",
             "world_reaction": "你在網絡中的智慧成為了所有數位生命追尋的終極目標。"},
            {"name": "創造幽靈", "condition": lambda p: p.creativity >= 90,
             "text": "你以數位之姿創造了無數虛擬世界，你成為了創世者，在網絡中自由翱翔。",
             "world_reaction": "你創造的虛擬世界成為了數十億人的精神家園。"},
            {"name": "長壽幽靈", "condition": lambda p: p.age >= 70,
             "text": "你在 70 歲時選擇了意識上傳，從此人間再無你，但網絡中處處是你的影子。",
             "world_reaction": "你的數位足跡成為了人類文明的永恆紀念碑。"},
            {"name": "默認幽靈", "condition": lambda p: True,
             "text": "你的意識化為永恆的數據，在命運網絡中漂流。你獲得了某種意義上的永生。",
             "world_reaction": "你的存在成為了網絡中的傳奇，有人說你還在某處悄悄觀察著這個世界。"}
        ]
    },
    "time_rogue": {
        "versions": [
            {"name": "智慧時空", "condition": lambda p: p.intelligence >= 90,
             "text": "你穿梭時間無數次，最終參透了時間的本質。你不再被時間束縛，成為了時間本身。",
             "world_reaction": "你的時間理論徹底改變了人類對宇宙的理解。"},
            {"name": "創造時空", "condition": lambda p: p.creativity >= 80,
             "text": "你在時間線中創造了無數分支，每一次穿梭都是一次新的創作。你是時間的藝術家。",
             "world_reaction": "你的時間藝術作品成為了跨越時代的經典。"},
            {"name": "健康時空", "condition": lambda p: p.health >= 80,
             "text": "你強健的體魄讓你在時間旅行中毫髮無傷，你成為了最完美的時空旅者。",
             "world_reaction": "你的身體成為了科學家研究的對象，人們渴望複製你的時空旅行能力。"},
            {"name": "默認時空", "condition": lambda p: True,
             "text": "你穿梭於過去與未來之間，修正了無數錯誤，最終消失在時間的縫隙中，成為永恆的謎。",
             "world_reaction": "你的消失成為了最大的歷史懸案，有人說你還在某個時間點看著這個世界。"}
        ]
    },
    "balance": {
        "versions": [
            {"name": "完美平衡", "condition": lambda p: all(getattr(p, attr) >= 70 for attr in ['health','intelligence','strength','charisma','luck','sanity','creativity']),
             "text": "你在所有方面都達到了超凡境界，你成為了三種原力的完美平衡者，世界因你而和諧。",
             "world_reaction": "你的平衡之道成為了世界的終極法則，所有衝突因你而止。"},
            {"name": "智慧力量平衡", "condition": lambda p: p.intelligence >= 80 and p.strength >= 80,
             "text": "你的智慧與力量並重，你以理性與行動調和了世界的衝突，成為了和平的象徵。",
             "world_reaction": "你的和平理念被寫入國際憲章，世界進入了長達數百年的和平時期。"},
            {"name": "魅力運氣平衡", "condition": lambda p: p.charisma >= 80 and p.luck >= 80,
             "text": "你的魅力與運氣讓你成為命運之網的樞紐，所有人都願意追隨你，你帶來了黃金時代。",
             "world_reaction": "你的黃金時代成為了歷史教科書中最輝煌的一頁。"},
            {"name": "默認平衡", "condition": lambda p: True,
             "text": "你找到了三種原力的平衡點，世界因你而不再混亂。你的名字被寫入命運之網的核心。",
             "world_reaction": "你的名字成為了『平衡』的同義詞，你的雕像矗立在世界的中心。"}
        ]
    },
    "default": {
        "versions": [
            {"name": "有意義的平凡", "condition": lambda p: len(p.life_achievements) >= 3,
             "text": "你雖然只是一個凡人，但你活得精彩，你幫助了許多人，你的善行被永遠記住。",
             "world_reaction": "你的善行故事被當地人傳頌，你成為了社區的精神支柱。"},
            {"name": "長壽平凡", "condition": lambda p: p.age >= 70,
             "text": "你活了 70 年，雖然平凡但很充實。你有愛你的人，有你愛的事，這就是最真實的幸福。",
             "world_reaction": "你的子孫們繼承了你的善良與樂觀，你的家族成為了社區的榜樣。"},
            {"name": "健康平凡", "condition": lambda p: p.health >= 60,
             "text": "你健健康康地活了一輩子，最後在睡夢中安詳離世。對一個凡人來說，這是最好的結局。",
             "world_reaction": "你的安詳離世成為了當地『好死』的典範，人們說你被命運善待了。"},
            {"name": "默認平凡", "condition": lambda p: True,
             "text": "你度過了一段普通而真實的人生。你愛過、笑過、哭過，你沒有改變世界，但世界因你而不同。",
             "world_reaction": "你的存在悄悄地改變了身邊的每一個人，你的故事在無數人心中留下了印記。"}
        ]
    }
}

# =============================================================================
# 4. 擴充靜態事件庫（40+ 個）
# =============================================================================

STATIC_EVENTS = [
    # 0-6 歲
    {"age_range": (0, 6), "title": "第一次學走路", "description": "你搖搖晃晃地站起來了！",
     "choices": [{"text": "勇敢邁步", "effects": {"strength": 2}}, {"text": "繼續爬行", "effects": {"intelligence": 1}}]},
    {"age_range": (0, 6), "title": "媽媽的擁抱", "description": "你感受到溫暖的擁抱。",
     "choices": [{"text": "緊緊抱住", "effects": {"happiness": 5}}, {"text": "好奇地打量", "effects": {"intelligence": 2}}]},
    {"age_range": (0, 6), "title": "撿到一片樹葉", "description": "你在院子裡撿到一片形狀特別的樹葉。",
     "choices": [{"text": "仔細觀察", "effects": {"intelligence": 2}}, {"text": "當作寶藏收藏", "effects": {"creativity": 2}}]},
    {"age_range": (0, 6), "title": "鄰居的小狗", "description": "鄰居家的小狗跑來舔你的手。",
     "choices": [{"text": "開心地摸牠", "effects": {"happiness": 5, "charisma": 2}}, {"text": "有點害怕地退後", "effects": {"sanity": 2}}]},
    {"age_range": (0, 6), "title": "睡前故事", "description": "媽媽在床邊講了一個關於星星的童話。",
     "choices": [{"text": "認真聽故事", "effects": {"intelligence": 3}}, {"text": "數著星星睡著", "effects": {"happiness": 3}}]},
    # 7-17 歲
    {"age_range": (7, 17), "title": "學校的考試", "description": "期末考到了，你準備好了嗎？",
     "choices": [{"text": "努力讀書", "effects": {"intelligence": 5}}, {"text": "與同學討論", "effects": {"charisma": 3}}]},
    {"age_range": (7, 17), "title": "操場上的爭執", "description": "同學在吵架，好像快打起來了。",
     "choices": [{"text": "上前勸架", "effects": {"charisma": 3, "happiness": 2}}, {"text": "報告老師", "effects": {"intelligence": 2}}]},
    {"age_range": (7, 17), "title": "圖書館的祕密", "description": "你在圖書館發現了一本奇怪的書。",
     "choices": [{"text": "借回家讀", "effects": {"intelligence": 5}}, {"text": "放在原處", "effects": {"sanity": 3}}]},
    {"age_range": (7, 17), "title": "運動會", "description": "學校舉辦運動會，你報名了賽跑。",
     "choices": [{"text": "全力衝刺", "effects": {"strength": 3}}, {"text": "幫同學加油", "effects": {"charisma": 3}}]},
    {"age_range": (7, 17), "title": "第一次騎腳踏車", "description": "你學會騎腳踏車了！",
     "choices": [{"text": "挑戰爬坡", "effects": {"strength": 3}}, {"text": "跟朋友一起騎", "effects": {"happiness": 5}}]},
    {"age_range": (7, 17), "title": "課堂上的提問", "description": "老師問了一個很難的問題。",
     "choices": [{"text": "勇敢舉手回答", "effects": {"intelligence": 3, "charisma": 2}}, {"text": "低頭假裝沒聽見", "effects": {"sanity": 2}}]},
    {"age_range": (7, 17), "title": "書桌裡的祕密", "description": "你發現同學偷放了一張紙條在你書桌裡。",
     "choices": [{"text": "打開看看", "effects": {"creativity": 3}}, {"text": "交給老師", "effects": {"charisma": 2}}]},
    # 18-40 歲
    {"age_range": (18, 40), "title": "第一份工作", "description": "你拿到了第一份薪水，雖然不多但很開心。",
     "choices": [{"text": "存起來", "effects": {"credits": 200}}, {"text": "請朋友吃飯", "effects": {"happiness": 5}}]},
    {"age_range": (18, 40), "title": "愛情的邂逅", "description": "你在咖啡廳遇到一個讓你心動的人。",
     "choices": [{"text": "主動搭話", "effects": {"charisma": 3}}, {"text": "害羞地走開", "effects": {"sanity": 2}}]},
    {"age_range": (18, 40), "title": "同事的背叛", "description": "同事搶了你的功勞，你很生氣。",
     "choices": [{"text": "直接對質", "effects": {"charisma": 2, "happiness": -5}}, {"text": "默默準備證據", "effects": {"intelligence": 5}}]},
    {"age_range": (18, 40), "title": "城市冒險", "description": "你決定來一場說走就走的旅行。",
     "choices": [{"text": "去探索未知的城市", "effects": {"creativity": 5}}, {"text": "在附近走走就好", "effects": {"happiness": 3}}]},
    {"age_range": (18, 40), "title": "職場貴人", "description": "一位前輩願意教你很多東西。",
     "choices": [{"text": "認真學習", "effects": {"intelligence": 5, "credits": 200}}, {"text": "婉拒好意", "effects": {"sanity": 2}}]},
    {"age_range": (18, 40), "title": "夜市的驚喜", "description": "你在夜市吃到前所未有的美食。",
     "choices": [{"text": "開心享受", "effects": {"happiness": 5}}, {"text": "學習怎麼做", "effects": {"creativity": 3}}]},
    {"age_range": (18, 40), "title": "創業的念頭", "description": "你突然有了一個創業的想法。",
     "choices": [{"text": "勇敢嘗試", "effects": {"credits": 500, "creativity": 5}}, {"text": "先打工存錢", "effects": {"credits": 300, "intelligence": 2}}]},
    {"age_range": (18, 40), "title": "面對失敗", "description": "你經歷了一次重大失敗。",
     "choices": [{"text": "重新站起來", "effects": {"strength": 5}}, {"text": "休息一下", "effects": {"sanity": 5}}]},
    # 41-65 歲
    {"age_range": (41, 65), "title": "中年危機", "description": "你突然覺得人生缺少了什麼。",
     "choices": [{"text": "學新技能", "effects": {"creativity": 5}}, {"text": "旅行散心", "effects": {"happiness": 5}}]},
    {"age_range": (41, 65), "title": "孩子的畢業典禮", "description": "你的孩子長大了，看著他們畢業，你百感交集。",
     "choices": [{"text": "感動落淚", "effects": {"happiness": 5}}, {"text": "拍照記錄", "effects": {"creativity": 2}}]},
    {"age_range": (41, 65), "title": "重拾舊愛", "description": "你重新開始了年輕時的興趣。",
     "choices": [{"text": "投入其中", "effects": {"creativity": 5, "happiness": 5}}, {"text": "當作休閒就好", "effects": {"happiness": 3}}]},
    {"age_range": (41, 65), "title": "健康檢查報告", "description": "醫生說你的健康有些問題。",
     "choices": [{"text": "改變生活習慣", "effects": {"health": 10}}, {"text": "繼續過日子", "effects": {"sanity": -5}}]},
    {"age_range": (41, 65), "title": "老友重逢", "description": "你遇到了年輕時的好朋友。",
     "choices": [{"text": "敘舊暢聊", "effects": {"happiness": 5, "charisma": 2}}, {"text": "交換聯絡方式", "effects": {"charisma": 2}}]},
    {"age_range": (41, 65), "title": "職業轉折", "description": "你面臨職業生涯的重大抉擇。",
     "choices": [{"text": "勇敢轉行", "effects": {"credits": 300, "creativity": 5}}, {"text": "安於現狀", "effects": {"sanity": 3}}]},
    {"age_range": (41, 65), "title": "社區貢獻", "description": "社區需要人幫忙組織活動。",
     "choices": [{"text": "接下任務", "effects": {"charisma": 5, "happiness": 5}}, {"text": "捐錢就好", "effects": {"credits": -200}}]},
    {"age_range": (41, 65), "title": "失落的夢想", "description": "你想起年輕時放棄的夢想。",
     "choices": [{"text": "重新追夢", "effects": {"creativity": 5, "happiness": 5}}, {"text": "把它寫成小說", "effects": {"creativity": 5}}]},
    # 66+ 歲
    {"age_range": (66, 120), "title": "養老院的棋局", "description": "你在養老院下棋，對手是個老手。",
     "choices": [{"text": "認真下棋", "effects": {"intelligence": 3}}, {"text": "邊下邊聊", "effects": {"charisma": 3}}]},
    {"age_range": (66, 120), "title": "孫子的來訪", "description": "孫子來看你，你很高興。",
     "choices": [{"text": "講故事給孫子聽", "effects": {"happiness": 5}}, {"text": "玩遊戲", "effects": {"creativity": 3}}]},
    {"age_range": (66, 120), "title": "人生的回顧", "description": "你開始寫自己的回憶錄。",
     "choices": [{"text": "詳細記錄", "effects": {"creativity": 5, "happiness": 3}}, {"text": "只記重點", "effects": {"intelligence": 3}}]},
    {"age_range": (66, 120), "title": "花園的樂趣", "description": "你喜歡在花園裡種花。",
     "choices": [{"text": "照顧更多花", "effects": {"happiness": 5}}, {"text": "教鄰居種花", "effects": {"charisma": 3}}]},
    {"age_range": (66, 120), "title": "最後一課", "description": "你受邀去學校分享人生經驗。",
     "choices": [{"text": "誠摯分享", "effects": {"charisma": 5, "happiness": 5}}, {"text": "簡單講講", "effects": {"intelligence": 2}}]},
    {"age_range": (66, 120), "title": "與遺憾和解", "description": "你終於放下了某些遺憾。",
     "choices": [{"text": "完全放下", "effects": {"sanity": 5, "happiness": 5}}, {"text": "寫成一首詩", "effects": {"creativity": 5}}]},
    {"age_range": (66, 120), "title": "最後的旅行", "description": "你決定再出去走走看看。",
     "choices": [{"text": "去想去的地方", "effects": {"happiness": 5}}, {"text": "在附近散步", "effects": {"health": 2}}]},
    {"age_range": (66, 120), "title": "傳承", "description": "你把自己的技能教給了年輕人。",
     "choices": [{"text": "認真傳授", "effects": {"charisma": 5, "happiness": 5}}, {"text": "留筆記", "effects": {"intelligence": 3}}]},
    # 通用（任何年齡）
    {"age_range": (0, 120), "title": "神祕的禮物", "description": "你收到了一份沒有署名的禮物。",
     "choices": [{"text": "打開看看", "effects": {"luck": 5}}, {"text": "交給警察", "effects": {"charisma": 2}}]},
    {"age_range": (0, 120), "title": "流浪貓", "description": "一隻流浪貓跟著你回家。",
     "choices": [{"text": "收留牠", "effects": {"happiness": 5}}, {"text": "餵完就離開", "effects": {"charisma": 2}}]},
    {"age_range": (0, 120), "title": "意外的收穫", "description": "你在地上撿到一張彩券。",
     "choices": [{"text": "試試手氣", "effects": {"luck": 5, "credits": 300}}, {"text": "直接扔掉", "effects": {"sanity": 2}}]},
    {"age_range": (0, 120), "title": "陌生人的善意", "description": "一位陌生人幫了你一個大忙。",
     "choices": [{"text": "表達感謝", "effects": {"charisma": 3, "happiness": 3}}, {"text": "記在心裏", "effects": {"sanity": 2}}]},
    {"age_range": (0, 120), "title": "夢境的啟示", "description": "你昨晚做了一個奇怪的夢。",
     "choices": [{"text": "記錄下來", "effects": {"creativity": 3}}, {"text": "忘記就好", "effects": {"sanity": 2}}]},
    {"age_range": (0, 120), "title": "幸運的一天", "description": "今天一切都特別順利！",
     "choices": [{"text": "把握運氣", "effects": {"luck": 3, "credits": 100}}, {"text": "分享快樂", "effects": {"happiness": 5}}]},
    {"age_range": (0, 120), "title": "秘密的發現", "description": "你發現了一個隱藏的角落。",
     "choices": [{"text": "深入探索", "effects": {"creativity": 5}}, {"text": "記住位置", "effects": {"intelligence": 3}}]},
    {"age_range": (0, 120), "title": "與老朋友聯繫", "description": "你想起了很久沒聯絡的朋友。",
     "choices": [{"text": "主動聯絡", "effects": {"charisma": 5, "happiness": 5}}, {"text": "默默想念", "effects": {"sanity": 2}}]},
]

# =============================================================================
# 5. 資料模型
# =============================================================================

class Player:
    def __init__(self, name: str):
        self.name = name
        self.age = 0
        self.health = 50
        self.intelligence = 30
        self.strength = 30
        self.charisma = 30
        self.luck = 30
        self.sanity = 50
        self.creativity = 30
        self.happiness = 50
        self.credits = 100
        self.relationships: Dict[str, int] = {}
        self.inventory: List[Dict] = []
        self.flags: Set[str] = set()
        self.action_points = 5
        self.year_actions = 0
        self.traits: List[str] = []
        self.life_achievements: List[str] = []
        self.story_memory: List[str] = []
        self.current_scene = "origin"
        self.death_reason = ""
        self.game_over = False
        self.pending_hidden_events: List[Dict] = []
        self.fatigue = 0
        # 圖鑑記錄
        self.unlocked_endings: List[str] = []
        self.unlocked_hidden_events: List[str] = []

    def get_power_level(self) -> str:
        total = (self.health + self.intelligence + self.strength + self.charisma +
                 self.luck + self.sanity + self.creativity) / 7
        if total >= 90: return "織網真神"
        elif total >= 75: return "半神"
        elif total >= 60: return "傳奇"
        elif total >= 45: return "超凡"
        else: return "凡人"

    def get_title(self) -> str:
        titles = []
        if self.credits >= 100000: titles.append("巨富")
        if self.age >= 80: titles.append("長壽")
        if "time_weave" in self.flags: titles.append("時空行者")
        if "dimension_weave" in self.flags: titles.append("維度旅者")
        if "consciousness_web" in self.flags: titles.append("數位永生")
        if len(self.relationships) >= 5: titles.append("交友廣泛")
        if self.strength >= 80: titles.append("力士")
        if self.intelligence >= 80: titles.append("智者")
        if self.luck >= 80: titles.append("幸運星")
        if self.creativity >= 80: titles.append("創造者")
        if self.sanity >= 80: titles.append("心如明鏡")
        if not titles: titles.append("凡人")
        return ", ".join(titles)

    def add_item(self, item: Dict):
        self.inventory.append(item.copy())

    def remove_item(self, item_id: str) -> bool:
        for i, item in enumerate(self.inventory):
            if item.get("id") == item_id:
                del self.inventory[i]
                return True
        return False

    def use_item(self, item_id: str) -> Optional[Dict]:
        for i, item in enumerate(self.inventory):
            if item.get("id") == item_id:
                effect = item.get("effect", {})
                del self.inventory[i]
                return effect
        return None

# =============================================================================
# 6. AI 服務
# =============================================================================

CONFIG_FILE = "config_gui.json"
DEFAULT_CONFIG = {
    "api_key": "",
    "base_url": "https://api.openai.com/v1",
    "model": "gpt-3.5-turbo",
    "last_played": ""
}

SAFETY_INSTRUCTION = (
    "嚴禁生成任何涉及色情、暴力（除了遊戲內必要的戰鬥描述但不得血腥）、歧視、仇恨言論、"
    "髒話或不當內容。所有內容必須積極、健康，適合全年齡層。"
)

class AIService:
    def __init__(self, api_key: str = "", base_url: str = "", model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.enabled = bool(api_key and base_url)
        self.last_error = ""

    def _call_api(self, messages: List[Dict], temperature=0.8, max_tokens=500):
        if not self.enabled:
            self.last_error = "API 未啟用"
            return None
        try:
            url = f"{self.base_url}/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'),
                                         headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=30) as response:
                resp_data = json.loads(response.read().decode('utf-8'))
                if 'choices' in resp_data and len(resp_data['choices']) > 0:
                    content = resp_data['choices'][0].get('message', {}).get('content', '')
                    if content:
                        return content.strip()
                self.last_error = "無法解析 API 回傳"
                return None
        except urllib.error.URLError as e:
            self.last_error = f"網路錯誤: {e.reason}"
            return None
        except urllib.error.HTTPError as e:
            self.last_error = f"HTTP {e.code}: {e.reason}"
            return None
        except Exception as e:
            self.last_error = f"錯誤: {str(e)}"
            return None

    def _safe_generate(self, system_prompt: str, user_prompt: str, temperature=0.8, max_tokens=500) -> Optional[str]:
        full_system = f"{system_prompt}\n{SAFETY_INSTRUCTION}"
        messages = [
            {"role": "system", "content": full_system},
            {"role": "user", "content": user_prompt}
        ]
        return self._call_api(messages, temperature, max_tokens)

    def generate_story_event(self, player: Player, scene: str):
        if not self.enabled:
            return None
        context = f"目前狀態：年齡{player.age}，健康{player.health}，智力{player.intelligence}，力量{player.strength}，魅力{player.charisma}，運氣{player.luck}，理智{player.sanity}，創造力{player.creativity}，金錢{player.credits}，旗標{list(player.flags)}，場景{scene}。\n世界觀：{WORLD_BACKGROUND[:200]}\n請生成一個事件（JSON格式），包含 title, description, choices（每個choice含 text 和 effects）。"
        resp = self._safe_generate("你是遊戲劇情生成器，回傳JSON。", context, temperature=0.9, max_tokens=600)
        if not resp:
            return None
        try:
            m = re.search(r'\{.*\}', resp, re.DOTALL)
            return json.loads(m.group()) if m else None
        except:
            self.last_error = "AI 回傳無法解析為 JSON"
            return None

    def generate_npc_dialogue(self, player: Player, npc_id: str, context: str = ""):
        if not self.enabled:
            return f"{KEY_NPCS.get(npc_id, {}).get('name', '神秘人')}默默地看著你。"
        npc = KEY_NPCS.get(npc_id, {})
        rep = player.relationships.get(npc_id, 0)
        level = "友好" if rep > 30 else "中立" if rep > -10 else "敵意"
        prompt = f"NPC：{npc.get('name')}，性格：{npc.get('personality')}，好感度：{rep}({level})，情境：{context}。請生成一段20-50字的對話。"
        resp = self._safe_generate("你是角色扮演助手。", prompt, temperature=0.8, max_tokens=100)
        return resp or f"{npc.get('name', '神秘人')}沉默地凝視著你。"

    def generate_scene_description(self, player: Player, scene_id: str):
        if not self.enabled:
            return SCENE_FRAMEWORK.get(scene_id, {}).get("description", "")
        scene = SCENE_FRAMEWORK.get(scene_id, {})
        prompt = f"場景：{scene.get('name')}，玩家年齡{player.age}，健康{player.health}，理智{player.sanity}。請生成50-80字生動描述。"
        resp = self._safe_generate("你是場景描述生成器。", prompt, temperature=0.7, max_tokens=100)
        return resp or scene.get("description", "")

    def generate_death_narrative(self, player: Player):
        if not self.enabled:
            return "你在一場意外中離開了這個世界。"
        prompt = f"角色死亡，年齡{player.age}，財富{player.credits}，成就{player.life_achievements}。請生成30-50字詩意敘事。"
        resp = self._safe_generate("你是詩意敘事生成器。", prompt, temperature=0.8, max_tokens=150)
        return resp or "你的故事在此刻畫上了句號。"

    def generate_epic_moment(self, player: Player, achievement: str):
        if not self.enabled:
            return f"你達成了 {achievement}！"
        prompt = f"達成成就：{achievement}，實力等級{player.get_power_level()}。請生成20-30字史詩描述。"
        resp = self._safe_generate("你是史詩時刻生成器。", prompt, temperature=0.9, max_tokens=80)
        return resp or f"你達成了 {achievement}！世界在你腳下顫抖。"

    def generate_ending_epilogue(self, player: Player, ending: Dict):
        if not self.enabled:
            return ending.get("desc", "")
        prompt = f"結局：{ending.get('name')}，年齡{player.age}，財富{player.credits}，實力{player.get_power_level()}，成就{player.life_achievements}。請生成50-100字史詩描述。"
        resp = self._safe_generate("你是史詩結局生成器。", prompt, temperature=0.8, max_tokens=200)
        return resp or ending.get("desc", "")

    def generate_work_scenario(self, player: Player) -> Dict:
        if not self.enabled:
            return self._static_work_scenario(player)

        age = player.age
        if age <= 6:
            age_group = "幼兒（0-6歲）"
            work_hint = "做家務、幫忙整理、學習生活技能"
        elif age <= 17:
            age_group = "青少年（7-17歲）"
            work_hint = "學校打工、幫鄰居跑腿、協助家務"
        elif age <= 40:
            age_group = "青年（18-40歲）"
            work_hint = "正職工作、創業、專業技能勞動"
        elif age <= 65:
            age_group = "中年（41-65歲）"
            work_hint = "資深工作、管理職、顧問"
        else:
            age_group = "老年（66歲以上）"
            work_hint = "輕度勞動、傳承經驗、社區服務"

        prompt = f"""
玩家年齡：{player.age}歲（{age_group}）
玩家屬性：健康{player.health}，智力{player.intelligence}，力量{player.strength}，魅力{player.charisma}，運氣{player.luck}
當前場景：{player.current_scene}

請根據年齡段，生成一段生動、有趣的工作敘事（40-80字）。
敘事應描述玩家做了什麼工作，並且獲得多少信用點報酬。
回傳格式為 JSON：
{{"description": "工作敘事", "income": 數字}}
"""
        resp = self._safe_generate("你是遊戲工作場景生成器。", prompt, temperature=0.8, max_tokens=200)
        if not resp:
            return self._static_work_scenario(player)

        try:
            m = re.search(r'\{.*\}', resp, re.DOTALL)
            if m:
                data = json.loads(m.group())
                desc = data.get("description", "")
                income = data.get("income", 0)
                if desc and isinstance(income, int):
                    return {"description": desc, "income": income}
        except:
            pass
        return self._static_work_scenario(player)

    def _static_work_scenario(self, player: Player) -> Dict:
        age = player.age
        base_income = 50 + age * 2 + random.randint(0, 20)
        if age <= 6:
            desc = f"你幫媽媽整理房間，得到了 {base_income} 信用點零用錢。"
        elif age <= 17:
            desc = f"你幫鄰居遛狗，得到了 {base_income} 信用點報酬。"
        elif age <= 40:
            desc = f"你今天完成了一個專案，獲得了 {base_income} 信用點薪資。"
        elif age <= 65:
            desc = f"你以顧問身份提供建議，獲得了 {base_income} 信用點酬勞。"
        else:
            desc = f"你整理了花園，鄰居送你 {base_income} 信用點表示感謝。"
        return {"description": desc, "income": base_income}

# =============================================================================
# 7. 遊戲引擎（含圖鑑系統）
# =============================================================================

class GameEngine:
    def __init__(self, ai: AIService):
        self.ai = ai
        self.player: Optional[Player] = None
        self.game_over = False
        self.ending_text = ""
        self.ending_title = ""
        self.ending_version_name = ""
        self.world_reaction = ""
        self.year = 0
        self.current_scene = "origin"
        self.unlocked_tech = None
        self.last_event = None
        self.epic_achievement = None
        self.epic_text = ""
        self.view_mode = "story"
        self.shop_items = SHOP_ITEMS.copy()
        self.static_events = STATIC_EVENTS.copy()
        # 圖鑑狀態（全域記錄）
        self.unlocked_endings: Set[str] = set()
        self.unlocked_hidden_events: Set[str] = set()
        self._load_codex()

    def _load_codex(self):
        """載入圖鑑記錄（從檔案）"""
        try:
            if os.path.exists("codex_data.json"):
                with open("codex_data.json", 'r') as f:
                    data = json.load(f)
                    self.unlocked_endings = set(data.get("endings", []))
                    self.unlocked_hidden_events = set(data.get("hidden_events", []))
        except:
            pass

    def _save_codex(self):
        """儲存圖鑑記錄"""
        try:
            with open("codex_data.json", 'w') as f:
                json.dump({
                    "endings": list(self.unlocked_endings),
                    "hidden_events": list(self.unlocked_hidden_events)
                }, f, indent=2)
        except:
            pass

    def unlock_ending(self, ending_id: str):
        """解鎖結局並記錄"""
        if ending_id not in self.unlocked_endings:
            self.unlocked_endings.add(ending_id)
            self._save_codex()
            if self.player:
                self.player.unlocked_endings.append(ending_id)

    def unlock_hidden_event(self, event_id: str):
        """解鎖隱藏事件並記錄"""
        if event_id not in self.unlocked_hidden_events:
            self.unlocked_hidden_events.add(event_id)
            self._save_codex()
            if self.player:
                self.player.unlocked_hidden_events.append(event_id)

    def get_codex_data(self) -> Dict:
        """取得圖鑑資料（供顯示用）"""
        return {
            "endings": {
                "all": list(ENDING_DEFINITIONS.keys()),
                "unlocked": list(self.unlocked_endings)
            },
            "hidden_events": {
                "all": list(HIDDEN_EVENT_DEFINITIONS.keys()),
                "unlocked": list(self.unlocked_hidden_events)
            }
        }

    def create_player(self, name: str, attributes: Dict, traits: List[str]) -> Player:
        p = Player(name)
        p.health = attributes.get("health", 50)
        p.intelligence = attributes.get("intelligence", 30)
        p.strength = attributes.get("strength", 30)
        p.charisma = attributes.get("charisma", 30)
        p.luck = attributes.get("luck", 30)
        p.sanity = attributes.get("sanity", 50)
        p.creativity = attributes.get("creativity", 30)
        p.traits = traits
        for t in traits:
            if t == "天才": p.intelligence += 20
            elif t == "大力士": p.strength += 15
            elif t == "萬人迷": p.charisma += 15
            elif t == "幸運兒": p.luck += 25
            elif t == "發明家": p.creativity += 20
            elif t == "靈媒": p.sanity += 10
            elif t == "體弱多病": p.health -= 15
            elif t == "社交恐懼": p.charisma -= 15
            elif t == "偏執狂": p.sanity -= 15
            elif t == "賭徒": p.luck -= 10
            elif t == "外星人過敏": p.health -= 10
            elif t == "時間感知障礙": p.sanity -= 10
        for attr in ['health','intelligence','strength','charisma','luck','sanity','creativity']:
            setattr(p, attr, max(0, min(100, getattr(p, attr))))
        p.story_memory.append("你在命運起點醒來。")
        p.current_scene = "origin"
        # 繼承圖鑑記錄
        p.unlocked_endings = list(self.unlocked_endings)
        p.unlocked_hidden_events = list(self.unlocked_hidden_events)
        self.player = p
        self.game_over = False
        self.year = 0
        self.current_scene = "origin"
        return p

    def next_year(self):
        if self.game_over or not self.player: return
        p = self.player
        p.age += 1
        self.year += 1
        p.action_points = 5
        p.year_actions = 0
        p.health = max(0, p.health - random.randint(1, 3))
        p.sanity = max(0, p.sanity - random.randint(0, 2))
        p.happiness = max(0, min(100, p.happiness + random.randint(-5, 5)))
        self.update_scene()
        self.check_hidden_events()
        self.trigger_event()
        self.check_tech_unlock()
        self.check_death()
        if not self.game_over:
            p.story_memory.append(f"第{p.age}年：繼續前行。")
            if len(p.story_memory) > 20: p.story_memory = p.story_memory[-20:]

    def update_scene(self):
        p = self.player
        if p.age <= 5: self.current_scene = "origin"
        elif p.age <= 15: self.current_scene = "village"
        elif p.age <= 30: self.current_scene = "forest" if "forest_visited" in p.flags else "village"
        elif p.age <= 50: self.current_scene = "city" if "city_visited" in p.flags else "forest"
        elif p.age <= 70: self.current_scene = "ruins" if "ruins_visited" in p.flags else "city"
        elif p.age <= 90: self.current_scene = "rift_realm" if "rift_realm_visited" in p.flags else "ruins"
        else: self.current_scene = "core"
        p.current_scene = self.current_scene

    def check_hidden_events(self):
        if not self.player: return
        p = self.player

        # 負面隱藏事件
        if "installed_prosthetic" in p.flags and p.age >= 50:
            if random.random() < 0.05:
                self.unlock_hidden_event("prosthetic_malfunction")
                tech = next((t for t in TECH_TREE if t.get("flag") == "installed_prosthetic"), None)
                solution = tech.get("solution", "請前往機械師處檢修。") if tech else "請前往機械師處檢修。"
                solution_effects = tech.get("solution_effects", {"health": 5, "credits": -500}) if tech else {"health": 5, "credits": -500}
                self.trigger_hidden_event({
                    "id": "prosthetic_malfunction",
                    "title": "義肢異常",
                    "description": "你感到義肢傳來異樣的震動，似乎有自主意識…",
                    "effects": {"health": -10, "sanity": -5},
                    "solution": solution,
                    "solution_effects": solution_effects,
                    "is_solvable": True
                })
        if "brain_weave" in p.flags and p.age >= 45:
            if random.random() < 0.03:
                self.unlock_hidden_event("brain_overload")
                self.trigger_hidden_event({
                    "id": "brain_overload",
                    "title": "腦機過載",
                    "description": "你開始接收到不屬於自己的記憶片段，腦中一片混亂。",
                    "effects": {"sanity": -15, "intelligence": 5},
                    "solution": "進行冥想調節（消耗 1 行動點，理智 +10）",
                    "solution_effects": {"sanity": 10},
                    "is_solvable": True
                })

        # 正面隱藏事件
        if "installed_prosthetic" in p.flags and p.age < 40:
            if random.random() < 0.02:
                self.unlock_hidden_event("prosthetic_adapt")
                self.trigger_hidden_event({
                    "id": "prosthetic_adapt",
                    "title": "義肢適應",
                    "description": "你的身體完全適應了義肢，動作變得更加流暢。",
                    "effects": {"health": 10, "strength": 5},
                    "is_solvable": False,
                    "is_positive": True
                })
        if "brain_weave" in p.flags and p.age < 45:
            if random.random() < 0.02:
                self.unlock_hidden_event("brain_optimize")
                self.trigger_hidden_event({
                    "id": "brain_optimize",
                    "title": "腦機優化",
                    "description": "你的腦機介面自動優化了神經連結，思維更加清晰。",
                    "effects": {"intelligence": 10, "sanity": 5},
                    "is_solvable": False,
                    "is_positive": True
                })
        if "memory_web" in p.flags:
            if random.random() < 0.01:
                self.unlock_hidden_event("memory_boost")
                self.trigger_hidden_event({
                    "id": "memory_boost",
                    "title": "記憶強化",
                    "description": "你的記憶雲端自動整理，喚醒了遺忘的靈感。",
                    "effects": {"creativity": 10},
                    "is_solvable": False,
                    "is_positive": True
                })

    def trigger_hidden_event(self, event_data: Dict):
        if not self.player: return
        if event_data.get("is_solvable", True) and "solution" not in event_data:
            event_data["solution"] = "嘗試與事件相關的人溝通或使用物品。"
            event_data["solution_effects"] = {"health": 5}
        self.player.pending_hidden_events.append(event_data)

    def trigger_event(self):
        if self.game_over or not self.player: return
        p = self.player

        if p.pending_hidden_events:
            self.last_event = p.pending_hidden_events.pop(0)
            self.last_event["is_hidden"] = True
            return

        if p.age <= 2: return

        if self.ai.enabled and random.random() < 0.3:
            evt = self.ai.generate_story_event(p, self.current_scene)
            if evt:
                self.last_event = evt
                p.flags.add(f"{self.current_scene}_visited")
                return

        eligible = [e for e in self.static_events if e["age_range"][0] <= p.age <= e["age_range"][1]]
        if eligible:
            evt = random.choice(eligible)
            self.last_event = evt
            return

        generic = [e for e in self.static_events if e["age_range"] == (0, 120)]
        if generic:
            self.last_event = random.choice(generic)

    def check_tech_unlock(self):
        for tech in TECH_TREE:
            if tech["age"] == self.player.age:
                self.unlocked_tech = tech
                return
        self.unlocked_tech = None

    def check_death(self):
        p = self.player
        if p.health <= 0: self.trigger_death("健康耗盡")
        elif p.sanity <= 0: self.trigger_death("理智崩潰")
        elif p.luck <= 0: self.trigger_death("運氣枯竭")
        elif "installed_prosthetic" in p.flags and p.age >= 50 and random.random() < 0.02:
            self.trigger_death("義肢失控奪取生命")
        elif random.random() < 0.01 and p.age > 10:
            self.trigger_death("命運無常")

    def trigger_death(self, cause: str):
        if self.game_over: return
        self.game_over = True
        narrative = self.ai.generate_death_narrative(self.player)
        self.player.death_reason = f"{cause} - {narrative}"
        self.check_ending()

    def check_ending(self):
        p = self.player
        ending_map = [
            ("legend", lambda: p.age >= 100 and p.credits >= 100000),
            ("madman", lambda: p.sanity < 10 and p.age >= 80),
            ("tycoon", lambda: p.credits >= 500000),
            ("hermit", lambda: p.age >= 60 and sum(p.relationships.values()) < 10),
            ("digital_ghost", lambda: "consciousness_web" in p.flags),
            ("time_rogue", lambda: "time_weave" in p.flags),
            ("balance", lambda: p.get_power_level() == "半神" and len(p.flags) >= 10 and p.age >= 60),
        ]

        for ending_id, condition in ending_map:
            if condition():
                self.unlock_ending(ending_id)
                self.ending_title = ENDINGS_NAMES.get(ending_id, ending_id)
                self._select_ending_version(ending_id, p)
                return

        self.unlock_ending("default")
        self.ending_title = "凡人織者"
        self._select_ending_version("default", p)

    def _select_ending_version(self, ending_id: str, player: Player):
        versions = ENDING_NARRATIVES.get(ending_id, {}).get("versions", [])
        if not versions:
            self.ending_text = "你度過了一段普通而真實的人生。"
            self.ending_version_name = "凡人"
            self.world_reaction = "世界繼續轉動。"
            return

        for version in versions:
            try:
                if version["condition"](player):
                    self.ending_text = version["text"]
                    self.ending_version_name = version["name"]
                    self.world_reaction = version.get("world_reaction", "世界繼續轉動。")
                    return
            except:
                continue

        last = versions[-1]
        self.ending_text = last["text"]
        self.ending_version_name = last["name"]
        self.world_reaction = last.get("world_reaction", "世界繼續轉動。")

    def perform_action(self, action: Dict):
        if self.game_over: return
        p = self.player
        if p.action_points <= 0: return
        cost_pts = action.get("points", 1)
        cost_credits = action.get("credits", 0)
        if p.credits < cost_credits: return
        p.action_points -= cost_pts
        p.credits -= cost_credits
        p.year_actions += 1
        effects = action.get("effects", {})
        for attr, val in effects.items():
            if attr == "flags":
                for f in val: p.flags.add(f)
            elif attr == "credits": p.credits += val
            elif attr == "relationships":
                for npc, delta in val.items(): p.relationships[npc] = p.relationships.get(npc, 0) + delta
            else:
                current = getattr(p, attr, 0)
                setattr(p, attr, max(0, min(100, current + val)))
        income = action.get("income", 0)
        if income: p.credits += income
        self.check_achievements()
        if p.action_points <= 0: self.next_year()

    def check_achievements(self):
        p = self.player
        achievements = []
        if p.health >= 90: achievements.append("鋼鐵之軀")
        if p.intelligence >= 90: achievements.append("超級大腦")
        if p.strength >= 90: achievements.append("力拔山兮")
        if p.charisma >= 90: achievements.append("萬人迷")
        if p.luck >= 90: achievements.append("天選之人")
        if p.sanity >= 90: achievements.append("心如明鏡")
        if p.creativity >= 90: achievements.append("創世者")
        if p.credits >= 100000: achievements.append("百萬富翁")
        if p.age >= 80: achievements.append("長壽星")
        if len(p.flags) >= 15: achievements.append("世界探索者")
        for ach in achievements:
            if ach not in p.life_achievements:
                p.life_achievements.append(ach)
                self.epic_achievement = ach
                self.epic_text = self.ai.generate_epic_moment(p, ach)
                return
        self.epic_achievement = None
        self.epic_text = ""

    def do_work(self) -> Dict:
        p = self.player
        result = self.ai.generate_work_scenario(p)
        desc = result.get("description", "你努力工作了一天。")
        income = result.get("income", 50 + p.age * 2)
        if p.age <= 6:
            income = min(income, 100)
        elif p.age <= 17:
            income = min(income, 200)
        elif p.age <= 40:
            income = max(income, 100)
        elif p.age <= 65:
            income = max(income, 150)
        else:
            income = max(income, 80)
        bonus = max(0, (p.intelligence + p.strength) // 10)
        income += bonus
        p.fatigue += random.randint(1, 5)
        return {"description": desc, "income": income}

    def get_available_actions(self) -> List[Dict]:
        actions = [
            {"id": "walk", "name": "漫步", "points": 1, "credits": 0, "effects": {"happiness": 3, "health": 2}},
            {"id": "read", "name": "研讀", "points": 1, "credits": 0, "effects": {"intelligence": 2, "creativity": 1}},
            {"id": "work", "name": "工作", "points": 2, "credits": 0, "effects": {}, "is_work": True},
            {"id": "social", "name": "交際", "points": 1, "credits": random.randint(0, 50),
             "effects": {"charisma": 2, "happiness": 2}},
            {"id": "explore", "name": "探索", "points": 2, "credits": 0,
             "effects": {"flags": ["explored_" + self.current_scene], "wisdom": 5}},
        ]
        if self.unlocked_tech and self.player.credits >= self.unlocked_tech["cost"]:
            tech = self.unlocked_tech
            actions.append({
                "id": "tech_upgrade",
                "name": f"🔬 安裝：{tech['name']}",
                "points": 2,
                "credits": tech['cost'],
                "effects": tech['effects'],
                "flags": [tech['flag']],
                "is_tech": True
            })
        return actions

    def apply_event_choice(self, choice: Dict):
        p = self.player
        effects = choice.get("effects", {})
        for attr, val in effects.items():
            if attr == "flags":
                for f in val: p.flags.add(f)
            elif attr == "credits": p.credits += val
            elif attr == "relationships":
                for npc, delta in val.items(): p.relationships[npc] = p.relationships.get(npc, 0) + delta
            else:
                current = getattr(p, attr, 0)
                setattr(p, attr, max(0, min(100, current + val)))
        p.story_memory.append(f"你選擇了：{choice.get('text', '未知')}")
        self.check_death()
        if not self.game_over: self.check_achievements()

    def get_scene_description(self) -> str:
        return self.ai.generate_scene_description(self.player, self.current_scene)

    def get_scene_npcs(self) -> List[str]:
        return SCENE_FRAMEWORK.get(self.current_scene, {}).get("npcs", [])

    def buy_item(self, item_id: str) -> bool:
        if not self.player: return False
        for item in self.shop_items:
            if item["id"] == item_id:
                if self.player.credits >= item["price"]:
                    self.player.credits -= item["price"]
                    self.player.add_item(item)
                    return True
        return False

    def sell_item(self, item_id: str) -> bool:
        if not self.player: return False
        for i, item in enumerate(self.player.inventory):
            if item.get("id") == item_id:
                price = item.get("price", 50) // 2
                self.player.credits += price
                del self.player.inventory[i]
                return True
        return False

    def use_item_from_inventory(self, item_id: str) -> Optional[Dict]:
        if not self.player: return None
        return self.player.use_item(item_id)

# 結局名稱對照
ENDINGS_NAMES = {
    "legend": "命運織主",
    "madman": "裂變狂人",
    "tycoon": "織網巨鱷",
    "hermit": "絲線隱者",
    "digital_ghost": "織網幽靈",
    "time_rogue": "時空織者",
    "balance": "織網平衡者",
    "default": "凡人織者"
}

# =============================================================================
# 8. GUI 應用程式（含圖鑑按鈕）
# =============================================================================

class GameApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"命運織網 - 人生模擬 RPG  v{VERSION}")
        self.root.geometry("1050x780")
        self.root.minsize(850, 650)
        self.root.configure(bg="#1a1a2e")

        self.config = self.load_config()
        self.ai = AIService(
            api_key=self.config.get("api_key", ""),
            base_url=self.config.get("base_url", "https://api.openai.com/v1"),
            model=self.config.get("model", "gpt-3.5-turbo")
        )
        self.engine = GameEngine(self.ai)

        self.event_choices = []
        self.waiting_for_event = False
        self.tutorial_step = 0
        self.in_tutorial = False
        self.view_mode = "story"

        self.setup_ui()
        self.show_welcome()

    def load_config(self) -> Dict:
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)

    # -------------------------------------------------------------------------
    # UI 佈局
    # -------------------------------------------------------------------------
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        # Info Bar
        self.info_bar = tk.Frame(main_frame, bg="#1a1a2e", height=80)
        self.info_bar.pack(fill=tk.X, pady=(0, 5))
        self.info_bar.pack_propagate(False)

        self.status_label = tk.Label(self.info_bar, text="", font=('Arial', 10),
                                     fg="#a0d0ff", bg="#1a1a2e", justify=tk.LEFT)
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.power_label = tk.Label(self.info_bar, text="", font=('Arial', 10, 'bold'),
                                    fg="#ffd700", bg="#1a1a2e")
        self.power_label.pack(side=tk.RIGHT, padx=5)

        # Event Monitor
        self.event_monitor = tk.Frame(main_frame, bg="#0d0d1a")
        self.event_monitor.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.text_area = scrolledtext.ScrolledText(self.event_monitor, wrap=tk.WORD,
                                                   font=('Consolas', 11),
                                                   bg="#0d0d1a", fg="#e0e0e0",
                                                   insertbackground="#f0c040",
                                                   relief=tk.FLAT, borderwidth=0)
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.tag_configure("title", foreground="#f0c040", font=('Arial', 14, 'bold'))
        self.text_area.tag_configure("highlight", foreground="#ff6b6b")
        self.text_area.tag_configure("gold", foreground="#ffd700")
        self.text_area.tag_configure("green", foreground="#51cf66")
        self.text_area.tag_configure("blue", foreground="#4dabf7")
        self.text_area.tag_configure("npc", foreground="#f06595")
        self.text_area.tag_configure("death", foreground="#ff0000", font=('Arial', 12, 'bold'))
        self.text_area.tag_configure("ending", foreground="#ffd700", font=('Arial', 14, 'bold'))
        self.text_area.tag_configure("tutorial", foreground="#00ffff", font=('Arial', 11, 'bold'))
        self.text_area.tag_configure("error", foreground="#ff4444", font=('Arial', 10, 'bold'))
        self.text_area.tag_configure("item", foreground="#ffa94d")
        self.text_area.tag_configure("solution", foreground="#90ee90", font=('Arial', 10, 'bold'))
        self.text_area.tag_configure("world", foreground="#ffa94d", font=('Arial', 10, 'italic'))
        self.text_area.tag_configure("codex", foreground="#ffd700", font=('Arial', 12, 'bold'))

        # 背包模式
        self.inventory_frame = tk.Frame(self.event_monitor, bg="#0d0d1a")
        self.inventory_frame.pack(fill=tk.BOTH, expand=True)
        self.inventory_frame.pack_forget()

        self.inventory_list = scrolledtext.ScrolledText(self.inventory_frame, wrap=tk.WORD,
                                                         font=('Consolas', 11),
                                                         bg="#0d0d1a", fg="#e0e0e0",
                                                         relief=tk.FLAT, borderwidth=0)
        self.inventory_list.pack(fill=tk.BOTH, expand=True)
        self.inventory_list.tag_configure("title", foreground="#f0c040", font=('Arial', 12, 'bold'))
        self.inventory_list.tag_configure("item", foreground="#ffa94d")
        self.inventory_list.tag_configure("info", foreground="#4dabf7")

        # 商店模式
        self.shop_frame = tk.Frame(self.event_monitor, bg="#0d0d1a")
        self.shop_frame.pack(fill=tk.BOTH, expand=True)
        self.shop_frame.pack_forget()

        self.shop_list = scrolledtext.ScrolledText(self.shop_frame, wrap=tk.WORD,
                                                    font=('Consolas', 11),
                                                    bg="#0d0d1a", fg="#e0e0e0",
                                                    relief=tk.FLAT, borderwidth=0)
        self.shop_list.pack(fill=tk.BOTH, expand=True)
        self.shop_list.tag_configure("title", foreground="#f0c040", font=('Arial', 12, 'bold'))
        self.shop_list.tag_configure("item", foreground="#ffa94d")
        self.shop_list.tag_configure("price", foreground="#51cf66")
        self.shop_list.tag_configure("info", foreground="#4dabf7")

        # Action Panel
        self.action_panel = tk.Frame(main_frame, bg="#1a1a2e", height=65)
        self.action_panel.pack(fill=tk.X)
        self.action_panel.pack_propagate(False)

        self.btn1 = tk.Button(self.action_panel, text="", command=lambda: None,
                              font=('Arial', 10), bg="#2a2a4a", fg="white", relief=tk.FLAT)
        self.btn1.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        self.btn2 = tk.Button(self.action_panel, text="", command=lambda: None,
                              font=('Arial', 10), bg="#2a2a4a", fg="white", relief=tk.FLAT)
        self.btn2.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        self.btn3 = tk.Button(self.action_panel, text="", command=lambda: None,
                              font=('Arial', 10), bg="#2a2a4a", fg="white", relief=tk.FLAT)
        self.btn3.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        self.btn4 = tk.Button(self.action_panel, text="", command=lambda: None,
                              font=('Arial', 10), bg="#2a2a4a", fg="white", relief=tk.FLAT)
        self.btn4.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

        self.hide_buttons()

        # Toolbar
        self.toolbar = tk.Frame(main_frame, bg="#1a1a2e", height=30)
        self.toolbar.pack(fill=tk.X, pady=(0, 5))

        self.start_btn = tk.Button(self.toolbar, text="🌟 新人生", command=self.start_new_game,
                                   font=('Arial', 10, 'bold'), bg="#f0c040", fg="#1a1a2e",
                                   relief=tk.FLAT, padx=10)
        self.start_btn.pack(side=tk.LEFT, padx=2)

        self.end_year_btn = tk.Button(self.toolbar, text="⏭ 結束年", command=self.end_year,
                                      font=('Arial', 10), bg="#4a4a6a", fg="white",
                                      relief=tk.FLAT, padx=10, state=tk.DISABLED)
        self.end_year_btn.pack(side=tk.LEFT, padx=2)

        self.inventory_btn = tk.Button(self.toolbar, text="🎒 背包", command=self.toggle_inventory,
                                       font=('Arial', 10), bg="#2a4a6a", fg="white",
                                       relief=tk.FLAT, padx=10, state=tk.DISABLED)
        self.inventory_btn.pack(side=tk.LEFT, padx=2)

        self.shop_btn = tk.Button(self.toolbar, text="🏪 商店", command=self.toggle_shop,
                                  font=('Arial', 10), bg="#4a4a2a", fg="white",
                                  relief=tk.FLAT, padx=10, state=tk.DISABLED)
        self.shop_btn.pack(side=tk.LEFT, padx=2)

        # 圖鑑按鈕
        self.codex_btn = tk.Button(self.toolbar, text="📖 圖鑑", command=self.open_codex,
                                   font=('Arial', 10), bg="#5a3a2a", fg="#ffd700",
                                   relief=tk.FLAT, padx=10)
        self.codex_btn.pack(side=tk.LEFT, padx=2)

        self.settings_btn = tk.Button(self.toolbar, text="⚙️ API", command=self.open_api_settings,
                                      font=('Arial', 10), bg="#3a3a5a", fg="white",
                                      relief=tk.FLAT, padx=10)
        self.settings_btn.pack(side=tk.LEFT, padx=2)

        self.view_label = tk.Label(self.toolbar, text="📖 故事", font=('Arial', 10),
                                   fg="#a0d0ff", bg="#1a1a2e")
        self.view_label.pack(side=tk.RIGHT, padx=5)

        self.action_label = tk.Label(self.toolbar, text="", font=('Arial', 9),
                                     fg="#a0d0ff", bg="#1a1a2e")
        self.action_label.pack(side=tk.RIGHT, padx=5)

    def hide_buttons(self):
        self.btn1.config(text="", command=lambda: None, bg="#2a2a4a")
        self.btn2.config(text="", command=lambda: None, bg="#2a2a4a")
        self.btn3.config(text="", command=lambda: None, bg="#2a2a4a")
        self.btn4.config(text="", command=lambda: None, bg="#2a2a4a")

    def show_action_buttons(self, actions: List[Dict]):
        buttons = [self.btn1, self.btn2, self.btn3, self.btn4]
        for i in range(4):
            if i < len(actions):
                buttons[i].config(text=actions[i]["text"],
                                  command=actions[i]["command"],
                                  bg="#2a2a4a", fg="white")
            else:
                buttons[i].config(text="", command=lambda: None, bg="#2a2a4a")

    def show_event_buttons(self, choices: List[Dict]):
        self.hide_buttons()
        buttons = [self.btn1, self.btn2, self.btn3, self.btn4]
        for i in range(4):
            if i < len(choices):
                buttons[i].config(text=choices[i].get("text", "選擇"),
                                  command=lambda c=choices[i]: self.choose_event(c),
                                  bg="#4a2a4a", fg="#ffd700")
            else:
                buttons[i].config(text="", command=lambda: None, bg="#2a2a4a")

    def set_view_mode(self, mode: str):
        self.view_mode = mode
        self.text_area.pack_forget()
        self.inventory_frame.pack_forget()
        self.shop_frame.pack_forget()

        if mode == "story":
            self.text_area.pack(fill=tk.BOTH, expand=True)
            self.view_label.config(text="📖 故事")
        elif mode == "inventory":
            self.inventory_frame.pack(fill=tk.BOTH, expand=True)
            self.view_label.config(text="🎒 背包")
            self.refresh_inventory_view()
        elif mode == "shop":
            self.shop_frame.pack(fill=tk.BOTH, expand=True)
            self.view_label.config(text="🏪 商店")
            self.refresh_shop_view()

    def refresh_inventory_view(self):
        self.inventory_list.config(state='normal')
        self.inventory_list.delete(1.0, tk.END)
        p = self.engine.player
        if not p:
            self.inventory_list.insert(tk.END, "尚無角色")
            self.inventory_list.config(state='normal')
            return
        self.inventory_list.insert(tk.END, "🎒 背包物品\n", "title")
        self.inventory_list.insert(tk.END, "─" * 30 + "\n", "info")
        if not p.inventory:
            self.inventory_list.insert(tk.END, "（空的）\n", "info")
        else:
            for i, item in enumerate(p.inventory):
                name = item.get("name", "未知")
                desc = item.get("desc", "")
                self.inventory_list.insert(tk.END, f"{i+1}. {name}", "item")
                if desc:
                    self.inventory_list.insert(tk.END, f" - {desc}", "info")
                self.inventory_list.insert(tk.END, "\n")
        self.inventory_list.config(state='normal')

    def refresh_shop_view(self):
        self.shop_list.config(state='normal')
        self.shop_list.delete(1.0, tk.END)
        p = self.engine.player
        if not p:
            self.shop_list.insert(tk.END, "尚無角色")
            self.shop_list.config(state='normal')
            return
        self.shop_list.insert(tk.END, "🏪 商店\n", "title")
        self.shop_list.insert(tk.END, "─" * 30 + "\n", "info")
        self.shop_list.insert(tk.END, f"你的信用點：{p.credits}\n\n", "price")
        for item in self.engine.shop_items:
            name = item.get("name", "未知")
            desc = item.get("desc", "")
            price = item.get("price", 0)
            self.shop_list.insert(tk.END, f"• {name}", "item")
            self.shop_list.insert(tk.END, f" - {desc}", "info")
            self.shop_list.insert(tk.END, f" (💰{price})\n", "price")
        self.shop_list.config(state='normal')

    # -------------------------------------------------------------------------
    # 圖鑑系統
    # -------------------------------------------------------------------------
    def open_codex(self):
        """開啟圖鑑視窗"""
        win = tk.Toplevel(self.root)
        win.title("📖 圖鑑 - 命運織網")
        win.geometry("700x600")
        win.minsize(600, 400)
        win.configure(bg="#1a1a2e")

        tk.Label(win, text="📖 圖鑑", font=('Arial', 18, 'bold'),
                 fg="#f0c040", bg="#1a1a2e").pack(pady=10)

        # 使用 Notebook 分頁
        notebook = ttk.Notebook(win)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 結局分頁
        ending_frame = tk.Frame(notebook, bg="#0d0d1a")
        notebook.add(ending_frame, text="🏆 結局")

        ending_text = scrolledtext.ScrolledText(ending_frame, wrap=tk.WORD,
                                                 font=('Consolas', 11),
                                                 bg="#0d0d1a", fg="#e0e0e0",
                                                 relief=tk.FLAT, borderwidth=0)
        ending_text.pack(fill=tk.BOTH, expand=True)
        ending_text.tag_configure("title", foreground="#f0c040", font=('Arial', 12, 'bold'))
        ending_text.tag_configure("unlocked", foreground="#51cf66")
        ending_text.tag_configure("locked", foreground="#4a4a6a")
        ending_text.tag_configure("desc", foreground="#a0d0ff")
        ending_text.tag_configure("condition", foreground="#ffa94d")

        # 隱藏事件分頁
        hidden_frame = tk.Frame(notebook, bg="#0d0d1a")
        notebook.add(hidden_frame, text="✨ 隱藏事件")

        hidden_text = scrolledtext.ScrolledText(hidden_frame, wrap=tk.WORD,
                                                font=('Consolas', 11),
                                                bg="#0d0d1a", fg="#e0e0e0",
                                                relief=tk.FLAT, borderwidth=0)
        hidden_text.pack(fill=tk.BOTH, expand=True)
        hidden_text.tag_configure("title", foreground="#f0c040", font=('Arial', 12, 'bold'))
        hidden_text.tag_configure("unlocked", foreground="#51cf66")
        hidden_text.tag_configure("locked", foreground="#4a4a6a")
        hidden_text.tag_configure("desc", foreground="#a0d0ff")
        hidden_text.tag_configure("condition", foreground="#ffa94d")
        hidden_text.tag_configure("positive", foreground="#51cf66")
        hidden_text.tag_configure("negative", foreground="#ff6b6b")

        # 填入資料
        codex_data = self.engine.get_codex_data()

        # 結局
        ending_text.config(state='normal')
        for ending_id in codex_data["endings"]["all"]:
            is_unlocked = ending_id in codex_data["endings"]["unlocked"]
            definition = ENDING_DEFINITIONS.get(ending_id, {})
            status = "✅ 已解鎖" if is_unlocked else "🔒 未解鎖"
            tag = "unlocked" if is_unlocked else "locked"
            ending_text.insert(tk.END, f"{definition.get('name', ending_id)} - {status}\n", tag)
            ending_text.insert(tk.END, f"  📝 {definition.get('description', '')}\n", "desc")
            ending_text.insert(tk.END, f"  📌 條件：{definition.get('condition_text', '未知')}\n", "condition")
            ending_text.insert(tk.END, "\n")
        ending_text.config(state='normal')

        # 隱藏事件
        hidden_text.config(state='normal')
        for event_id in codex_data["hidden_events"]["all"]:
            is_unlocked = event_id in codex_data["hidden_events"]["unlocked"]
            definition = HIDDEN_EVENT_DEFINITIONS.get(event_id, {})
            status = "✅ 已觸發" if is_unlocked else "🔒 未觸發"
            tag = "unlocked" if is_unlocked else "locked"
            pos_neg = "positive" if definition.get("is_positive", True) else "negative"
            type_label = "✨ 增益" if definition.get("is_positive", True) else "⚠️ 危機"
            hidden_text.insert(tk.END, f"{definition.get('name', event_id)} - {status} [{type_label}]\n", tag)
            hidden_text.insert(tk.END, f"  📝 {definition.get('description', '')}\n", "desc")
            hidden_text.insert(tk.END, f"  📌 觸發條件：{definition.get('condition_text', '未知')}\n", "condition")
            hidden_text.insert(tk.END, "\n")
        hidden_text.config(state='normal')

        # 關閉按鈕
        tk.Button(win, text="關閉", command=win.destroy,
                  font=('Arial', 11), bg="#4a4a6a", fg="white", padx=20, pady=5).pack(pady=10)

    # -------------------------------------------------------------------------
    # 按鈕功能
    # -------------------------------------------------------------------------
    def toggle_inventory(self):
        if self.view_mode == "inventory":
            self.set_view_mode("story")
            self.show_actions()
        else:
            self.set_view_mode("inventory")
            self.show_inventory_actions()

    def toggle_shop(self):
        if self.view_mode == "shop":
            self.set_view_mode("story")
            self.show_actions()
        else:
            self.set_view_mode("shop")
            self.show_shop_actions()

    def show_inventory_actions(self):
        p = self.engine.player
        if not p or not p.inventory:
            self.hide_buttons()
            self.btn1.config(text="返回", command=self.toggle_inventory, bg="#4a4a6a", fg="white")
            return
        actions = []
        for i, item in enumerate(p.inventory[:3]):
            actions.append({
                "text": f"使用 {item.get('name', '物品')}",
                "command": lambda it=item: self.use_item(it)
            })
        actions.append({"text": "返回", "command": self.toggle_inventory})
        self.show_action_buttons(actions)

    def use_item(self, item):
        p = self.engine.player
        if not p: return
        effect = p.use_item(item.get("id"))
        if effect:
            for attr, val in effect.items():
                if attr == "flags":
                    for f in val: p.flags.add(f)
                else:
                    current = getattr(p, attr, 0)
                    setattr(p, attr, max(0, min(100, current + val)))
            self.append_text(f"💊 使用了 {item.get('name')}", "gold")
            self.refresh_inventory_view()
            self.update_status()
            self.show_inventory_actions()

    def show_shop_actions(self):
        actions = [
            {"text": "購買", "command": self.buy_selected},
            {"text": "賣出", "command": self.sell_selected},
            {"text": "返回", "command": self.toggle_shop}
        ]
        self.show_action_buttons(actions)

    def buy_selected(self):
        p = self.engine.player
        if not p: return
        items = [f"{item['name']} (💰{item['price']})" for item in self.engine.shop_items]
        items.append("取消")
        choice = simpledialog.askstring("購買物品",
                                         "輸入要購買的物品編號：\n" +
                                         "\n".join([f"{i+1}. {name}" for i, name in enumerate(items)]),
                                         parent=self.root)
        if not choice: return
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(self.engine.shop_items):
                item = self.engine.shop_items[idx]
                if self.engine.buy_item(item["id"]):
                    self.append_text(f"🛒 購買了 {item['name']}", "green")
                    self.refresh_shop_view()
                    self.update_status()
                else:
                    self.append_text("❌ 信用點不足！", "error")
        except ValueError:
            pass

    def sell_selected(self):
        p = self.engine.player
        if not p or not p.inventory:
            self.append_text("背包是空的！", "error")
            return
        items = [f"{item['name']}" for item in p.inventory]
        items.append("取消")
        choice = simpledialog.askstring("賣出物品",
                                         "輸入要賣出的物品編號（半價）：\n" +
                                         "\n".join([f"{i+1}. {name}" for i, name in enumerate(items)]),
                                         parent=self.root)
        if not choice: return
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(p.inventory):
                item = p.inventory[idx]
                if self.engine.sell_item(item["id"]):
                    self.append_text(f"💰 賣出了 {item['name']}", "green")
                    self.refresh_shop_view()
                    self.update_status()
        except ValueError:
            pass

    # -------------------------------------------------------------------------
    # API 設定
    # -------------------------------------------------------------------------
    def open_api_settings(self):
        win = tk.Toplevel(self.root)
        win.title("AI 設定")
        win.geometry("450x250")
        win.resizable(False, False)
        win.configure(bg="#1a1a2e")

        tk.Label(win, text="AI 服務設定", font=('Arial', 16, 'bold'),
                 fg="#f0c040", bg="#1a1a2e").pack(pady=10)

        frame = tk.Frame(win, bg="#1a1a2e")
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        tk.Label(frame, text="API 金鑰：", font=('Arial', 11),
                 fg="white", bg="#1a1a2e").grid(row=0, column=0, sticky='w', pady=5)
        key_entry = tk.Entry(frame, width=35, font=('Arial', 11), bg="#2a2a4a", fg="white")
        key_entry.grid(row=0, column=1, sticky='w', pady=5)
        key_entry.insert(0, self.config.get("api_key", ""))

        tk.Label(frame, text="Base URL：", font=('Arial', 11),
                 fg="white", bg="#1a1a2e").grid(row=1, column=0, sticky='w', pady=5)
        url_entry = tk.Entry(frame, width=35, font=('Arial', 11), bg="#2a2a4a", fg="white")
        url_entry.grid(row=1, column=1, sticky='w', pady=5)
        url_entry.insert(0, self.config.get("base_url", "https://api.openai.com/v1"))

        tk.Label(frame, text="模型：", font=('Arial', 11),
                 fg="white", bg="#1a1a2e").grid(row=2, column=0, sticky='w', pady=5)
        model_entry = tk.Entry(frame, width=35, font=('Arial', 11), bg="#2a2a4a", fg="white")
        model_entry.grid(row=2, column=1, sticky='w', pady=5)
        model_entry.insert(0, self.config.get("model", "gpt-3.5-turbo"))

        def save_settings():
            key = key_entry.get().strip()
            url = url_entry.get().strip()
            model = model_entry.get().strip()
            if not url:
                url = "https://api.openai.com/v1"
            if not model:
                model = "gpt-3.5-turbo"
            self.config["api_key"] = key
            self.config["base_url"] = url
            self.config["model"] = model
            self.save_config()
            self.ai = AIService(api_key=key, base_url=url, model=model)
            self.engine.ai = self.ai
            win.destroy()
            if self.ai.enabled:
                messagebox.showinfo("成功", "AI 設定已儲存！")
            else:
                messagebox.showinfo("提示", "請輸入有效的 API 金鑰和 URL")

        btn_frame = tk.Frame(win, bg="#1a1a2e")
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="儲存", command=save_settings,
                  font=('Arial', 11), bg="#f0c040", fg="#1a1a2e", padx=20).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=win.destroy,
                  font=('Arial', 11), bg="#4a4a6a", fg="white", padx=15).pack(side=tk.LEFT, padx=5)

    # -------------------------------------------------------------------------
    # 核心遊戲功能
    # -------------------------------------------------------------------------
    def append_text(self, text: str, tag: str = None):
        if self.view_mode != "story":
            self.set_view_mode("story")
        self.text_area.config(state='normal')
        if tag:
            self.text_area.insert(tk.END, text + "\n", tag)
        else:
            self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.text_area.config(state='normal')

    def update_status(self):
        if not self.engine.player:
            return
        p = self.engine.player
        status = (f"👤 {p.name}  |  🎂 {p.age}歲  |  ❤️{p.health}  🧠{p.intelligence}  💪{p.strength}  "
                  f"🗣️{p.charisma}  🍀{p.luck}  🧠{p.sanity}  ✨{p.creativity}  😊{p.happiness}  "
                  f"💰{p.credits}  ⚡{p.action_points}點  |  🎒{len(p.inventory)}件")
        self.status_label.config(text=status)
        self.power_label.config(text=f"🏆 {p.get_power_level()}  |  {p.get_title()}")

    def show_welcome(self):
        self.append_text("=" * 60, "title")
        self.append_text(f"✦ 命運織網 - 天馬行空的人生模擬 RPG  v{VERSION} ✦", "title")
        self.append_text("=" * 60, "title")
        self.append_text(WORLD_BACKGROUND.strip())
        self.append_text("\n點擊「新人生」開始你的旅程！")
        self.append_text("按鈕說明：", "blue")
        self.append_text("  📖 故事 - 主劇情", "blue")
        self.append_text("  🎒 背包 - 查看/使用物品", "blue")
        self.append_text("  🏪 商店 - 買賣物品", "blue")
        self.append_text("  📖 圖鑑 - 查看已解鎖的結局與隱藏事件", "codex")
        self.append_text("  ⚙️ API - 設定 AI 服務", "blue")

    # -------------------------------------------------------------------------
    # 角色創建
    # -------------------------------------------------------------------------
    def start_new_game(self):
        self.engine.game_over = False
        self.engine.view_mode = "story"
        self.set_view_mode("story")
        self.text_area.config(state='normal')
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state='normal')
        self.open_character_creation()

    def open_character_creation(self):
        win = tk.Toplevel(self.root)
        win.title("角色創造")
        win.geometry("900x650")
        win.resizable(True, True)
        win.configure(bg="#1a1a2e")

        tk.Label(win, text="✦ 角色創造 ✦", font=('Arial', 18, 'bold'),
                 fg="#f0c040", bg="#1a1a2e").pack(pady=10)

        main_frame = tk.Frame(win, bg="#1a1a2e")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left_frame = tk.Frame(main_frame, bg="#1a1a2e")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(left_frame, text="姓名：", font=('Arial', 12),
                 fg="white", bg="#1a1a2e").grid(row=0, column=0, sticky='w', pady=5)
        name_entry = tk.Entry(left_frame, font=('Arial', 12), bg="#2a2a4a", fg="white")
        name_entry.grid(row=0, column=1, sticky='ew', pady=5)
        name_entry.insert(0, "節點行者")

        tk.Label(left_frame, text="屬性分配（初始 30，範圍 0-100）", font=('Arial', 12),
                 fg="#a0d0ff", bg="#1a1a2e").grid(row=1, column=0, columnspan=2, pady=10)

        attr_vars = {}
        attr_names = ["健康", "智力", "力量", "魅力", "運氣", "理智", "創造力"]
        for i, attr in enumerate(attr_names):
            tk.Label(left_frame, text=attr, font=('Arial', 11),
                     fg="white", bg="#1a1a2e").grid(row=i+2, column=0, sticky='w', pady=2)
            var = tk.IntVar(value=30)
            spin = tk.Spinbox(left_frame, from_=0, to=100, width=5, textvariable=var,
                              font=('Arial', 11), bg="#2a2a4a", fg="white")
            spin.grid(row=i+2, column=1, sticky='w', pady=2)
            attr_vars[attr] = var

        right_frame = tk.Frame(main_frame, bg="#1a1a2e")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        tk.Label(right_frame, text="特徵選擇（點擊切換）", font=('Arial', 12),
                 fg="#a0d0ff", bg="#1a1a2e").pack(pady=5)

        trait_data = [
            ("天才", "智力+20", -5),
            ("大力士", "力量+15", -3),
            ("萬人迷", "魅力+15", -4),
            ("幸運兒", "運氣+25", -6),
            ("發明家", "創造力+20", -5),
            ("靈媒", "理智+10", -4),
            ("體弱多病", "健康-15", 4),
            ("社交恐懼", "魅力-15", 3),
            ("偏執狂", "理智-15", 4),
            ("賭徒", "運氣-10", 3),
            ("外星人過敏", "健康-10", 5),
            ("時間感知障礙", "理智-10", 6)
        ]

        buff_traits = [t for t in trait_data if t[2] < 0]
        debuff_traits = [t for t in trait_data if t[2] > 0]

        buff_frame = tk.Frame(right_frame, bg="#1a1a2e")
        buff_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(buff_frame, text="🔹 增益（消耗點數）", font=('Arial', 11),
                 fg="#51cf66", bg="#1a1a2e").pack()

        buff_vars = {}
        for t_name, t_desc, t_cost in buff_traits:
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(buff_frame, text=f"{t_name} ({t_desc})",
                                 variable=var, font=('Arial', 10),
                                 fg="white", bg="#1a1a2e", selectcolor="#1a1a2e",
                                 onvalue=True, offvalue=False)
            chk.pack(anchor='w')
            buff_vars[t_name] = (var, t_cost)

        debuff_frame = tk.Frame(right_frame, bg="#1a1a2e")
        debuff_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        tk.Label(debuff_frame, text="🔸 減益（增加點數）", font=('Arial', 11),
                 fg="#ff6b6b", bg="#1a1a2e").pack()

        debuff_vars = {}
        for t_name, t_desc, t_cost in debuff_traits:
            var = tk.BooleanVar(value=False)
            chk = tk.Checkbutton(debuff_frame, text=f"{t_name} ({t_desc})",
                                 variable=var, font=('Arial', 10),
                                 fg="white", bg="#1a1a2e", selectcolor="#1a1a2e",
                                 onvalue=True, offvalue=False)
            chk.pack(anchor='w')
            debuff_vars[t_name] = (var, t_cost)

        total_points_label = tk.Label(win, text="總點數消耗：0", font=('Arial', 12),
                                      fg="#ffd700", bg="#1a1a2e")
        total_points_label.pack(pady=5)

        def update_total():
            total = 0
            for (var, cost) in buff_vars.values():
                if var.get(): total += cost
            for (var, cost) in debuff_vars.values():
                if var.get(): total += cost
            total_points_label.config(text=f"總點數消耗：{total}")

        for (var, cost) in buff_vars.values():
            var.trace_add('write', lambda *args: update_total())
        for (var, cost) in debuff_vars.values():
            var.trace_add('write', lambda *args: update_total())

        def confirm_creation():
            name = name_entry.get().strip()
            if not name: name = "節點行者"
            attributes = {attr: var.get() for attr, var in attr_vars.items()}
            selected = []
            for t_name, (var, cost) in buff_vars.items():
                if var.get(): selected.append(t_name)
            for t_name, (var, cost) in debuff_vars.items():
                if var.get(): selected.append(t_name)
            self.engine.create_player(name, attributes, selected)
            self.engine.game_over = False
            win.destroy()
            self.start_game_after_creation()

        confirm_btn = tk.Button(win, text="✅ 確認創造", command=confirm_creation,
                                font=('Arial', 12, 'bold'),
                                bg="#f0c040", fg="#1a1a2e", padx=20, pady=5)
        confirm_btn.pack(pady=10)

    def start_game_after_creation(self):
        self.end_year_btn.config(state=tk.NORMAL)
        self.inventory_btn.config(state=tk.NORMAL)
        self.shop_btn.config(state=tk.NORMAL)
        self.set_view_mode("story")

        p = self.engine.player
        self.append_text("=" * 60, "title")
        self.append_text(f"✨ {p.name} 降臨命運之網！", "title")
        self.append_text(f"健康:{p.health} 智力:{p.intelligence} 力量:{p.strength} "
                         f"魅力:{p.charisma} 運氣:{p.luck} 理智:{p.sanity} 創造力:{p.creativity}")
        if p.traits:
            self.append_text(f"特性: {', '.join(p.traits)}")

        desc = self.engine.get_scene_description()
        self.append_text(f"\n📍 {desc}")
        npcs = self.engine.get_scene_npcs()
        for npc_id in npcs:
            if npc_id in KEY_NPCS:
                dialogue = self.engine.ai.generate_npc_dialogue(p, npc_id)
                self.append_text(f"👤 {KEY_NPCS[npc_id]['name']}：{dialogue}", "npc")

        self.append_text("\n人生開始！每年 5 個行動。", "gold")
        self.append_text("💡 0 歲教學：試試所有按鈕熟悉操作！", "tutorial")

        if self.ai.last_error:
            self.append_text(f"⚠️ AI 警告：{self.ai.last_error}", "error")
            self.append_text("將使用靜態事件模式，不影響遊戲進行。", "error")

        self.in_tutorial = True
        self.tutorial_step = 0
        self.show_tutorial_step()
        self.update_status()
        self.show_actions()

    def show_tutorial_step(self):
        if not self.in_tutorial or self.engine.player.age > 0:
            self.in_tutorial = False
            return
        steps = [
            "👶 第一步：點擊「漫步」按鈕。",
            "👶 第二步：點擊「研讀」按鈕。",
            "👶 第三步：點擊「工作」按鈕。",
            "👶 第四步：點擊「交際」按鈕。",
            "👶 第五步：點擊「結束年」進入 1 歲。",
        ]
        if self.tutorial_step < len(steps):
            self.append_text(steps[self.tutorial_step], "tutorial")
        else:
            self.in_tutorial = False
            self.append_text("🎉 教學完成！自由探索吧！", "gold")

    def advance_tutorial(self):
        self.tutorial_step += 1
        self.show_tutorial_step()

    # -------------------------------------------------------------------------
    # 行動系統
    # -------------------------------------------------------------------------
    def show_actions(self):
        if self.engine.game_over:
            self.hide_buttons()
            return

        if self.engine.last_event and not self.waiting_for_event:
            self.show_event(self.engine.last_event)
            self.engine.last_event = None
            return

        if self.view_mode == "inventory":
            self.show_inventory_actions()
            return
        if self.view_mode == "shop":
            self.show_shop_actions()
            return

        actions = self.engine.get_available_actions()
        display_actions = []
        for action in actions[:4]:
            display_actions.append({
                "text": f"{action['name']} ({action.get('points',1)}點)",
                "command": lambda a=action: self.execute_action(a)
            })
        while len(display_actions) < 4:
            display_actions.append({"text": "", "command": lambda: None})
        self.show_action_buttons(display_actions)

    def execute_action(self, action_data):
        if self.engine.game_over:
            return
        p = self.engine.player
        if p.action_points <= 0:
            self.append_text("行動點已用完，點擊「結束年」繼續。")
            return

        if action_data.get("is_tech"):
            tech = self.engine.unlocked_tech
            if tech:
                self.engine.perform_action(action_data)
                self.append_text(f"🔬 安裝了 {tech['name']}！", "gold")
                self.append_text(f"⚠️ 副作用：{tech['side_effect']}", "highlight")
                self.engine.unlocked_tech = None
                self.update_status()
                self.show_actions()
                if self.in_tutorial and p.age == 0:
                    self.advance_tutorial()
                return

        if action_data.get("is_work"):
            cost_pts = action_data.get("points", 2)
            cost_credits = action_data.get("credits", 0)
            if p.credits < cost_credits:
                self.append_text("信用點不足！", "error")
                return
            if p.action_points < cost_pts:
                self.append_text("行動點不足！", "error")
                return

            result = self.engine.do_work()
            desc = result.get("description", "你努力工作了一天。")
            income = result.get("income", 0)

            p.action_points -= cost_pts
            p.credits -= cost_credits
            p.credits += income
            p.year_actions += 1

            self.append_text(f"💼 {desc}", "gold")
            self.append_text(f"💰 賺取 {income} 信用點", "green")

            self.engine.check_achievements()
            if self.engine.epic_achievement:
                self.append_text(f"\n🌟 史詩時刻：{self.engine.epic_text}", "gold")
                self.engine.epic_achievement = None
                self.engine.epic_text = ""

            if p.action_points <= 0:
                self.engine.next_year()

            if self.engine.game_over:
                self.show_game_over()
                return

            self.update_status()
            self.show_actions()
            if self.in_tutorial and p.age == 0:
                self.advance_tutorial()
            return

        self.engine.perform_action(action_data)
        self.append_text(f"▶ {action_data['name']}")

        if "income" in action_data and action_data["income"]:
            self.append_text(f"賺取 {action_data['income']} 信用點", "green")

        if self.engine.epic_achievement:
            self.append_text(f"\n🌟 史詩時刻：{self.engine.epic_text}", "gold")
            self.engine.epic_achievement = None
            self.engine.epic_text = ""

        if self.engine.last_event and not self.waiting_for_event:
            self.show_event(self.engine.last_event)
            self.engine.last_event = None
            return

        if self.engine.game_over:
            self.show_game_over()
            return

        self.update_status()
        self.show_actions()
        if self.in_tutorial and p.age == 0:
            self.advance_tutorial()

    # -------------------------------------------------------------------------
    # 事件系統
    # -------------------------------------------------------------------------
    def show_event(self, event: Dict):
        self.waiting_for_event = True
        is_hidden = event.get("is_hidden", False)
        is_positive = event.get("is_positive", False)
        choices = event.get("choices", [])
        solution = event.get("solution", None)

        self.append_text("\n" + "─" * 40, "blue")
        if is_hidden:
            if is_positive:
                self.append_text(f"✨ 隱藏事件（增益）：{event.get('title', '未知')}", "gold")
            else:
                self.append_text(f"⚠️ 隱藏事件：{event.get('title', '未知')}", "highlight")
        else:
            self.append_text(f"⚡ 事件：{event.get('title', '未知事件')}", "title")
        self.append_text(event.get('description', ''))

        if solution and event.get("is_solvable", True):
            self.append_text(f"💡 解法：{solution}", "solution")

        if is_positive:
            effects = event.get("effects", {})
            for attr, val in effects.items():
                if attr == "flags":
                    for f in val: self.engine.player.flags.add(f)
                else:
                    current = getattr(self.engine.player, attr, 0)
                    setattr(self.engine.player, attr, max(0, min(100, current + val)))
            self.append_text("✅ 事件已自動應用增益！", "green")
            self.waiting_for_event = False
            self.update_status()
            self.show_actions()
            return

        if choices:
            self.show_event_buttons(choices)
            self.event_choices = choices
        else:
            if is_hidden and solution:
                self.show_event_buttons([
                    {"text": "執行解法", "effects": event.get("solution_effects", {})},
                    {"text": "暫時忽略", "effects": {}}
                ])
                self.event_choices = [
                    {"text": "執行解法", "effects": event.get("solution_effects", {})},
                    {"text": "暫時忽略", "effects": {}}
                ]
            else:
                self.show_event_buttons([{"text": "繼續", "effects": {}}])
                self.event_choices = [{"text": "繼續", "effects": {}}]

    def choose_event(self, choice: Dict):
        self.engine.apply_event_choice(choice)
        self.append_text(f"➜ 選擇：{choice.get('text', '未知')}", "gold")

        if self.engine.epic_achievement:
            self.append_text(f"\n🌟 史詩時刻：{self.engine.epic_text}", "gold")
            self.engine.epic_achievement = None
            self.engine.epic_text = ""

        self.waiting_for_event = False
        self.event_choices = []

        if self.engine.game_over:
            self.show_game_over()
            return

        self.update_status()
        self.show_actions()

    # -------------------------------------------------------------------------
    # 結束年份與遊戲結束
    # -------------------------------------------------------------------------
    def end_year(self):
        if self.engine.game_over or not self.engine.player:
            return

        p = self.engine.player
        if p.action_points > 0:
            if not messagebox.askyesno("結束今年", f"還有 {p.action_points} 行動點未用，確定結束？"):
                return

        self.engine.next_year()

        if self.engine.game_over:
            self.show_game_over()
            return

        self.append_text("\n" + "=" * 50, "blue")
        self.append_text(f"✦ 第 {p.age} 年 ✦", "title")

        if self.engine.unlocked_tech:
            tech = self.engine.unlocked_tech
            self.append_text(f"\n🔬 科技解鎖：{tech['name']}！", "gold")
            self.append_text(f"描述：{tech['desc']}")
            self.append_text(f"費用：{tech['cost']} 信用點 | 副作用：{tech['side_effect']}", "highlight")
            self.append_text("在行動列表中選擇「安裝」來使用。")

        desc = self.engine.get_scene_description()
        self.append_text(f"\n📍 {desc}")

        npcs = self.engine.get_scene_npcs()
        for npc_id in npcs:
            if npc_id in KEY_NPCS:
                dialogue = self.engine.ai.generate_npc_dialogue(p, npc_id)
                self.append_text(f"👤 {KEY_NPCS[npc_id]['name']}：{dialogue}", "npc")

        if self.engine.epic_achievement:
            self.append_text(f"\n🌟 史詩時刻：{self.engine.epic_text}", "gold")
            self.engine.epic_achievement = None
            self.engine.epic_text = ""

        self.update_status()
        self.show_actions()

        if p.age == 1 and self.in_tutorial:
            self.in_tutorial = False
            self.append_text("🎉 你長大了！教學結束，自由探索吧！", "gold")

    def show_game_over(self):
        self.hide_buttons()
        self.end_year_btn.config(state=tk.DISABLED)
        self.inventory_btn.config(state=tk.DISABLED)
        self.shop_btn.config(state=tk.DISABLED)

        p = self.engine.player
        self.append_text("\n" + "=" * 60, "death")
        self.append_text("💀 故事終結 💀", "death")
        self.append_text("=" * 60, "death")
        self.append_text(f"角色：{p.name}")
        self.append_text(f"享年：{p.age} 歲")
        self.append_text(f"死因：{p.death_reason}", "highlight")
        self.append_text(f"總財富：{p.credits} 信用點")
        self.append_text(f"成就：{', '.join(p.life_achievements) if p.life_achievements else '無'}")

        # 顯示已解鎖的圖鑑數量
        codex_data = self.engine.get_codex_data()
        unlocked_endings = len(codex_data["endings"]["unlocked"])
        total_endings = len(codex_data["endings"]["all"])
        unlocked_hidden = len(codex_data["hidden_events"]["unlocked"])
        total_hidden = len(codex_data["hidden_events"]["all"])

        self.append_text("\n📖 圖鑑進度：", "codex")
        self.append_text(f"  🏆 結局：{unlocked_endings}/{total_endings}", "codex")
        self.append_text(f"  ✨ 隱藏事件：{unlocked_hidden}/{total_hidden}", "codex")

        self.append_text("\n" + "=" * 60, "ending")
        self.append_text(f"✦ 結局：{self.engine.ending_title} ✦", "ending")
        self.append_text(f"版本：{self.engine.ending_version_name}", "gold")
        self.append_text(self.engine.ending_text)
        self.append_text("\n🌍 世界的反應：", "title")
        self.append_text(self.engine.world_reaction, "world")
        self.append_text("=" * 60, "ending")

        self.append_text("\n點擊「新人生」重新開始。")
        self.start_btn.config(text="🔄 轉世重生")

        self.update_status()

    # -------------------------------------------------------------------------
    # 主程式運行
    # -------------------------------------------------------------------------
    def run(self):
        self.root.mainloop()

# =============================================================================
# 主程式
# =============================================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = GameApp(root)
    app.run()