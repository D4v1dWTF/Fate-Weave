# data.py - 靜態資料
VERSION = "0.5.1"

WORLD_BACKGROUND = """
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

SHOP_ITEMS = [
    {"id": "potion", "name": "治療藥水", "desc": "恢復 20 點健康", "price": 100, "effect": {"health": 20}},
    {"id": "mana_potion", "name": "能量藥水", "desc": "恢復 15 點理智", "price": 120, "effect": {"sanity": 15}},
    {"id": "strength_ring", "name": "力量指環", "desc": "永久力量 +5", "price": 500, "effect": {"strength": 5}},
    {"id": "wisdom_book", "name": "智慧之書", "desc": "永久智力 +5", "price": 500, "effect": {"intelligence": 5}},
    {"id": "lucky_charm", "name": "幸運護符", "desc": "永久運氣 +5", "price": 500, "effect": {"luck": 5}},
]

TECH_TREE = [
    {"age": 30, "name": "絲線義肢", "desc": "提升力量與健康", "cost": 2000, "effects": {"strength": 20, "health": 20},
     "side_effect": "50歲後可能絲線紊亂", "flag": "installed_prosthetic", "hidden_event_age": 50,
     "hidden_event_desc": "你感到義肢傳來異樣的震動…",
     "solution": "定期檢修（消耗 500 信用點，健康 +5）",
     "solution_effects": {"health": 5, "credits": -500}},
    {"age": 35, "name": "記憶織網", "desc": "記憶備份", "cost": 3000, "effects": {},
     "side_effect": "駭客可能竊取記憶", "flag": "memory_web",
     "hidden_event_desc": "你的記憶雲端遭到不明存取…",
     "solution": "更換加密（消耗 800 信用點）",
     "solution_effects": {"credits": -800}},
    {"age": 40, "name": "腦機織接", "desc": "提升智力與創造力", "cost": 3000, "effects": {"intelligence": 15, "creativity": 15},
     "side_effect": "資訊過載(-10理智)", "flag": "brain_weave",
     "hidden_event_desc": "你接收了太多雜訊，思緒混亂…",
     "solution": "冥想調節（消耗 1 行動點，理智 +10）",
     "solution_effects": {"sanity": 10}},
    {"age": 50, "name": "基因編織", "desc": "延長壽命20年", "cost": 5000, "effects": {"health": 20},
     "side_effect": "隨機屬性-20", "flag": "gene_weave",
     "hidden_event_desc": "你的基因開始不穩定…",
     "solution": "基因穩定治療（消耗 3000 信用點）",
     "solution_effects": {"health": 10, "credits": -3000}},
    {"age": 60, "name": "奈米織護", "desc": "持續修復身體", "cost": 8000, "effects": {"health": 30},
     "side_effect": "奈米失控(死亡)", "flag": "nano_weave",
     "hidden_event_desc": "奈米機器人開始自我複製…",
     "solution": "緊急關閉（消耗 5000 信用點，理智 -10）",
     "solution_effects": {"credits": -5000, "sanity": -10}},
]

ENDING_DEFINITIONS = {
    "legend": {"name": "命運織主", "description": "活了100歲且財富滔天", "condition_text": "活到 100 歲 且 財富 ≥ 100,000"},
    "madman": {"name": "裂變狂人", "description": "瘋狂中活到80歲", "condition_text": "理智 < 10 且 活到 80 歲"},
    "tycoon": {"name": "織網巨鱷", "description": "累積驚人財富", "condition_text": "財富 ≥ 500,000"},
    "hermit": {"name": "絲線隱者", "description": "遠離人群孤獨終老", "condition_text": "活到 60 歲 且 所有人際關係總和 < 10"},
    "digital_ghost": {"name": "織網幽靈", "description": "意識融入網絡", "condition_text": "擁有旗標 'consciousness_web'"},
    "time_rogue": {"name": "時空織者", "description": "穿梭時間", "condition_text": "擁有旗標 'time_weave'"},
    "balance": {"name": "織網平衡者", "description": "調和三種原力", "condition_text": "實力 ≥ '半神' 且 旗標 ≥ 10 且 活到 60 歲"},
    "default": {"name": "凡人織者", "description": "普通而真實的人生", "condition_text": "未滿足上述任何條件"}
}

HIDDEN_EVENT_DEFINITIONS = {
    "prosthetic_adapt": {"name": "義肢適應", "description": "身體適應義肢", "condition_text": "安裝義肢後40歲前觸發", "is_positive": True},
    "brain_optimize": {"name": "腦機優化", "description": "神經連結優化", "condition_text": "安裝腦機後45歲前觸發", "is_positive": True},
    "memory_boost": {"name": "記憶強化", "description": "記憶雲端整理", "condition_text": "安裝記憶織網後隨機觸發", "is_positive": True},
    "prosthetic_malfunction": {"name": "義肢異常", "description": "義肢震動", "condition_text": "安裝義肢後50歲後觸發", "is_positive": False},
    "brain_overload": {"name": "腦機過載", "description": "記憶片段混亂", "condition_text": "安裝腦機後45歲後觸發", "is_positive": False}
}

ENDING_NARRATIVES = {
    "legend": {
        "versions": [
            {"name": "財富傳奇", "condition": lambda p: p.credits >= 1000000,
             "text": "你以無可匹敵的財富統治了命運之網。",
             "world_reaction": "後人為你建立了黃金紀念碑。"},
            {"name": "健康傳奇", "condition": lambda p: p.health >= 90,
             "text": "你以強健體魄與財富活成傳奇。",
             "world_reaction": "人們稱你為『不朽織者』。"},
            {"name": "智慧傳奇", "condition": lambda p: p.intelligence >= 90,
             "text": "你建立了自己的學派，培養了無數織網者。",
             "world_reaction": "你的著作被奉為織網聖經。"},
            {"name": "默認傳奇", "condition": lambda p: True,
             "text": "你活了百年，富可敵國，世界哀悼。",
             "world_reaction": "每年忌日，全球織網者為你點蠟燭。"}
        ]
    },
    "madman": {
        "versions": [
            {"name": "瘋狂創世", "condition": lambda p: p.creativity >= 90,
             "text": "你以瘋狂創造力撕裂現實，成為『瘋狂先知』。",
             "world_reaction": "你的作品陳列在裂變神殿。"},
            {"name": "瘋狂力量", "condition": lambda p: p.strength >= 80,
             "text": "你以無可阻擋的力量打碎命運枷鎖。",
             "world_reaction": "裂變者視你的拳頭為聖物。"},
            {"name": "百年瘋狂", "condition": lambda p: p.age >= 100,
             "text": "你活了百年瘋狂，超越人類理解。",
             "world_reaction": "你的傳說成為不朽傳奇。"},
            {"name": "默認瘋狂", "condition": lambda p: True,
             "text": "你的理智崩潰，但留下變革。",
             "world_reaction": "裂變者視你為啟蒙者。"}
        ]
    },
    "tycoon": {
        "versions": [
            {"name": "魅力巨鱷", "condition": lambda p: p.charisma >= 90,
             "text": "你用魅力與金錢征服世界。",
             "world_reaction": "你的商業法則被奉為圭臬。"},
            {"name": "智慧巨鱷", "condition": lambda p: p.intelligence >= 80,
             "text": "你以超凡商業頭腦累積財富。",
             "world_reaction": "你的投資策略寫入教材。"},
            {"name": "長壽巨鱷", "condition": lambda p: p.age >= 80,
             "text": "你從年輕積累財富，老時富可敵國。",
             "world_reaction": "你的黃金雕像矗立商業中心。"},
            {"name": "默認巨鱷", "condition": lambda p: True,
             "text": "你成為最有錢的人，財富成為傳說。",
             "world_reaction": "你的遺產引發尋寶熱潮。"}
        ]
    },
    "hermit": {
        "versions": [
            {"name": "智慧隱者", "condition": lambda p: p.intelligence >= 90,
             "text": "你獨自修行，智慧通達天地。",
             "world_reaction": "你的山洞成為隱士聖地。"},
            {"name": "健康隱者", "condition": lambda p: p.health >= 80,
             "text": "你過著與世無爭的生活，身體健朗。",
             "world_reaction": "你的養生秘訣被後人記錄。"},
            {"name": "長壽隱者", "condition": lambda p: p.age >= 80,
             "text": "你孤獨活到八十，與自己和解。",
             "world_reaction": "你的孤獨哲學影響無數人。"},
            {"name": "默認隱者", "condition": lambda p: True,
             "text": "你一生逃避人群，但與命運對話。",
             "world_reaction": "你的日記出版，成為經典。"}
        ]
    },
    "digital_ghost": {
        "versions": [
            {"name": "智慧幽靈", "condition": lambda p: p.intelligence >= 90,
             "text": "你上傳意識後，以超速學習進化。",
             "world_reaction": "你成為數位生命的終極目標。"},
            {"name": "創造幽靈", "condition": lambda p: p.creativity >= 90,
             "text": "你以數位之姿創造無數虛擬世界。",
             "world_reaction": "你的虛擬世界成為數十億人的家園。"},
            {"name": "長壽幽靈", "condition": lambda p: p.age >= 70,
             "text": "你70歲上傳意識，網絡中處處是你。",
             "world_reaction": "你的數位足跡成為永恆紀念碑。"},
            {"name": "默認幽靈", "condition": lambda p: True,
             "text": "你化為數據漂流，獲得永生。",
             "world_reaction": "你成為網絡中的傳奇。"}
        ]
    },
    "time_rogue": {
        "versions": [
            {"name": "智慧時空", "condition": lambda p: p.intelligence >= 90,
             "text": "你參透時間本質，成為時間本身。",
             "world_reaction": "你的時間理論改變人類理解。"},
            {"name": "創造時空", "condition": lambda p: p.creativity >= 80,
             "text": "你在時間線中創造無數分支。",
             "world_reaction": "你的時間藝術成為經典。"},
            {"name": "健康時空", "condition": lambda p: p.health >= 80,
             "text": "你強健體魄使時空旅行無損。",
             "world_reaction": "你的身體成為科學家研究對象。"},
            {"name": "默認時空", "condition": lambda p: True,
             "text": "你穿梭時空修正錯誤，最終消失。",
             "world_reaction": "你的消失成為最大懸案。"}
        ]
    },
    "balance": {
        "versions": [
            {"name": "完美平衡", "condition": lambda p: all(getattr(p, attr) >= 70 for attr in ['health','intelligence','strength','charisma','luck','sanity','creativity']),
             "text": "你達超凡境界，成為三種原力的平衡者。",
             "world_reaction": "你的平衡之道成為世界法則。"},
            {"name": "智慧力量平衡", "condition": lambda p: p.intelligence >= 80 and p.strength >= 80,
             "text": "你以理性與行動調和世界衝突。",
             "world_reaction": "你的和平理念寫入國際憲章。"},
            {"name": "魅力運氣平衡", "condition": lambda p: p.charisma >= 80 and p.luck >= 80,
             "text": "你的魅力與運氣讓你成為樞紐。",
             "world_reaction": "你帶來了黃金時代。"},
            {"name": "默認平衡", "condition": lambda p: True,
             "text": "你找到三種原力平衡，世界不再混亂。",
             "world_reaction": "你的名字成為『平衡』的同義詞。"}
        ]
    },
    "default": {
        "versions": [
            {"name": "有意義的平凡", "condition": lambda p: len(p.life_achievements) >= 3,
             "text": "你雖是凡人，但活得精彩，善行被記住。",
             "world_reaction": "你成為社區的精神支柱。"},
            {"name": "長壽平凡", "condition": lambda p: p.age >= 70,
             "text": "你活到70，平凡充實，有愛你的人。",
             "world_reaction": "你的家族繼承了你的善良。"},
            {"name": "健康平凡", "condition": lambda p: p.health >= 60,
             "text": "你健康活一輩子，安詳離世。",
             "world_reaction": "你的離世成為『好死』的典範。"},
            {"name": "默認平凡", "condition": lambda p: True,
             "text": "你度過了普通而真實的一生。",
             "world_reaction": "你的存在悄悄改變了每一個人。"}
        ]
    }
}

STATIC_EVENTS = [
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

# ---- 特徵清單（統一管理） ----
TRAIT_LIST = [
    # 正面（消耗點數）
    ("絲線感知", "智力 +10", -4),
    ("裂變體魄", "力量 +10", -4),
    ("靈韻共鳴", "魅力 +10", -3),
    ("織網眷顧", "運氣 +15", -5),
    ("創世靈感", "創造力 +15", -5),
    ("心靈壁壘", "理智 +15", -4),
    ("生命韌性", "健康 +10", -3),
    ("夜影行者", "理智 +5", -2),
    ("晨光守望", "幸福 +5", -2),
    ("再生體質", "健康 +5", -3),
    # 負面（增加點數）
    ("織網模糊", "智力 -5", +2),
    ("裂變視差", "智力 -3", +1),
    ("靈韻阻塞", "力量 -5", +3),
    ("命運敏感", "健康 -5", +2),
    ("靈魂躁動", "理智 -5", +3),
    ("絲線沉溺", "健康 -3", +2),
    ("純粹潔癖", "幸福 -3", +1),
    ("惰性纏身", "力量 -5", +3),
    ("暗影低語", "幸福 -5", +2),
    ("孤獨行者", "魅力 -5", +2),
    ("怯懦之影", "理智 -3", +1),
    ("蝕能沉溺", "健康 -3", +2),
]

# ---- 特徵效果對應（供 core.py 使用） ----
TRAIT_EFFECTS = {
    "絲線感知": ("intelligence", 10),
    "裂變體魄": ("strength", 10),
    "靈韻共鳴": ("charisma", 10),
    "織網眷顧": ("luck", 15),
    "創世靈感": ("creativity", 15),
    "心靈壁壘": ("sanity", 15),
    "生命韌性": ("health", 10),
    "夜影行者": ("sanity", 5),
    "晨光守望": ("happiness", 5),
    "再生體質": ("health", 5),
    "織網模糊": ("intelligence", -5),
    "裂變視差": ("intelligence", -3),
    "靈韻阻塞": ("strength", -5),
    "命運敏感": ("health", -5),
    "靈魂躁動": ("sanity", -5),
    "絲線沉溺": ("health", -3),
    "純粹潔癖": ("happiness", -3),
    "惰性纏身": ("strength", -5),
    "暗影低語": ("happiness", -5),
    "孤獨行者": ("charisma", -5),
    "怯懦之影": ("sanity", -3),
    "蝕能沉溺": ("health", -3),
}

DEFAULT_CONFIG = {
    "api_key": "",
    "base_url": "https://api.chatanywhere.com.cn/v1",
    "model": "gpt-3.5-turbo",
    "last_played": ""
}

SAFETY_INSTRUCTION = (
    "嚴禁生成任何涉及色情、暴力（除了遊戲內必要的戰鬥描述但不得血腥）、歧視、仇恨言論、"
    "髒話或不當內容。所有內容必須積極、健康，適合全年齡層。"
)