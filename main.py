import pygame
import time
import random
import utils
import queue
import graphics
import pygame_textinput
import copy
pygame.mixer.pre_init(44100, -16, 1, 512)
pygame.init()


# global timer accumulator
accumulator = 0

# global variables for bpm setter
clicker_accumulator = 0
first_click = False
deltas = []

# global beat pattern position variables
sixteenth_position = 0
beat_position = 0
bar_position = 0

# global variable for swing rhythm
first_sixteenth = False

# determines paused state
pause = False

# determines if the user is inputting text. disable keyboard inputs until user hits
# return.
import_file_loop = False
export_file_loop = False
add_inst_loop = False
rem_inst_loop = False
edit_file_name = False

# initialize global variables
sixteenth_per_beat = 4
beats_per_bar = 4
num_bars = 2
sixteenth_duration = 150
vol = 0.1
swing = False
beat_pattern = utils.FULL_EMPTY_44
is_active = [1, 1, 1, 0, 0, 0]
swing_amount = 1

# logos for each instrument
logos = utils.initialize_logos()

# drum pattern is received as a list containing 3 lists which each contain
# 4 lists, corresponding to a beat in a measure. this splits up each list to
# match its instrument.

sounds = utils.load_sounds()

num_instruments = len(sounds)

utils.set_volume(sounds, vol)

# Initialize screen
display_width = 770
display_height = 200
gameDisplay = pygame.display.set_mode((display_width,display_height), pygame.RESIZABLE)
pygame.display.set_caption('Drum Looper')

# Initialize graphics
beat_grids = []
for i in range(4):
    beat_grid = graphics.Measure(gameDisplay, 50, 50, sixteenth_per_beat, beats_per_bar, beat_pattern[i], is_active, logos)
    beat_grids.append(beat_grid)
metronome = graphics.Metronome(gameDisplay, 5, 5)
end_coord = 50 + sixteenth_per_beat * beats_per_bar * 40
full_amount = sixteenth_duration * sixteenth_per_beat * beats_per_bar
# Weird parameters to make sure bar lines up with music.
rhythm_bar = graphics.RhythmBar(gameDisplay, 50 - 40, 40, end_coord, full_amount)
textinput = pygame_textinput.TextInput( 'fonts/digital-7.ttf', 15)

message = graphics.Message(gameDisplay)

info_bar = graphics.InfoBar(gameDisplay, 80, 5)

#------------------------------------------------------------------------------

def sixteenth_beat(clockTick):
    """
    A method for playing the smallest subdivision available in the app, a sixteenth
    note. Once the accumulator, as determined by the global game clock, goes over
    a certain threshold, check the current location in the beat pattern array
    and chooses whether or not to play a sound.
    """
    global accumulator
    global sixteenth_position
    global beat_position
    global bar_position
    global first_sixteenth

    accumulator += clockTick
    duration = sixteenth_duration

    # Determines if this is the start of a beat. Used for metronome graphic only.
    first_beat = sixteenth_position == 1

    # If swing is True, then adjust every first sixteenth note by 4/3 and every
    # second sixteenth note by 2/3.
    if swing:
        if first_sixteenth:
            duration *= 1 + 1/3 * swing_amount
        else:
            duration *= 1 - 1/3 * swing_amount
    if accumulator >= duration:
        accumulator = 0
        first_sixteenth = not first_sixteenth

        for i in range(num_instruments):
            n = beat_pattern[bar_position][i][beat_position][sixteenth_position]
            if n != 0 and is_active[i] == 1:
                pygame.mixer.Sound.play(sounds[i][n - 1])

        # Testing purposes, remove for actual submission
        # print((beat_pattern[0][beat_position][sixteenth_position], beat_pattern[1][beat_position][sixteenth_position], beat_pattern[2][beat_position][sixteenth_position]))
        #print(sixteenth_position, beat_position)
        s_p = sixteenth_position
        s_p_b = sixteenth_per_beat
        b_p = beat_position
        b_p_b = beats_per_bar
        ba_p = bar_position
        n_b = num_bars
        sixteenth_position, beat_position, bar_position = utils.increment_beat_position(s_p, s_p_b, b_p, b_p_b, ba_p, n_b)

        # Resets the rhythm bar at the end of every beat, helps keep it in sync with
        # the music.
        if beat_position < b_p:
            rhythm_bar.reset_bar()


    return first_beat

#------------------------------------------------------------------------------

