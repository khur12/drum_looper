import json
import pygame
import os
import copy
import pprint
EMPTY_44 = [
                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],

                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],

                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],

                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],

                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],

                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
              ]
EMPTY_34 = [
                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],

                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],

                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],

                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],

                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]],

                  [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
              ]
EMPTY_68 = [
                  [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],

                  [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],

                  [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],

                  [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],

                  [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]],

                  [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0]]
              ]

FULL_EMPTY_44 = [copy.deepcopy(EMPTY_44), copy.deepcopy(EMPTY_44), copy.deepcopy(EMPTY_44) ,copy.deepcopy(EMPTY_44)]
FULL_EMPTY_34 = [copy.deepcopy(EMPTY_34), copy.deepcopy(EMPTY_34), copy.deepcopy(EMPTY_34) ,copy.deepcopy(EMPTY_34)]
FULL_EMPTY_68 = [copy.deepcopy(EMPTY_68), copy.deepcopy(EMPTY_68), copy.deepcopy(EMPTY_68) ,copy.deepcopy(EMPTY_68)]

def import_file(file_name):
    """
    Imports the given file as a json and parses it to extract the desired
    global constants.
    """
    with open(file_name) as json_data:
        data = json.load(json_data)
    sixteenth_per_beat = data['sixteenth_per_beat']
    beats_per_bar = data['beats_per_bar']
    num_bars = data['num_bars']
    sixteenth_duration = data['sixteenth_duration']
    swing = data['swing']
    beat_pattern = data['beat_pattern']
    is_active = data['is_active']
    swing_amount = data['swing_amount']
    return sixteenth_per_beat, beats_per_bar, num_bars, sixteenth_duration, swing, beat_pattern, is_active, swing_amount

def export_file(sixteenth_per_beat, beats_per_bar, num_bars, sixteenth_duration, swing, beat_pattern, is_active, swing_amount, file_name):
    """
    Takes the given parameters and exports it to the given file as a json.
    """
    data = {}
    data['sixteenth_per_beat'] = sixteenth_per_beat
    data['beats_per_bar'] = beats_per_bar
    data['num_bars'] = num_bars
    data['sixteenth_duration'] = sixteenth_duration
    data['swing'] = swing
    data['beat_pattern'] = beat_pattern
    data['is_active'] = is_active
    data['swing_amount'] = swing_amount
    with open(file_name, 'w') as outfile:
        json.dump(data, outfile)

def is_valid_file(file_name):
    """Checks if the given file is a correctly formatted .drum file."""
    if not os.path.isfile(file_name):
        return False
    if not file_name.endswith('.drum'):
        return False

    with open(file_name) as json_data:
        try:
            data = json.load(json_data)
        except ValueError:
            return False
    # Check that all attributes are in the json.
    if 'sixteenth_per_beat' not in data or \
       'beats_per_bar' not in data or \
       'num_bars' not in data or \
       'sixteenth_duration' not in data or \
       'swing' not in data or \
       'beat_pattern' not in data or \
       'is_active' not in data or \
       'swing_amount' not in data:
       return False
    if data['sixteenth_per_beat'] != 4 and data['sixteenth_per_beat'] != 6:
        return False
    if data['beats_per_bar'] != 4 and data['beats_per_bar'] != 3:
        return False
    if data['sixteenth_duration'] < 40 or data['sixteenth_duration'] > 300:
        return False
    if data['num_bars'] != 1 and data['num_bars'] != 2 and data['num_bars'] != 4:
        return False
    # Check that the beat_pattern array has the correct shape.
    beat_pattern = data['beat_pattern']
    if len(beat_pattern) != 4:
        return False
    for i in range(4):
        if len(beat_pattern[i]) != 6:
            return False
    for i in range(4):
        for j in range(6):
            if len(beat_pattern[i][j]) != data['beats_per_bar']:
                return False
    return True

def set_volume(sounds, vol):
    """
    Small helper function to readjust volume for all sounds.
    """
    for list in sounds:
        for sound in list:
            sound.set_volume(vol)

def increment_beat_position(sixteenth_position, sixteenth_per_beat, beat_position, beats_per_bar, bar_position, num_bars):
    """Logic for incrementing the position in the beat pattern array."""
    sixteenth_position += 1
    if sixteenth_position == sixteenth_per_beat:
        sixteenth_position = 0
        beat_position += 1
        if beat_position == beats_per_bar:
            beat_position = 0
            bar_position = (bar_position + 1) % num_bars
    return sixteenth_position, beat_position, bar_position

def load_sounds():
    """Loads all drum samples into separate lists."""
    hihat1 = pygame.mixer.Sound("sounds/hihat1.wav")
    hihat2 = pygame.mixer.Sound("sounds/hihat2.wav")
    hihat3 = pygame.mixer.Sound("sounds/hihat3.wav")
    hihat4 = pygame.mixer.Sound("sounds/hihat4.wav")
    hihats = [hihat1, hihat2, hihat3, hihat4]

    snare1 = pygame.mixer.Sound("sounds/snare1.wav")
    snare2 = pygame.mixer.Sound("sounds/snare2.wav")
    snare3 = pygame.mixer.Sound("sounds/snare3.wav")
    snares = [snare1, snare2, snare3]

    kick1 = pygame.mixer.Sound("sounds/kick1.wav")
    kick2 = pygame.mixer.Sound("sounds/kick2.wav")
    kick3 = pygame.mixer.Sound("sounds/kick3.wav")
    kicks = [kick1, kick2, kick3]

    cbell1 = pygame.mixer.Sound("sounds/cbell1.wav")
    cbell2 = pygame.mixer.Sound("sounds/cbell2.wav")
    cbell3 = pygame.mixer.Sound("sounds/cbell3.wav")
    cbells = [cbell1, cbell2, cbell3]

    tom1 = pygame.mixer.Sound("sounds/tb1.wav")
    tom2 = pygame.mixer.Sound("sounds/tb2.wav")
    tom3 = pygame.mixer.Sound("sounds/tb3.wav")
    toms = [tom1, tom2, tom3]

    ride1 = pygame.mixer.Sound("sounds/ride1.wav")
    ride2 = pygame.mixer.Sound("sounds/ride2.wav")
    ride3 = pygame.mixer.Sound("sounds/ride3.wav")
    ride4 = pygame.mixer.Sound("sounds/ride4.wav")
    rides = [ride1, ride2, ride3, ride4]

    return [hihats, snares, kicks, cbells, toms, rides]

def mili_to_bpm(mili, sixteenth_per_beat):
    """Converts milisecond sixteenth note subdivisions to bpm."""
    return int(60 * 1000 / (mili * sixteenth_per_beat))

def bpm_to_mili(bpm, sixteenth_per_beat):
    return int(60 * 1000 / (bpm * sixteenth_per_beat))

def initialize_logos():
    font = pygame.font.Font('fonts/digital-7.ttf', 15)
    logos = [font.render('H', True, (255, 255, 255)),
                    font.render('S', True, (255, 255, 255)),
                    font.render('K', True, (255, 255, 255)),
                    font.render('C', True, (255, 255, 255)),
                    font.render('T', True, (255, 255, 255)),
                    font.render('R', True, (255, 255, 255))]
    return logos

def string_to_index(str):
    """Converts name of instrument to its corresponding index."""
    if str == 'hihat' or str == 'h':
        return 0
    if str == 'snare' or str == 's':
        return 1
    if str == 'kick' or str == 'k':
        return 2
    if str == 'cowbell' or str == 'c':
        return 3
    if str == 'tom' or str == 'toms' or str == 't':
        return 4
    if str == 'ride' or str == 'r':
        return 5
    return -1
