from random import randint
from character_types import CharacterTypes
from gui import file_log

class Unit:
    def __init__(self, ct):
        ''' Make an Unit for Game

        :param hp (int): Heath Point
        :param e (int): Exp Point
        :param ct (CLASS_TYPE): Class Type
        '''
        self.is_dead = False
        self._health_point = 100
        self.exp = 0
        self._level = 1
        self.character_type = ct

    # Constrains the hp to not exceed 100.
    # implemented getters just in case.
    @property
    def health_point(self):
        return self._health_point

    @health_point.setter
    def health_point(self, health_point):
        # if total health point is over 100, do not any thing
        # or not if hp is under 0, just input 0
        if 100 >= health_point > 0:
            self._health_point = health_point
        elif health_point < 0:
            self._health_point = 0

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, level):
        # do not level up more than 10.
        if level <= 10:
            self._level = level

    def hp_for_display(self):
        # make formatted str
        return f'HP: {self.health_point}/100'

    def attack(self, target):
        '''randomize integer for atk, and deducting hp from target'''

        # random attack point depending on class type.
        if self.character_type == CharacterTypes.warrior.value:
            attack_point = randint(5, 20)
        elif self.character_type == CharacterTypes.tanker.value:
            attack_point = randint(1, 10)

        # random defend point depending on class type.
        if target.character_type == CharacterTypes.tanker.value:
            defend_point = randint(5, 15)
        elif target.character_type == CharacterTypes.warrior.value:
            defend_point = randint(1, 10)

        # calculate total damage.
        total_damage = attack_point - defend_point + randint(-5, 10)

        # if total damage is negative, do not any thing.
        if total_damage > 0:
            target.health_point = target.health_point - total_damage

        # after attack, calculate exp for both the AI and the user
        if total_damage > 0:
            self.exp = self.exp + (total_damage * 10)  # for attacker exp

        # for defender exp
        if total_damage > 10:
            target.exp += (defend_point * 1.2)
        elif total_damage <= 0:
            target.exp += (defend_point * 1.5)

        # proceed level
        while (self.exp // 100) > 0:
            self.exp -= 100
            self.level = self.level + 1

        while (target.exp // 100) > 0:
            target.exp -= 100
            target.level = target.level + 1

        # return message
        if total_damage > 0:
            return {
                'damage': total_damage,
                'exp': total_damage,
            }
        else:
            return {
                'damage': 0,
                'exp': 0,
            }

    def heal(self):
        # assuming the fixed value for healing is 15
        self.health_point = self.health_point + 15
        return {
            'damage': 15,
            'exp': 0,
        }

    def do(self, *args, **kwargs):
        '''
        Unit do someting. This is Abstract Method.
        Whenever the turn comes, do() is executed.
        '''
        pass

    def eval_self(self):
        '''
        proceed unit's dead.
        '''
        if self.health_point <= 0:
            # character is dead
            self.is_dead = True


class Player(Unit):
    def __init__(self, ct):
        self.name = ''
        self.set_name()
        super().__init__(ct)

        file_log(f'Player {self.name} is created')

    def set_name(self):
        '''
        set player name from user input.
        '''

        from tkinter.simpledialog import askstring
        name = askstring('Create Character', 'What is this character\'s new name')
        self.name = name

    def do(self, *args, **kwargs):
        if kwargs['state'] == 'a':
            target = kwargs['target']
            result = self.attack(target)
        elif kwargs['state'] == 'h':
            result = self.heal()

        self.eval_self()
        return {
            'name': self.name,
            'action': kwargs['state'],
            'target': target.name if kwargs.get('target') else 'itself',
            'damage': result['damage'], # atk or heal
            'exp': result['exp'],
        }


class AI(Unit):
    def __init__(self, ct):
        self.name = 'AI' + str(randint(10, 99))
        self.manager = None
        super().__init__(ct)

    def do(self, *args, **kwargs):
        print(f'{self.name}\'s Turn.')

        self.eval_self()

    def choose_target(self):
        '''choose the lowest health point from the user's characters'''
        minHealth = 100
        i = 0
        index = 0
        for health in playerHealth:  # playerHealth is a list for the player's characters' health
            if minHealth > health and health != 0:
                minHealth = health
                index = i
            i += 1