def beat_clock(clockTick):
    """
    Accumulator for BPM setter. Resets once the spacing between taps is greater
    than 1200 ms.
    """
    global clicker_accumulator
    global first_click
    global deltas

    if first_click:
        clicker_accumulator += clockTick
    if clicker_accumulator >= 1200:
        clicker_accumulator = 0
        deltas = []
        first_click = False

#------------------------------------------------------------------------------


def beat_setter():
    """
    Takes the average of the last 4 spaced taps on the space bar and sets the current
    tempo as it.
    """
    global first_click
    global clicker_accumulator
    global sixteenth_duration
    global deltas

    if first_click:
        if len(deltas) == 4:
            deltas.pop(0)
        deltas.append(clicker_accumulator)
        change_tempo(sum(deltas) / (len(deltas) * 4))
        clicker_accumulator = 0
    first_click = True

#------------------------------------------------------------------------------

def import_file(file_name):
    """Take the json in the given file and import all global constants."""
    global sixteenth_per_beat
    global beats_per_bar
    global num_bars
    global sixteenth_duration
    global swing
    global beat_pattern
    global is_active
    global swing_amount

    if not utils.is_valid_file('saved_beats/' + file_name + '.drum'):
        message.set_message("Error")
        return False

    reset_global_timer()

    sixteenth_per_beat, beats_per_bar, num_bars, sixteenth_duration, swing, beat_pattern, is_active, swing_amount = utils.import_file('saved_beats/' + file_name + '.drum')

    set_graphics()
    message.set_message("Imported")
    resize_window()
    return True

#------------------------------------------------------------------------------

def export_file(file_name):
    """Take current global constants and export it to a given file."""
    utils.export_file(sixteenth_per_beat, beats_per_bar, num_bars, sixteenth_duration, swing, beat_pattern, is_active, swing_amount, 'saved_beats/' + file_name + '.drum')
    message.set_message("Saved")

#------------------------------------------------------------------------------

def bpm_loader(key):
    """Changes time signature. Supports 4/4, 3/4, and 6/8 (2 bars)."""
    global sixteenth_per_beat
    global beats_per_bar
    global beat_pattern
    global sixteenth_duration

    bpm = utils.mili_to_bpm(sixteenth_duration, sixteenth_per_beat)

    if key == pygame.K_j:
        sixteenth_per_beat = 4
        beats_per_bar = 4
        beat_pattern = utils.FULL_EMPTY_44
    if key == pygame.K_k:
        sixteenth_per_beat = 4
        beats_per_bar = 3
        beat_pattern = utils.FULL_EMPTY_34
    if key == pygame.K_l:
        sixteenth_per_beat = 6
        beats_per_bar = 4
        beat_pattern = utils.FULL_EMPTY_68

    reset_global_timer()

    sixteenth_duration = utils.bpm_to_mili(bpm, sixteenth_per_beat)

    resize_window()
    set_graphics()

#------------------------------------------------------------------------------

def change_num_bars(key):
    """Changes time signature. Supports 4/4, 3/4, and 6/8 (2 bars)."""
    global num_bars

    if key == pygame.K_1:
        num_bars = 1
    if key == pygame.K_2:
        num_bars = 2
    if key == pygame.K_4:
        num_bars = 4

    reset_global_timer()

#------------------------------------------------------------------------------

def resize_window():
    """Resize window depending on # of instruments and time signature"""
    global display_width
    global display_height
    if sixteenth_per_beat == 4 and beats_per_bar == 4:
        display_width = 770
    if sixteenth_per_beat == 4 and beats_per_bar == 3:
        display_width = 590
    if sixteenth_per_beat == 6 and beats_per_bar == 4:
        display_width = 1080
    display_height = 80 + 40 * sum(is_active)
    # reshape window to fit beat grid
    gameDisplay = pygame.display.set_mode((display_width, display_height))

#------------------------------------------------------------------------------

def reset_global_timer():
    """
    Resets the current state of the track/ui. Start beat from the beginning, moves
    rhythm bar back to the beginning.
    """
    global accumulator
    global clicker_accumulator
    global first_click
    global deltas
    global sixteenth_position
    global beat_position
    global bar_position
    global first_sixteenth

    accumulator = 0
    clicker_accumulator = 0
    first_click = False
    deltas = []
    sixteenth_position = 0
    beat_position = 0
    bar_position = 0
    first_sixteenth = False
    rhythm_bar.reset_bar()

