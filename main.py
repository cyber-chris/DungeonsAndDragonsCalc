import streamlit as st
import pandas as pd
from dataclasses import dataclass
from enum import Enum
import math

st.header("D&D 5e Calculator", divider=True)


class AdvantageType(Enum):
    DISADVANTAGE = -1
    REGULAR = 0
    ADVANTAGE = 1


@dataclass
class Creature:
    armour_class: int


@dataclass
class Player(Creature):
    proficiency_bonus: int

    def hit_chance(
        self, ability_modifier: int, target: Creature, vantage: AdvantageType
    ) -> float:
        min_attack_roll = 2 + ability_modifier + self.proficiency_bonus
        max_attack_roll = 20 + ability_modifier + self.proficiency_bonus
        if vantage == AdvantageType.REGULAR:
            if min_attack_roll <= target.armour_class <= max_attack_roll:
                return (max_attack_roll - target.armour_class + 1) / 20
            return 1 / 20

        if target.armour_class > max_attack_roll:
            return 1 - (19 / 20) ** 2 if AdvantageType.ADVANTAGE else 1 / 400

        if vantage == AdvantageType.ADVANTAGE:
            hit_boxes = (max_attack_roll - target.armour_class + 1) * 20 * 2 - (
                max_attack_roll - target.armour_class + 1
            ) ** 2
            return hit_boxes / 400
        if vantage == AdvantageType.DISADVANTAGE:
            hit_boxes = (max_attack_roll - target.armour_class + 1) ** 2
            return hit_boxes / 400


fighter = Player(16, 4)
dragon = Creature(19)
dragon_hit = fighter.hit_chance(5, dragon, AdvantageType.REGULAR)
assert math.isclose(dragon_hit, 0.55), dragon_hit
assert math.isclose(
    Player(10, 1).hit_chance(1, Creature(30), AdvantageType.ADVANTAGE), 0.0975
)

with st.container(border=True):
    st.header("Player Stats")
    player_ac = st.slider("Player AC", min_value=10, max_value=40, value=12)
    prof_bonus = st.slider("Proficiency Bonus", min_value=2, max_value=6)
    ability_mod = st.slider(
        "Ability Modifier (STR, DEX, or spellcasting mod)",
        min_value=-5,
        max_value=10,
        value=2,
    )
    vantage = st.selectbox("Advantage/Disadvantage?", AdvantageType, index=1)
    mc = Player(player_ac, prof_bonus)

with st.container(border=True):
    st.header("Enemy Stats")
    enemy_ac = st.slider("Enemy AC", min_value=5, max_value=30, value=12)
    enemy = Creature(enemy_ac)

hit_chance = mc.hit_chance(ability_mod, enemy, vantage)

st.write(f"Player has a **{int(hit_chance*100)}%** chance of hitting enemy.")


hit_chances = dict()

for ac in range(10, 26):
    creature = Creature(ac)
    hit_chances[ac] = mc.hit_chance(ability_mod, creature, AdvantageType.REGULAR)


st.header("Hit chance by AC", divider=True)
st.write("(without advantage)")
st.scatter_chart(hit_chances, x_label="Enemy AC", y_label="Hit chance")
