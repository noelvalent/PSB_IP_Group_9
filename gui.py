#! /usr/bin/env python

from tkinter.font import Font
from tkinter import *

import threading

from game_manager import GameManager

# global variables
from log_util import file_log

root = Tk()
coin_strvar = StringVar()
player_control_dict = {}


# This Thread runs the turn-based system independently of the GUI routine.
class CoreThread(threading.Thread):
    def __init__(self, threadID, name, counter):
        # Just for Thread object
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter

    def run(self):
        # Thread main routine.
        self.core_loop()

    def core_loop(self):
        # Turn-base system's core loop
        from unit import Player

        # global variables
        global gm
        global game_view
        global player_control_dict
        game_switch = True

        # never-end loop
        while game_switch:
            # if for-statements is ended, a turn is gone.
            for slot in gm.unit_slot:
                # if game finish thread loop is stopped.
                if gm.is_player_win():
                    fontStyle = Font(size=18)
                    result_label = Label(game_view.Battler, text="You Win!", font=fontStyle)
                    game_view.Battler.create_window(240, 240, anchor=CENTER, window=result_label)
                    game_switch = False
                    # game finish log
                    file_log('Game finish. Player win.')
                    break

                elif gm.is_ai_win():
                    fontStyle = Font(size=18)
                    result_label = Label(game_view.Battler, text="You Lose...", font=fontStyle)
                    game_view.Battler.create_window(240, 240, anchor=CENTER, window=result_label)
                    game_switch = False
                    # game finish log
                    file_log('Game finish. Player Lose.')
                    break

                # turn start
                file_log(f'{slot.unit.name}\'s turn start')

                # if the unit is dead, its turn skip.
                if slot.unit.is_dead:
                    continue

                # is Player class' instance?
                if isinstance(slot.unit, Player):
                    # Show GUI for player
                    show_player_control()
                    result = slot.unit.do(**player_control_dict)
                else:
                    result = slot.unit.do(**{'player_list': gm.player_slot, 'previous_target': gm.previous_target})
                    gm.previous_target = result['previous_target']

                # Update displayed HP.
                slot.hp_string_var.set(slot.unit.hp_for_display())

                # is there message from Unit.do()
                if result is not None:
                    # logging on text box ui.
                    log(result)

                # if change level, update image.
                # but this routine is always run.
                rank_x, rank_y = slot.rank_position
                slot.update_level_image()
                game_view.Battler.create_image(rank_x, rank_y, anchor=NW, image=slot.rank_image)

                # turn end log
                file_log(f'{slot.unit.name}\'s turn start')
                game_view.Battler.update()


def log(result):
    # make verb
    if result['action'] == 'a':
        state = 'attacked'
    elif result['action'] == 'h':
        state = 'heal'
    elif result['action'] == 'd':
        state = 'is dead.'
    else:
        # if it has unexpected exception
        state = result['a']

    # formatted message
    msg = f'[Game Message]\n {result["name"]} {state} {result["target"]} with damage {result["damage"]}: +{result["exp"]}EXP \n'
    # update on GUI
    event_controller.txtLogBox.insert('1.0', msg)
    # write on file.
    file_log(msg)


def show_player_control():
    def attack_command():
        # a callback function for attack button
        global player_control_dict
        nonlocal top_level

        # button log
        file_log('send attack signal')
        player_control_dict.update({'state': 'a', 'target': gm.unit_slot[int(target_str_var.get())].unit})
        top_level.destroy()

    def heal_command():
        # a callback function for heal button
        global player_control_dict
        nonlocal top_level

        # button log
        file_log('send heal signal')
        player_control_dict.update({'state': 'h', 'target': None})
        top_level.destroy()

    from unit import AI

    global root
    global gm

    # make new GUI
    top_level = Toplevel(root)
    top_level.title('Player')
    top_level_x = root.winfo_x() + 480
    top_level_y = root.winfo_y()
    top_level.geometry(f'200x480+{top_level_x}+{top_level_y}')

    fontStyle = Font(size=18)
    label1 = Label(top_level, text='Attack', font=fontStyle, justify=CENTER)
    label1.pack(fill='x')

    # create target button
    slot_names = [str(x) for x in range(6)]
    target_str_var = StringVar(top_level, '1')
    for slot, slot_name in zip(gm.unit_slot, slot_names):
        unit = slot.unit
        if isinstance(unit, AI):
            radio_button = Radiobutton(
                top_level,
                text=unit.name,
                variable=target_str_var,
                value=slot_name,
                indicator=0,
            )
            if not slot.unit.is_dead:
                radio_button.pack(fill=X, ipady=5)

    attack_button = Button(
        top_level,
        text='Do Attack',
        command=attack_command,
        font=fontStyle,
        justify=CENTER
    )
    attack_button.pack(fill=X)

    label2 = Label(top_level, text='Heal', font=fontStyle, justify=CENTER)
    label2.pack(fill='x')

    heal_button = Button(
        top_level,
        text='Do Heal',
        command=heal_command,
        font=fontStyle,
        justify=CENTER
    )
    heal_button.pack(fill=X)

    # toplevel is opened log
    file_log('Player UI open')

    # set focus to this TopLevel
    top_level.focus_set()
    top_level.wait_window()


