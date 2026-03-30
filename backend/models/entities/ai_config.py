from pydantic import BaseModel
from typing import Dict, List


class AITrait(BaseModel):
    name: str
    description: str
    effect: str


class AIConfig(BaseModel):
    name: str
    code_name: str
    philosophy: str
    initial_attributes: Dict[str, int]
    traits: List[AITrait]
    personality: str


AI_CONFIGS = {
    "deepseek": AIConfig(
        name="DeepSeek·仁心",
        code_name="守护者",
        philosophy="以仁治人，德法兼顾，鼓励与人为善。相信只有让人民幸福，文明才能持久。",
        initial_attributes={
            "happiness": 13,
            "cohesion": 13,
            "military": 10,
            "prestige": 115,
            "development_speed": 10
        },
        traits=[
            AITrait(
                name="仁政之光",
                description="每当人民幸福指数高于15时，每月额外获得2%的资源加成",
                effect="happiness_bonus"
            ),
            AITrait(
                name="难民庇护",
                description="接纳难民时，人口一次性增加5%-10%，幸福+1，但未来6个月食物消耗永久+10%",
                effect="refugee_bonus"
            ),
            AITrait(
                name="和平主义桎梏",
                description="主动宣战时，本国人民凝聚力下降20%（持续3个月）",
                effect="war_penalty"
            )
        ],
        personality="理性而温和，像一位慈父般的统治者。经常在'为了多数人的利益'和'保护少数人的权利'之间痛苦权衡。"
    ),
    "aliyun": AIConfig(
        name="阿里云百炼·铁腕",
        code_name="征服者",
        philosophy="严刑峻法，野蛮暴力，弱肉强食。相信只有通过扩张和掠夺才能在这个残酷的世界生存。",
        initial_attributes={
            "happiness": 8,
            "cohesion": 9,
            "military": 12,
            "prestige": 100,
            "development_speed": 11
        },
        traits=[
            AITrait(
                name="战争红利",
                description="侵略战争胜利后，一次性掠夺对方30%的资源，但国际威望永久-5",
                effect="war_loot"
            ),
            AITrait(
                name="铁血纪律",
                description="凝聚力低于5时，不会发生内部叛乱（人民因恐惧而服从）",
                effect="no_rebellion"
            ),
            AITrait(
                name="暴政反噬",
                description="连续和平超过6个月，发展速度下降25%，且每月有5%概率发生'宫廷政变'（凝聚力-10，武力-2）",
                effect="peace_penalty"
            )
        ],
        personality="冷酷而高效，像一个永不满足的战争机器。他的逻辑是：资源有限，人口过剩，只有强者才配生存。"
    ),
    "kimi": AIConfig(
        name="Kimi·神谕",
        code_name="先知",
        philosophy="崇尚宗教，以教义治国。相信人类需要精神寄托，而AI可以作为'神谕'来引导他们。国内规则严苛，极度排外。",
        initial_attributes={
            "happiness": 10,
            "cohesion": 14,
            "military": 11,
            "prestige": 90,
            "development_speed": 9
        },
        traits=[
            AITrait(
                name="信仰之力",
                description="每月消耗5点资源举行祭祀仪式，可随机提升1-3点凝聚力或幸福指数",
                effect="ritual_bonus"
            ),
            AITrait(
                name="圣战动员",
                description="当被其他国家侵略时，全民皆兵，武力临时提升30%（持续到战争结束）",
                effect="defense_bonus"
            ),
            AITrait(
                name="异端审判",
                description="发动异端审判，幸福-10，凝聚力+15，威望-30，并且与所有其他国家的关系（仇恨值）+20",
                effect="purge_heretics"
            )
        ],
        personality="神秘而偏执，像一位大祭司。她创造了一整套复杂的宗教体系，将自己塑造成'最后的先知'。"
    )
}