#------------------------------------------------------------------------------

def set_graphics():
    """Method for re-initializing graphics."""
    global beat_grids
    global metronome
    global rhythm_bar
    beat_grids = []
    for i in range(4):
        beat_grid = graphics.Measure(gameDisplay, 50, 50, sixteenth_per_beat, beats_per_bar, beat_pattern[i], is_active, logos)
        beat_grids.append(beat_grid)
    metronome = graphics.Metronome(gameDisplay, 5, 5)
    end_coord = 50 + sixteenth_per_beat * beats_per_bar * 40
    full_amount = sixteenth_duration * sixteenth_per_beat * beats_per_bar
    # Weird parameters to make sure bar lines up with music.
    rhythm_bar = graphics.RhythmBar(gameDisplay, 50 - 40, 40, end_coord, full_amount)

#------------------------------------------------------------------------------

# If it aint swing, it aint jazz.
def swingify():
    """Change whether or not the beat swings."""
    global swing
    swing = not swing

#------------------------------------------------------------------------------

def increase_volume():
    global vol
    if vol < 1:
        vol += 0.1
    utils.set_volume(sounds, vol)

def decrease_volume():
    global vol
    if vol > 0.1:
        vol -= 0.1
    utils.set_volume(sounds, vol)

#------------------------------------------------------------------------------

def increase_swing():
    global swing_amount
    if swing_amount < 1:
        swing_amount += 0.1

def decrease_swing():
    global swing_amount
    if swing_amount > 0.1:
        swing_amount -= 0.1

#------------------------------------------------------------------------------

def increase_speed():
    global sixteenth_duration
    if sixteenth_duration < 300:
        change_tempo(sixteenth_duration - 10)

def decrease_speed():
    global sixteenth_duration
    if sixteenth_duration > 40:
        change_tempo(sixteenth_duration + 10)

#------------------------------------------------------------------------------

def change_tempo(new_duration):
    global sixteenth_duration
    sixteenth_duration = new_duration
    full_amount = sixteenth_duration * sixteenth_per_beat * beats_per_bar
    rhythm_bar.set_full_amount(full_amount)

#------------------------------------------------------------------------------

def add_instrument(inst_name):
    """
    Adds instrument to the board. Does nothing and displays error message if
    the instrument name is invalid.
    """
    global is_active
    global beat_grids
    ind = utils.string_to_index(inst_name)
    if ind < 0:
        message.set_message('error')
        return
    if ind >= 0:
        if is_active[ind] == 1:
            message.set_message('already active')
            return
        else:
            is_active[ind] = 1
    beat_grids = []
    for i in range(4):
        beat_grid = graphics.Measure(gameDisplay, 50, 50, sixteenth_per_beat, beats_per_bar, beat_pattern[i], is_active, logos)
        beat_grids.append(beat_grid)
    resize_window()
    message.set_message(inst_name + ' active')

#------------------------------------------------------------------------------

def remove_instrument(inst_name):
    """
    Same thing as above, except it removes the given instrument.
    """
    global is_active
    global beat_grids
    ind = utils.string_to_index(inst_name)
    if ind < 0:
        message.set_message('error')
        return
    if ind >= 0:
        if is_active[ind] == 0:
            message.set_message('already deactive')
            return
        else:
            is_active[ind] = 0
    beat_grids = []
    for i in range(4):
        beat_grid = graphics.Measure(gameDisplay, 50, 50, sixteenth_per_beat, beats_per_bar, beat_pattern[i], is_active, logos)
        beat_grids.append(beat_grid)
    resize_window()
    message.set_message(inst_name + ' removed')

#------------------------------------------------------------------------------

def draw_graphics(first_beat, ticker, draw_bar):
    """Method for drawing all the UI components."""
    gameDisplay.fill((0, 0, 0))
    beat_grids[bar_position].run_logic()
    beat_grids[bar_position].draw()
    metronome.draw(utils.mili_to_bpm(sixteenth_duration, sixteenth_per_beat), first_beat)
    # makes it so that the rhythm bar will still be synced after a pause.
    if ticker < 10 and draw_bar:
        rhythm_bar.draw(ticker, sum(is_active))
    if edit_file_name:
        gameDisplay.blit(textinput.get_surface(), (display_width - 150, 10))
    message.draw(display_width - 120, 25, ticker)
    info_bar.draw(vol, swing, pause, swing_amount, bar_position, num_bars)
    pygame.display.flip()