def initialize_game():
    '''Outputs slot data.'''

    global game_view

    # Background Image Update
    background = PhotoImage(file='./resources/bg.png')
    game_view.Battler.create_image(0, 0, anchor=NW, image=background)

    for slot in gm.unit_slot:
        # unit slot logginh
        file_log(f'{slot.unit.name}\'s slot is displaying')

        # create hp, name labels
        hp_label = Label(game_view.Battler, textvariable=slot.hp_string_var)
        hp_x, hp_y = slot.hp_position
        game_view.Battler.create_window(hp_x, hp_y, anchor=NW, window=hp_label)

        name_label = Label(game_view.Battler, textvariable=slot.name_string_var)
        name_x, name_y = slot.name_position
        game_view.Battler.create_window(name_x, name_y, anchor=NW, window=name_label)

        # label's string var initialize.
        slot.hp_string_var.set(slot.unit.hp_for_display())
        slot.name_string_var.set(slot.unit.name)

        # Character Image Update
        cx, cy = slot.character_position
        game_view.Battler.create_image(cx, cy, anchor=NW, image=slot.character_image)

        # hp update
        slot.hp_string_var.set(slot.unit.hp_for_display())

        # Level update
        lx, ly = slot.rank_position
        game_view.Battler.create_image(lx, ly, anchor=NW, image=slot.rank_image)

    # finish initialize log
    file_log('All slots are ready')


def restart():
    global gm
    global game_view

    file_log('game is restarted')

    # clear GUI component
    game_view.Battler.delete('all')
    event_controller.txtLogBox.delete('1.0', END)

    # initialize game data
    gm = GameManager()
    initialize_game()

    # Core System Thread Start
    core = CoreThread(1, 'core', 1)
    core.start()
    file_log('Core routine started')


if __name__ == '__main__':
    # start log
    file_log('game start')

    # window's title
    root.title("PSB Group 9")
    root.resizable(width=FALSE, height=FALSE)

    # Get 1st monitor's resolution
    from screeninfo import get_monitors

    monitor = get_monitors()[0]
    center_of_monitor = (monitor.width // 2 - 480, monitor.height // 2 - 240)
    # Because the window's Anchor is NW, move point as much as window size's half toward NW.
    root.geometry(f'480x480+{center_of_monitor[0]}+{center_of_monitor[1]}')
    # widnow's location width x height + north point + west point

    # create frame
    game_view = Frame(root)
    game_view.Battler = Canvas(game_view, width=480, height=480)
    game_view.Battler.pack(fill=BOTH)
    game_view.pack()

    # create coin label
    event_controller = Toplevel(root)
    event_controller_x = game_view.winfo_x() - 160
    event_controller_y = game_view.winfo_y()
    event_controller.geometry(f'300x480+{(center_of_monitor[0]-300)}+{center_of_monitor[1]}')
    fontStyle = Font(size=14)
    event_controller.Label1 = Label(event_controller, font=fontStyle)
    event_controller.Label1.place(x=10, y=8, height=21, width=50)
    event_controller.Label1.configure(text='''Coin''')

    # create Coin Button
    event_controller.Button1 = Button(event_controller, font=fontStyle)
    event_controller.Button1.place(x=8, y=35, height=32, width=32)
    event_controller.Button1.configure(pady="0")
    event_controller.Button1.configure(text='''C''')

    # create label
    event_controller.lblCoin = Label(event_controller, textvariable=coin_strvar, font=fontStyle, anchor=E)
    event_controller.lblCoin.place(x=60, y=39, height=21, width=220)
    event_controller.lblCoin.configure(text='''314,159''')

    # create label
    event_controller.Label2 = Label(event_controller, font=fontStyle)
    event_controller.Label2.place(x=8, y=75, height=23, width=164)
    event_controller.Label2.configure(text='''Game Log''')

    # create Game Log text box
    event_controller.txtLogBox = Text(event_controller)
    event_controller.txtLogBox.place(x=0, rely=0.221, width=300, height=320)
    event_controller.txtLogBox.configure(wrap="word")

    # create Option button
    event_controller.Button2 = Button(event_controller, font=fontStyle)
    event_controller.Button2.place(x=8, rely=0.919, height=27, width=64)
    event_controller.Button2.configure(pady="0")
    event_controller.Button2.configure(text='''Option''')

    # create Restart button
    event_controller.Button3 = Button(event_controller, font=fontStyle, command=restart)
    event_controller.Button3.place(x=224, rely=0.919, height=27, width=68)
    event_controller.Button3.configure(pady="0")
    event_controller.Button3.configure(text='''Restart''')

    # component loaded log
    file_log('All gui components are loaded completely')

    # game set up
    gm = GameManager()
    initialize_game()

    # Core System Thread Start
    core = CoreThread(1, 'core', 1)
    core.start()
    file_log('Core routine started')

    root.mainloop()
