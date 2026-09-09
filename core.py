# core.py - 核心類別（Player, AIService, GameEngine）
import random
import json
import os
import urllib.request
import urllib.error
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from data import (
    KEY_NPCS, SCENE_FRAMEWORK, SHOP_ITEMS, TECH_TREE,
    ENDING_DEFINITIONS, HIDDEN_EVENT_DEFINITIONS, ENDING_NARRATIVES,
    STATIC_EVENTS, WORLD_BACKGROUND, SAFETY_INSTRUCTION, TRAIT_EFFECTS, VERSION
)

# -----------------------------------------------------------------------------
# Player
# -----------------------------------------------------------------------------
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


# -----------------------------------------------------------------------------
# AIService
# -----------------------------------------------------------------------------
class AIService:
    def __init__(self, api_key: str = "", base_url: str = "", model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.enabled = bool(api_key and base_url)
        self.last_error = ""

    def _call_api(self, messages: List[Dict], temperature=0.8, max_tokens=500):
        if not self.enabled:
            self.last_error = "API 未啟用（請檢查金鑰與 URL）"
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
                self.last_error = "AI 回傳格式異常"
                return None
        except urllib.error.HTTPError as e:
            self.last_error = f"HTTP 錯誤 {e.code}: {e.reason}"
            if e.code == 403:
                self.last_error += " (可能金鑰無效或無權限)"
            elif e.code == 401:
                self.last_error += " (金鑰錯誤)"
            return None
        except urllib.error.URLError as e:
            self.last_error = f"網路錯誤: {e.reason}"
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
        context = f"目前狀態：年齡{player.age}，健康{player.health}，智力{player.intelligence}，力量{player.strength}，魅力{player.charisma}，運氣{player.luck}，理智{player.sanity}，創造力{player.creativity}，金錢{player.credits}，旗標{list(player.flags)}，場景{scene}。\n世界觀：{WORLD_BACKGROUND[:200]}\n請生成一個事件（JSON格式），包含 title, description, choices（每個choice含 text 和 effects）。**務必確保 effects 中的數值與 description 中的描述完全一致**。"
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
            age_hint = "幼兒（0-6歲），請生成適合幼兒的活動，例如幫忙做簡單家務、學習新事物、玩遊戲等。"
        elif age <= 17:
            age_hint = "青少年（7-17歲），請生成適合青少年的打工或學習活動，例如學校打工、協助鄰居、參加競賽等。"
        elif age <= 40:
            age_hint = "青年（18-40歲），請生成正職工作、創業或專業技能活動。"
        elif age <= 65:
            age_hint = "中年（41-65歲），請生成資深工作、管理職或顧問活動。"
        else:
            age_hint = "老年（66歲以上），請生成輕度勞動、傳承經驗或社區服務活動。"

        prompt = f"""
玩家年齡：{age}歲。
{age_hint}

請生成一段 40-80 字的工作敘事，並明確寫出獲得多少「信用點」。
**重要規則**：信用點數量必須與敘事中的數量完全一致。
例如：如果敘事說「抓到 3 隻蝴蝶，每隻 1 信用點」，則收入就是 3 信用點。
回傳 JSON：
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
        if age <= 6:
            income = random.randint(1, 5)
            desc = f"你幫忙整理玩具，獲得了 {income} 信用點獎勵。"
        elif age <= 17:
            income = random.randint(5, 20)
            desc = f"你幫鄰居遛狗，獲得了 {income} 信用點報酬。"
        elif age <= 40:
            income = random.randint(30, 150)
            desc = f"你今天完成了一個專案，獲得了 {income} 信用點薪資。"
        elif age <= 65:
            income = random.randint(50, 200)
            desc = f"你以顧問身份提供建議，獲得了 {income} 信用點酬勞。"
        else:
            income = random.randint(10, 60)
            desc = f"你整理了花園，鄰居送你 {income} 信用點表示感謝。"
        return {"description": desc, "income": income}


# -----------------------------------------------------------------------------
# GameEngine
# -----------------------------------------------------------------------------
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
        self.unlocked_endings: Set[str] = set()
        self.unlocked_hidden_events: Set[str] = set()
        self._load_codex()

    def _load_codex(self):
        try:
            if os.path.exists("codex_data.json"):
                with open("codex_data.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.unlocked_endings = set(data.get("endings", []))
                    self.unlocked_hidden_events = set(data.get("hidden_events", []))
        except:
            pass

    def _save_codex(self):
        try:
            with open("codex_data.json", 'w', encoding='utf-8') as f:
                json.dump({
                    "endings": list(self.unlocked_endings),
                    "hidden_events": list(self.unlocked_hidden_events)
                }, f, indent=2, ensure_ascii=False)
        except:
            pass

    def unlock_ending(self, ending_id: str):
        if ending_id not in self.unlocked_endings:
            self.unlocked_endings.add(ending_id)
            self._save_codex()
            if self.player:
                self.player.unlocked_endings.append(ending_id)

    def unlock_hidden_event(self, event_id: str):
        if event_id not in self.unlocked_hidden_events:
            self.unlocked_hidden_events.add(event_id)
            self._save_codex()
            if self.player:
                self.player.unlocked_hidden_events.append(event_id)

    def get_codex_data(self) -> Dict:
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

    def roll_stats(self) -> List[int]:
        return [sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]) for _ in range(7)]

    def create_player(self, name: str, traits: List[str]) -> Player:
        base_stats = self.roll_stats()
        p = Player(name)
        attrs = ["health", "intelligence", "strength", "charisma", "luck", "sanity", "creativity"]
        for i, attr in enumerate(attrs):
            setattr(p, attr, base_stats[i])
        p.traits = traits

        for t in traits:
            if t in TRAIT_EFFECTS:
                attr, delta = TRAIT_EFFECTS[t]
                current = getattr(p, attr)
                setattr(p, attr, max(0, min(100, current + delta)))

        for attr in attrs:
            setattr(p, attr, max(0, min(100, getattr(p, attr))))

        p.story_memory.append("你在命運起點醒來。")
        p.current_scene = "origin"
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
        # 負面
        if "installed_prosthetic" in p.flags and p.age >= 50:
            if random.random() < 0.05:
                self.unlock_hidden_event("prosthetic_malfunction")
                self.trigger_hidden_event({
                    "id": "prosthetic_malfunction",
                    "title": "義肢異常",
                    "description": "你感到義肢傳來異樣的震動…",
                    "effects": {"health": -10, "sanity": -5},
                    "solution": "定期檢修（消耗 500 信用點）",
                    "solution_effects": {"health": 5, "credits": -500},
                    "is_solvable": True
                })
        if "brain_weave" in p.flags and p.age >= 45:
            if random.random() < 0.03:
                self.unlock_hidden_event("brain_overload")
                self.trigger_hidden_event({
                    "id": "brain_overload",
                    "title": "腦機過載",
                    "description": "你接收到不屬於自己的記憶片段…",
                    "effects": {"sanity": -15, "intelligence": 5},
                    "solution": "冥想調節（消耗 1 行動點）",
                    "solution_effects": {"sanity": 10},
                    "is_solvable": True
                })
        # 正面
        if "installed_prosthetic" in p.flags and p.age < 40:
            if random.random() < 0.02:
                self.unlock_hidden_event("prosthetic_adapt")
                self.trigger_hidden_event({
                    "id": "prosthetic_adapt",
                    "title": "義肢適應",
                    "description": "你的身體完全適應了義肢。",
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
                    "description": "你的腦機介面自動優化了神經連結。",
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
                    "description": "你的記憶雲端自動整理，喚醒靈感。",
                    "effects": {"creativity": 10},
                    "is_solvable": False,
                    "is_positive": True
                })

    def trigger_hidden_event(self, event_data: Dict):
        if not self.player: return
        if event_data.get("is_solvable", True) and "solution" not in event_data:
            event_data["solution"] = "嘗試與事件相關的人溝通。"
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
            self.last_event = random.choice(eligible)
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
                self.ending_title = ENDING_DEFINITIONS[ending_id]["name"]
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
        if income:
            p.credits += income
        self.check_achievements()
        if p.action_points <= 0:
            self.next_year()

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
        return self.ai.generate_work_scenario(self.player)

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
        if not self.game_over:
            self.check_achievements()

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