#!/usr/bin/env python3
"""
To Be Hero X - CLI Game
Based on the original anime/donghua
"""

import random
import time
import sys
import json
import os
from enum import Enum
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod


# ============== ANSI Colors for CLI ==============
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[35m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

    @staticmethod
    def color_text(text: str, color: str) -> str:
        return f"{color}{text}{Colors.END}"


# ============== Enums and Data Classes ==============
class HeroRank(Enum):
    UNRANKED = 0
    TOP_10 = 10
    TOP_9 = 9
    TOP_8 = 8
    TOP_7 = 7
    TOP_6 = 6
    TOP_5 = 5
    TOP_4 = 4
    TOP_3 = 3
    TOP_2 = 2
    TOP_1 = 1
    X = 0  # Special rank above #1


class TrustLevel(Enum):
    WORSHIP = 1000  # 1000+ trust
    LEGENDARY = 500  # 500-999 trust
    FAMOUS = 200  # 200-499 trust
    KNOWN = 50  # 50-199 trust
    UNKNOWN = 10  # 10-49 trust
    DISTRUSTED = 0  # 0-9 trust


@dataclass
class Hero:
    """Base Hero class matching anime characters"""
    name: str
    hero_name: str
    rank: HeroRank
    trust_value: int
    power: str
    special_ability: str
    hp: int = 100
    max_hp: int = 100
    energy: int = 50
    max_energy: int = 50

    def get_trust_level(self) -> TrustLevel:
        if self.trust_value >= 1000:
            return TrustLevel.WORSHIP
        elif self.trust_value >= 500:
            return TrustLevel.LEGENDARY
        elif self.trust_value >= 200:
            return TrustLevel.FAMOUS
        elif self.trust_value >= 50:
            return TrustLevel.KNOWN
        elif self.trust_value >= 10:
            return TrustLevel.UNKNOWN
        else:
            return TrustLevel.DISTRUSTED

    def display_status(self) -> str:
        trust_level = self.get_trust_level()
        level_colors = {
            TrustLevel.WORSHIP: Colors.YELLOW,
            TrustLevel.LEGENDARY: Colors.MAGENTA,
            TrustLevel.FAMOUS: Colors.CYAN,
            TrustLevel.KNOWN: Colors.GREEN,
            TrustLevel.UNKNOWN: Colors.BLUE,
            TrustLevel.DISTRUSTED: Colors.RED
        }
        color = level_colors.get(trust_level, Colors.END)

        return (f"{Colors.BOLD}{self.hero_name}{Colors.END} ({self.name})\n"
                f"Rank: #{self.rank.value if self.rank.value > 0 else 'X'}\n"
                f"Trust: {color}{self.trust_value}{Colors.END}\n"
                f"HP: {self.hp}/{self.max_hp}\n"
                f"Energy: {self.energy}/{self.max_energy}\n"
                f"Power: {self.power}")


# ============== Character Database ==============
class HeroDatabase:
    """All characters from To Be Hero X"""

    @staticmethod
    def get_all_heroes() -> List[Hero]:
        return [
            # X (The mysterious #1)
            Hero("???", "X", HeroRank.X, 9999,
                 "Reality Manipulation", "Can alter reality based on public perception"),

            # Queen (#2)
            Hero("Queen", "Queen", HeroRank.TOP_2, 950,
                 "Spear Mastery", "Precision strikes that ignore defenses"),

            # Dragon Boy (#3)
            Hero("Dragon Boy", "Dragon Boy", HeroRank.TOP_3, 880,
                 "Dragon Spirit", "Summons dragon energy for massive damage"),

            # Ghostblade (#4)
            Hero("Ghostblade", "Ghostblade", HeroRank.TOP_4, 820,
                 "Silent Assassination", "Attacks that don't alert enemies"),

            # The Johnnies (#5)
            Hero("Little Johnny", "The Johnnies", HeroRank.TOP_5, 750,
                 "Animal Communication + Immunity", "Tag-team attacks"),

            # Loli (#6)
            Hero("Loli", "Loli", HeroRank.TOP_6, 680,
                 "Mech Engineering", "Giant robot support"),

            # Lucky Cyan (#7)
            Hero("Lucky Cyan", "Lucky Cyan", HeroRank.TOP_7, 620,
                 "Music Magic", "Songs that boost allies or debuff enemies"),

            # Ahu (#8)
            Hero("Ahu", "Ahu", HeroRank.TOP_8, 550,
                 "Shape-shifting", "Can transform into any form"),

            # E-Soul (#9)
            Hero("E-Soul", "E-Soul", HeroRank.TOP_9, 480,
                 "Legacy Power", "Inherited hero abilities"),

            # Lin Ling / The Commoner (#10)
            Hero("Lin Ling", "The Commoner", HeroRank.TOP_10, 400,
                 "Determination", "Grows stronger when trust is low"),

            # Nice (Original hero)
            Hero("Nice", "Nice", HeroRank.UNRANKED, 300,
                 "Basic Heroics", "Standard hero abilities"),

            # Additional characters for variety
            Hero("Shadow", "Shadow Stalker", HeroRank.UNRANKED, 250,
                 "Darkness Manipulation", "Controls shadows"),

            Hero("Blaze", "Inferno", HeroRank.UNRANKED, 280,
                 "Fire Control", "Burns everything"),

            Hero("Frost", "Ice Queen", HeroRank.UNRANKED, 270,
                 "Ice Magic", "Freezes enemies"),
        ]

    @staticmethod
    def get_top_10() -> List[Hero]:
        heroes = HeroDatabase.get_all_heroes()
        return [h for h in heroes if h.rank.value <= 10][:10]

    @staticmethod
    def get_hero_by_name(name: str) -> Optional[Hero]:
        heroes = HeroDatabase.get_all_heroes()
        for hero in heroes:
            if hero.hero_name.lower() == name.lower() or hero.name.lower() == name.lower():
                return hero
        return None


# ============== Game Modes ==============
class GameMode(Enum):
    TRUST_BATTLE = 1  # 1v1 battles where trust affects power
    RANKING_TOURNAMENT = 2  # Fight through ranks to become X
    SURVIVAL = 3  # Survive as long as possible
    STORY_MODE = 4  # Play through anime events
    CUSTOM_BATTLE = 5  # Create custom matches


# ============== Battle System ==============
class BattleSystem:
    """Core battle mechanics based on Trust Value system"""

    @staticmethod
    def calculate_damage(attacker: Hero, defender: Hero, base_power: int) -> int:
        """Damage calculation influenced by trust values"""
        trust_advantage = attacker.trust_value - defender.trust_value
        trust_multiplier = 1.0 + (trust_advantage / 2000)  # Max ~2x damage

        # Critical hit chance based on trust
        crit_chance = min(0.3, attacker.trust_value / 5000)
        if random.random() < crit_chance:
            base_power *= 2
            print(Colors.color_text("CRITICAL HIT!", Colors.YELLOW))

        damage = int(base_power * trust_multiplier)
        return max(1, damage)  # Minimum 1 damage

    @staticmethod
    def trust_shift(winner: Hero, loser: Hero):
        """Trust values change based on battle outcome"""
        trust_change = random.randint(10, 50)
        winner.trust_value += trust_change
        loser.trust_value -= trust_change // 2

        # Ensure trust doesn't go negative
        loser.trust_value = max(0, loser.trust_value)

        print(f"\n{Colors.color_text('TRUST SHIFT!', Colors.MAGENTA)}")
        print(f"{winner.hero_name} gains {trust_change} trust!")
        print(f"{loser.hero_name} loses {trust_change // 2} trust!")

    @staticmethod
    def battle_turn(attacker: Hero, defender: Hero) -> Tuple[bool, str]:
        """Execute a single battle turn"""
        print(f"\n{Colors.BOLD}{attacker.hero_name}'s turn{Colors.END}")

        # Energy regeneration
        attacker.energy = min(attacker.max_energy, attacker.energy + 10)

        # Choose action
        print("\nChoose action:")
        print("1. Basic Attack (10 energy, low damage)")
        print("2. Special Ability (25 energy, medium damage)")
        print("3. Ultimate Move (40 energy, high damage)")
        print("4. Charge (Gain 20 energy)")

        while True:
            try:
                choice = int(input("\nEnter choice (1-4): "))
                if 1 <= choice <= 4:
                    break
                print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")

        if choice == 1:  # Basic Attack
            if attacker.energy >= 10:
                attacker.energy -= 10
                damage = BattleSystem.calculate_damage(attacker, defender, 15)
                defender.hp -= damage
                return True, f"{attacker.hero_name} deals {damage} damage with basic attack!"
            else:
                print("Not enough energy! Charging instead...")
                attacker.energy += 20
                return False, f"{attacker.hero_name} charges energy!"

        elif choice == 2:  # Special Ability
            if attacker.energy >= 25:
                attacker.energy -= 25
                damage = BattleSystem.calculate_damage(attacker, defender, 30)
                defender.hp -= damage
                return True, f"{attacker.hero_name} uses {attacker.special_ability} for {damage} damage!"
            else:
                print("Not enough energy! Using basic attack instead...")
                attacker.energy -= 10
                damage = BattleSystem.calculate_damage(attacker, defender, 15)
                defender.hp -= damage
                return True, f"{attacker.hero_name} deals {damage} damage with basic attack!"

        elif choice == 3:  # Ultimate Move
            if attacker.energy >= 40:
                attacker.energy -= 40
                damage = BattleSystem.calculate_damage(attacker, defender, 50)
                defender.hp -= damage
                return True, f"{Colors.color_text('ULTIMATE MOVE!', Colors.RED)} {attacker.hero_name} unleashes {attacker.power} for {damage} damage!"
            else:
                print("Not enough energy! Using special instead...")
                attacker.energy -= 25
                damage = BattleSystem.calculate_damage(attacker, defender, 30)
                defender.hp -= damage
                return True, f"{attacker.hero_name} uses {attacker.special_ability} for {damage} damage!"

        else:  # Charge
            attacker.energy += 20
            return False, f"{attacker.hero_name} charges energy!"


# ============== Game Modes Implementation ==============
class TrustBattleMode:
    """1v1 battles where trust affects everything"""

    @staticmethod
    def play(player_hero: Hero):
        print(f"\n{Colors.HEADER}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}TRUST BATTLE MODE{Colors.END}")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.END}")

        heroes = HeroDatabase.get_all_heroes()
        # Remove player hero from opponents
        opponents = [h for h in heroes if h.hero_name != player_hero.hero_name]

        wins = 0
        while player_hero.hp > 0 and opponents:
            opponent = random.choice(opponents)
            opponents.remove(opponent)

            print(f"\n{Colors.YELLOW}Match {wins + 1}{Colors.END}")
            print(f"Opponent: {opponent.hero_name} (Trust: {opponent.trust_value})")

            # Reset HP for next battle (but keep trust changes)
            player_hero.hp = player_hero.max_hp
            player_hero.energy = player_hero.max_energy

            # Battle loop
            while player_hero.hp > 0 and opponent.hp > 0:
                print(f"\n{player_hero.display_status()}")
                print(f"\n{opponent.display_status()}")

                # Player turn
                hit, message = BattleSystem.battle_turn(player_hero, opponent)
                print(message)

                if opponent.hp <= 0:
                    print(f"\n{Colors.color_text(f'{opponent.hero_name} defeated!', Colors.GREEN)}")
                    wins += 1
                    BattleSystem.trust_shift(player_hero, opponent)
                    break

                # Opponent turn (simple AI)
                time.sleep(1)
                print(f"\n{opponent.hero_name}'s turn...")
                if opponent.energy >= 30 and random.random() > 0.5:
                    opponent.energy -= 30
                    damage = BattleSystem.calculate_damage(opponent, player_hero, 35)
                    player_hero.hp -= damage
                    print(f"{opponent.hero_name} uses special attack for {damage} damage!")
                else:
                    opponent.energy += 15
                    damage = BattleSystem.calculate_damage(opponent, player_hero, 10)
                    player_hero.hp -= damage
                    print(f"{opponent.hero_name} attacks for {damage} damage!")

            if player_hero.hp <= 0:
                print(f"\n{Colors.color_text('You were defeated!', Colors.RED)}")
                print(f"Final win streak: {wins}")
                return wins

        print(f"\n{Colors.color_text('VICTORY! You defeated all opponents!', Colors.GREEN)}")
        print(f"Final win streak: {wins}")
        return wins