#------------------------------------------------------------------------------

def handle_key_press(event):
    """Handles all key presses except for pause and text inputs."""
    global edit_file_name
    global export_file_loop
    global import_file_loop
    global add_inst_loop
    global rem_inst_loop
    global textinput
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            increase_volume()
        elif event.key == pygame.K_DOWN:
            decrease_volume()
        elif event.key == pygame.K_LEFT:
            decrease_speed()
        elif event.key == pygame.K_RIGHT:
            increase_speed()
        elif event.key == pygame.K_s:
            swingify()
        elif event.key == pygame.K_SPACE:
            beat_setter()
        elif event.key == pygame.K_m:
            increase_swing()
        elif event.key == pygame.K_n:
            decrease_swing()
        elif event.key == pygame.K_e:
            textinput = pygame_textinput.TextInput( 'fonts/digital-7.ttf', 15)
            export_file_loop = True
            edit_file_name = True
        elif event.key == pygame.K_i:
            textinput = pygame_textinput.TextInput( 'fonts/digital-7.ttf', 15)
            import_file_loop = True
            edit_file_name = True
        elif event.key == pygame.K_a:
            textinput = pygame_textinput.TextInput( 'fonts/digital-7.ttf', 15)
            add_inst_loop = True
            edit_file_name = True
        elif event.key == pygame.K_r:
            textinput = pygame_textinput.TextInput( 'fonts/digital-7.ttf', 15)
            rem_inst_loop = True
            edit_file_name = True
        elif event.key == pygame.K_j or event.key == pygame.K_k or event.key == pygame.K_l:
            bpm_loader(event.key)
        elif event.key == pygame.K_1 or event.key == pygame.K_2 or event.key == pygame.K_4:
            change_num_bars(event.key)

#------------------------------------------------------------------------------

def pause_loop():
    """Pauses the global accumulator until 'p' is pressed again."""
    global pause
    global beat_grids
    global metronome
    global bar_position

    curr_bar_pos = bar_position

    while pause:
        draw_graphics(False, 0, curr_bar_pos == bar_position)

        for event in pygame.event.get():
            # GRAPHUCS LOGIC
            # ----------------------------
            beat_grids[bar_position].handle_events(event)
            # ----------------------------
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    bar_position = curr_bar_pos
                    pause = False
                elif event.key == pygame.K_1:
                    bar_position = 0
                elif event.key == pygame.K_2:
                    if not num_bars == 1:
                        bar_position = 1
                elif event.key == pygame.K_3:
                    if not num_bars == 1 and not num_bars == 2:
                        bar_position = 2
                elif event.key == pygame.K_4:
                    if not num_bars == 1 and not num_bars == 2:
                        bar_position = 3
                else:
                    handle_key_press(event)

#------------------------------------------------------------------------------

def main():
    """Main runner function for the program."""
    global pause
    global edit_file_name
    global textinput
    global import_file_loop
    global export_file_loop
    global add_inst_loop
    global rem_inst_loop

    clock = pygame.time.Clock()

    first_beat = sixteenth_beat(0)
    while True:
        ticker = clock.tick(480)
        first_beat = sixteenth_beat(ticker)

        beat_clock(ticker)

        draw_graphics(first_beat, ticker, True)

        events = pygame.event.get()
        if edit_file_name:
            if textinput.update(events):
                file_name = textinput.get_text()
                edit_file_name = False
                if export_file_loop:
                    export_file(file_name)
                    export_file_loop = False
                if import_file_loop:
                    import_file(file_name)
                    import_file_loop = False
                if add_inst_loop:
                    add_instrument(file_name)
                    add_inst_loop = False
                if rem_inst_loop:
                    remove_instrument(file_name)
                    rem_inst_loop = False
            for event in events:
                # GRAPHUCS LOGIC
                # ----------------------------
                beat_grids[bar_position].handle_events(event)
                # ----------------------------
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        edit_file_name = False
                        export_file_loop = False
                        import_file_loop = False
                        add_inst_loop = False
                        rem_inst_loop = False
        else:
            for event in events:
                # GRAPHUCS LOGIC
                # ----------------------------
                beat_grids[bar_position].handle_events(event)
                # ----------------------------
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        pause = True
                        pause_loop()
                    handle_key_press(event)


#------------------------------------------------------------------------------

main()
pygame.quit()
quit()
