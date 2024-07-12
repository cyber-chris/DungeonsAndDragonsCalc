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


@dataclass
class DamageDice:
    count: int
    faces: int
    modifiers: int = 0

    def expected_damage(self) -> float:
        die_damage = sum(range(1, self.faces + 1)) / self.faces
        return self.count * die_damage + self.modifiers

    def __repr__(self) -> str:
        return f"{self.count}d{self.faces}+{self.modifiers}"


assert DamageDice(1, 10, 0).expected_damage() == 5.5
assert DamageDice(3, 4, 3).expected_damage() == 10.5


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

    with st.expander("Damage Die"):
        damage_die_count = st.slider("Die Count", min_value=1, max_value=30, value=1)
        damage_die_faces = st.slider("Die Type", min_value=4, max_value=20, value=10)
        damage_modifiers = st.slider("Damage Modifier", min_value=0, max_value=20, value=0)
        damage_dice = DamageDice(damage_die_count, damage_die_faces, damage_modifiers)
    mc = Player(player_ac, prof_bonus)


with st.container(border=True):
    st.header("Enemy Stats")
    enemy_ac = st.slider("Enemy AC", min_value=5, max_value=30, value=12)
    enemy = Creature(enemy_ac)

hit_chance = mc.hit_chance(ability_mod, enemy, vantage)
expected_dmg = damage_dice.expected_damage()
expected_dmg_for_attack = hit_chance * expected_dmg

with st.container(border=True):
    st.header("Results")
    st.write(f"Player has a **{int(hit_chance*100)}%** chance of hitting")
    st.write(f"Expected dmg for {damage_dice} is **{expected_dmg:.2f}**")
    st.write(
        f"Therefore, overall expected dmg for attack is **{expected_dmg_for_attack:.2f}**"
    )


hit_chances = dict()

for ac in range(10, 26):
    creature = Creature(ac)
    hit_chances[ac] = mc.hit_chance(ability_mod, creature, AdvantageType.REGULAR)


st.header("Hit chance by AC", divider=True)
st.write("(without advantage)")
st.scatter_chart(hit_chances, x_label="Enemy AC", y_label="Hit chance")