class RankingTournamentMode:
    """Fight through ranks to become X"""

    @staticmethod
    def play(player_hero: Hero):
        print(f"\n{Colors.HEADER}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}RANKING TOURNAMENT MODE{Colors.END}")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.END}")
        print("\nFight through the ranks to become the legendary X!")

        top_10 = HeroDatabase.get_top_10()
        current_rank = 10

        for opponent in top_10:
            if opponent.hero_name == player_hero.hero_name:
                continue

            print(f"\n{Colors.YELLOW}Current Rank: #{current_rank}{Colors.END}")
            print(f"Challenger: {opponent.hero_name} (Rank #{opponent.rank.value})")

            # Reset HP
            player_hero.hp = player_hero.max_hp
            player_hero.energy = player_hero.max_energy
            opponent.hp = opponent.max_hp
            opponent.energy = opponent.max_energy

            # Battle loop
            while player_hero.hp > 0 and opponent.hp > 0:
                print(f"\n{player_hero.display_status()}")
                print(f"\n{opponent.display_status()}")

                # Player turn
                hit, message = BattleSystem.battle_turn(player_hero, opponent)
                print(message)

                if opponent.hp <= 0:
                    print(f"\n{Colors.color_text(f'Defeated #{opponent.rank.value}!', Colors.GREEN)}")
                    if current_rank > 1:
                        current_rank -= 1
                    BattleSystem.trust_shift(player_hero, opponent)
                    break

                # Opponent turn (smarter AI for higher ranks)
                time.sleep(1)
                print(f"\n{opponent.hero_name}'s turn...")
                if opponent.energy >= 40 and opponent.rank.value <= 3:
                    opponent.energy -= 40
                    damage = BattleSystem.calculate_damage(opponent, player_hero, 60)
                    player_hero.hp -= damage
                    print(f"{opponent.hero_name} uses ULTIMATE MOVE for {damage} damage!")
                elif opponent.energy >= 25:
                    opponent.energy -= 25
                    damage = BattleSystem.calculate_damage(opponent, player_hero, 35)
                    player_hero.hp -= damage
                    print(f"{opponent.hero_name} uses {opponent.special_ability} for {damage} damage!")
                else:
                    opponent.energy += 15
                    damage = BattleSystem.calculate_damage(opponent, player_hero, 15)
                    player_hero.hp -= damage
                    print(f"{opponent.hero_name} attacks for {damage} damage!")

            if player_hero.hp <= 0:
                print(f"\n{Colors.color_text('Tournament defeat!', Colors.RED)}")
                print(f"Final rank: #{current_rank}")
                return current_rank

        # Final battle with X
        print(f"\n{Colors.color_text('FINAL BATTLE: VS X!', Colors.YELLOW)}")
        x_hero = HeroDatabase.get_hero_by_name("X")
        if x_hero:
            player_hero.hp = player_hero.max_hp
            player_hero.energy = player_hero.max_energy

            # Special X battle - X has reality manipulation
            print(f"\n{Colors.MAGENTA}X: 'Let's see if your trust can overcome reality itself...'{Colors.END}")

            while player_hero.hp > 0 and x_hero.hp > 0:
                # X's reality manipulation affects the battle
                if random.random() < 0.2:
                    print(f"\n{Colors.RED}X warps reality!{Colors.END}")
                    if random.choice([True, False]):
                        player_hero.hp -= 30
                        print(f"You take 30 damage from reality fracture!")
                    else:
                        x_hero.hp -= 30
                        print(f"X takes 30 damage from reality fracture!")

                # Player turn
                hit, message = BattleSystem.battle_turn(player_hero, x_hero)
                print(message)

                if x_hero.hp <= 0:
                    print(f"\n{Colors.color_text('INCREDIBLE! You defeated X!', Colors.GOLD)}")
                    print(f"{Colors.BOLD}You have become the new X!{Colors.END}")
                    return 0  # X rank

                # X's turn
                time.sleep(1)
                print(f"\nX's turn...")
                damage = BattleSystem.calculate_damage(x_hero, player_hero, 45)
                player_hero.hp -= damage
                print(f"X attacks for {damage} damage!")

        return current_rank


class SurvivalMode:
    """Survive as long as possible against endless enemies"""

    @staticmethod
    def play(player_hero: Hero):
        print(f"\n{Colors.HEADER}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}SURVIVAL MODE{Colors.END}")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.END}")
        print("\nSurvive as long as you can against endless enemies!")

        wave = 1
        kills = 0
        heroes = HeroDatabase.get_all_heroes()

        while player_hero.hp > 0:
            print(f"\n{Colors.YELLOW}WAVE {wave}{Colors.END}")

            # Each wave gets harder
            num_enemies = min(3, 1 + wave // 3)
            enemies = random.sample(heroes, min(num_enemies, len(heroes)))

            print(f"Enemies: {', '.join([e.hero_name for e in enemies])}")

            # Reset player slightly between waves
            player_hero.hp = min(player_hero.max_hp, player_hero.hp + 30)
            player_hero.energy = player_hero.max_energy

            wave_survived = True
            for enemy in enemies:
                if player_hero.hp <= 0:
                    wave_survived = False
                    break

                print(f"\n{Colors.CYAN}Fighting {enemy.hero_name}{Colors.END}")
                enemy.hp = enemy.max_hp + (wave * 10)  # Enemies get stronger

                while player_hero.hp > 0 and enemy.hp > 0:
                    print(f"\n{player_hero.display_status()}")
                    print(f"\n{enemy.display_status()}")

                    # Player turn
                    hit, message = BattleSystem.battle_turn(player_hero, enemy)
                    print(message)

                    if enemy.hp <= 0:
                        kills += 1
                        print(f"{Colors.color_text(f'{enemy.hero_name} defeated!', Colors.GREEN)}")
                        BattleSystem.trust_shift(player_hero, enemy)
                        break

                    # Enemy turn
                    time.sleep(0.5)
                    damage = BattleSystem.calculate_damage(enemy, player_hero, 10 + wave)
                    player_hero.hp -= damage
                    print(f"{enemy.hero_name} deals {damage} damage!")

                if player_hero.hp <= 0:
                    wave_survived = False
                    break

            if wave_survived:
                print(f"\n{Colors.color_text(f'WAVE {wave} CLEARED!', Colors.GREEN)}")
                wave += 1
                # Bonus trust for clearing wave
                player_hero.trust_value += 50
            else:
                print(f"\n{Colors.color_text('GAME OVER!', Colors.RED)}")
                print(f"Survived {wave} waves")
                print(f"Defeated {kills} enemies")
                return wave, kills

        return wave, kills


class StoryMode:
    """Play through events from the anime"""

    @staticmethod
    def play():
        print(f"\n{Colors.HEADER}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}STORY MODE: The Path to X{Colors.END}")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.END}")

        # Create Lin Ling (The Commoner) as protagonist
        player_hero = HeroDatabase.get_hero_by_name("The Commoner")
        if not player_hero:
            player_hero = Hero("Lin Ling", "The Commoner", HeroRank.TOP_10, 400,
                               "Determination", "Grows stronger when trust is low")

        chapters = [
            {
                "name": "Chapter 1: The Commoner's Beginning",
                "desc": "Lin Ling, an ordinary office worker, is forced to impersonate the hero 'Nice'.",
                "enemy": Hero("Thug", "Street Thug", HeroRank.UNRANKED, 50,
                              "Brute Force", "Intimidation"),
                "trust_reward": 50
            },
            {
                "name": "Chapter 2: The Trust System",
                "desc": "You discover that powers come from public faith. Build your trust!",
                "enemy": HeroDatabase.get_hero_by_name("Nice"),
                "trust_reward": 100
            },
            {
                "name": "Chapter 3: Entering the Rankings",
                "desc": "Time to prove yourself in the hero rankings!",
                "enemy": HeroDatabase.get_hero_by_name("Shadow Stalker"),
                "trust_reward": 150
            },
            {
                "name": "Chapter 4: Meeting the Top 10",
                "desc": "You encounter Loli, the genius engineer.",
                "enemy": HeroDatabase.get_hero_by_name("Loli"),
                "trust_reward": 200
            },
            {
                "name": "Chapter 5: The Assassin's Creed",
                "desc": "Face Ghostblade, the silent assassin.",
                "enemy": HeroDatabase.get_hero_by_name("Ghostblade"),
                "trust_reward": 250
            },
            {
                "name": "Chapter 6: Dragon's Challenge",
                "desc": "Dragon Boy tests your resolve.",
                "enemy": HeroDatabase.get_hero_by_name("Dragon Boy"),
                "trust_reward": 300
            },
            {
                "name": "Chapter 7: Queen's Judgment",
                "desc": "Queen, the #2 hero, evaluates your worth.",
                "enemy": HeroDatabase.get_hero_by_name("Queen"),
                "trust_reward": 400
            },
            {
                "name": "Chapter 8: The Final Trial",
                "desc": "Face X himself and prove you deserve the title!",
                "enemy": HeroDatabase.get_hero_by_name("X"),
                "trust_reward": 1000
            }
        ]

        for chapter in chapters:
            print(f"\n{Colors.HEADER}{'=' * 50}{Colors.END}")
            print(f"{Colors.BOLD}{chapter['name']}{Colors.END}")
            print(f"{chapter['desc']}")
            print(f"{Colors.HEADER}{'=' * 50}{Colors.END}")

            input("\nPress Enter to continue...")

            # Setup battle
            enemy = chapter['enemy']
            if enemy:
                print(f"\n{Colors.RED}ENEMY: {enemy.hero_name}{Colors.END}")

                # Reset HP
                player_hero.hp = player_hero.max_hp
                player_hero.energy = player_hero.max_energy
                enemy.hp = enemy.max_hp
                enemy.energy = enemy.max_energy

                # Battle loop
                while player_hero.hp > 0 and enemy.hp > 0:
                    print(f"\n{player_hero.display_status()}")
                    print(f"\n{enemy.display_status()}")

                    # Player turn
                    hit, message = BattleSystem.battle_turn(player_hero, enemy)
                    print(message)

                    if enemy.hp <= 0:
                        print(f"\n{Colors.color_text('VICTORY!', Colors.GREEN)}")
                        player_hero.trust_value += chapter['trust_reward']
                        print(f"Trust increased by {chapter['trust_reward']}!")
                        break

                    # Enemy turn
                    time.sleep(1)
                    print(f"\n{enemy.hero_name}'s turn...")
                    damage = BattleSystem.calculate_damage(enemy, player_hero, 20 + (chapter['trust_reward'] // 10))
                    player_hero.hp -= damage
                    print(f"{enemy.hero_name} deals {damage} damage!")

                if player_hero.hp <= 0:
                    print(f"\n{Colors.color_text('DEFEAT! Story ends here...', Colors.RED)}")
                    print(f"Reached: {chapter['name']}")
                    return chapter['name']

            print(f"\n{Colors.color_text('Chapter Complete!', Colors.GREEN)}")
            time.sleep(1)

        print(f"\n{Colors.color_text('CONGRATULATIONS! You completed the story and became X!', Colors.GOLD)}")
        return "Complete"


# ============== Main Game Class ==============
class ToBeHeroXGame:
    """Main game controller"""

    def __init__(self):
        self.player_hero = None
        self.save_file = "tbhero_save.json"

    def save_game(self):
        """Save game state"""
        if self.player_hero:
            save_data = {
                "name": self.player_hero.name,
                "hero_name": self.player_hero.hero_name,
                "rank": self.player_hero.rank.value,
                "trust_value": self.player_hero.trust_value,
                "max_hp": self.player_hero.max_hp
            }
            with open(self.save_file, 'w') as f:
                json.dump(save_data, f)
            print(f"\n{Colors.GREEN}Game saved!{Colors.END}")

    def load_game(self):
        """Load game state"""
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    save_data = json.load(f)

                hero = HeroDatabase.get_hero_by_name(save_data['hero_name'])
                if hero:
                    hero.trust_value = save_data['trust_value']
                    hero.max_hp = save_data['max_hp']
                    hero.hp = hero.max_hp
                    self.player_hero = hero
                    print(f"\n{Colors.GREEN}Game loaded! Welcome back, {hero.hero_name}!{Colors.END}")
                    return True
            except:
                print(f"\n{Colors.RED}Failed to load save file.{Colors.END}")
        return False

    def select_hero(self) -> Hero:
        """Let player select their hero"""
        print(f"\n{Colors.BOLD}Select your hero:{Colors.END}")

        heroes = HeroDatabase.get_all_heroes()
        for i, hero in enumerate(heroes[:10], 1):  # Show first 10
            rank_display = f"#{hero.rank.value}" if hero.rank.value > 0 else "X"
            print(f"{i}. {hero.hero_name} (Rank: {rank_display}) - {hero.power}")

        print(f"{len(heroes[:10]) + 1}. Random Hero")

        while True:
            try:
                choice = int(input("\nChoose your hero (1-11): "))
                if 1 <= choice <= len(heroes[:10]):
                    return heroes[choice - 1]
                elif choice == len(heroes[:10]) + 1:
                    return random.choice(heroes)
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Please enter a number.")

    def show_menu(self):
        """Display main menu"""
        print(f"\n{Colors.HEADER}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}TO BE HERO X - CLI GAME{Colors.END}")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.END}")

        if self.player_hero:
            print(f"\n{self.player_hero.display_status()}")

        print(f"\n{Colors.BOLD}GAME MODES:{Colors.END}")
        print("1. Trust Battle Mode - 1v1 battles with trust system")
        print("2. Ranking Tournament - Fight to become X")
        print("3. Survival Mode - Endless waves of enemies")
        print("4. Story Mode - Experience the anime's story")
        print("5. Custom Battle - Create your own match")
        print("\n6. Save Game")
        print("7. Load Game")
        print("8. Exit")

    def custom_battle(self):
        """Create custom battle"""
        print(f"\n{Colors.HEADER}{'=' * 60}{Colors.END}")
        print(f"{Colors.BOLD}CUSTOM BATTLE{Colors.END}")
        print(f"{Colors.HEADER}{'=' * 60}{Colors.END}")

        heroes = HeroDatabase.get_all_heroes()

        print("\nSelect first hero:")
        for i, hero in enumerate(heroes, 1):
            print(f"{i}. {hero.hero_name}")

        try:
            choice1 = int(input("\nChoose (1-{}): ".format(len(heroes)))) - 1
            hero1 = heroes[choice1]

            print("\nSelect second hero:")
            for i, hero in enumerate(heroes, 1):
                print(f"{i}. {hero.hero_name}")

            choice2 = int(input("\nChoose (1-{}): ".format(len(heroes)))) - 1
            hero2 = heroes[choice2]

            # Create copies for battle
            h1 = Hero(hero1.name, hero1.hero_name, hero1.rank,
                      hero1.trust_value, hero1.power, hero1.special_ability)
            h2 = Hero(hero2.name, hero2.hero_name, hero2.rank,
                      hero2.trust_value, hero2.power, hero2.special_ability)

            print(f"\n{Colors.YELLOW}BATTLE: {h1.hero_name} vs {h2.hero_name}{Colors.END}")

            # Battle loop
            while h1.hp > 0 and h2.hp > 0:
                print(f"\n{h1.display_status()}")
                print(f"\n{h2.display_status()}")

                # Hero 1 turn (controlled)
                print(f"\n{Colors.BOLD}{h1.hero_name}'s turn{Colors.END}")
                hit, message = BattleSystem.battle_turn(h1, h2)
                print(message)

                if h2.hp <= 0:
                    print(f"\n{Colors.color_text(f'{h2.hero_name} defeated!', Colors.GREEN)}")
                    print(f"{h1.hero_name} wins!")
                    break

                # Hero 2 turn (controlled)
                print(f"\n{Colors.BOLD}{h2.hero_name}'s turn{Colors.END}")
                hit, message = BattleSystem.battle_turn(h2, h1)
                print(message)

                if h1.hp <= 0:
                    print(f"\n{Colors.color_text(f'{h1.hero_name} defeated!', Colors.RED)}")
                    print(f"{h2.hero_name} wins!")
                    break

        except (ValueError, IndexError):
            print(f"{Colors.RED}Invalid selection.{Colors.END}")

    def run(self):
        """Main game loop"""
        print(f"\n{Colors.CYAN}Welcome to To Be Hero X!{Colors.END}")
        print("In a world where powers come from public trust...")
        print("Will you rise to become X?")

        # Try to load or select hero
        if os.path.exists(self.save_file):
            load = input("\nLoad saved game? (y/n): ").lower()
            if load == 'y':
                self.load_game()

        if not self.player_hero:
            self.player_hero = self.select_hero()
            print(f"\n{Colors.GREEN}You selected {self.player_hero.hero_name}!{Colors.END}")

        while True:
            self.show_menu()

            try:
                choice = int(input("\nEnter choice (1-8): "))

                if choice == 1:  # Trust Battle
                    TrustBattleMode.play(self.player_hero)

                elif choice == 2:  # Ranking Tournament
                    RankingTournamentMode.play(self.player_hero)

                elif choice == 3:  # Survival
                    SurvivalMode.play(self.player_hero)

                elif choice == 4:  # Story Mode
                    StoryMode.play()

                elif choice == 5:  # Custom Battle
                    self.custom_battle()

                elif choice == 6:  # Save
                    self.save_game()

                elif choice == 7:  # Load
                    self.load_game()

                elif choice == 8:  # Exit
                    print(f"\n{Colors.CYAN}Thanks for playing To Be Hero X!{Colors.END}")
                    print("Remember: Your trust defines your power!")
                    sys.exit(0)

                else:
                    print(f"{Colors.RED}Invalid choice.{Colors.END}")

            except ValueError:
                print(f"{Colors.RED}Please enter a number.{Colors.END}")

            input("\nPress Enter to continue...")


# ============== Entry Point ==============
if __name__ == "__main__":
    game = ToBeHeroXGame()
    game.run()