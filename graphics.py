import pygame
import utils

# list of colors used to change on click
hihat_colors = [pygame.Color(120, 120, 120, 120),
                pygame.Color(255, 153, 153, 255),
                pygame.Color(255, 77, 77, 255),
                pygame.Color(180, 0, 0, 255),
                pygame.Color(100, 0, 0, 255)]
snare_colors = [pygame.Color(120, 120, 120, 120),
                pygame.Color(102, 255, 153, 255),
                pygame.Color(0, 200, 0, 255),
                pygame.Color(0, 122, 0, 255)]
kick_colors = [pygame.Color(120, 120, 120, 120),
               pygame.Color(153, 187, 255, 255),
               pygame.Color(0, 80, 255, 255),
               pygame.Color(0, 0, 153, 255)]
cbell_colors = [pygame.Color(120, 120, 120, 120),
                pygame.Color(244, 208, 63, 255),
                pygame.Color(212, 172, 13),
                pygame.Color(125, 102, 8)]
tom_colors = [pygame.Color(120, 120, 120, 120),
                pygame.Color(165, 105, 189),
                pygame.Color(108, 52, 131),
                pygame.Color(74, 35, 90)]
ride_colors = [pygame.Color(120, 120, 120, 120),
               pygame.Color(255, 194, 153, 255),
               pygame.Color(255, 133, 51, 255),
               pygame.Color(179, 71, 0, 255),
               pygame.Color(102, 41, 0, 255)]
main_colors = [hihat_colors, snare_colors, kick_colors, cbell_colors, tom_colors, ride_colors]

LEFT = 1
RIGHT = 3

class Button(pygame.sprite.Sprite):
    """
    Button class. Superclass of a sprite that performs a function on click and
    does actions on hover. Changes color on click, based on the list of colors
    it takes as a parameter.
    """
    def __init__(self, x, y, width, height, callback_left, callback_right, color_list, initial_color):
        super().__init__()

        self.color_list = color_list
        # Transform colors into images for the sprite to use.
        self.image_list = []
        for color in color_list:
            image_temp = pygame.Surface((width, height))
            image_temp.fill(color)
            pygame.transform.scale(image_temp, (width, height))
            self.image_list.append(image_temp)
        self.hover_image_list = []
        for color in color_list:
            image_temp = pygame.Surface((width, height))
            new_color = pygame.Color(min(255, color.r + 50),
                                     min(255, color.g + 50),
                                     min(255, color.b + 50))
            image_temp.fill(new_color)
            pygame.transform.scale(image_temp, (width, height))
            self.hover_image_list.append(image_temp)
        self.click_image_list = []
        for color in color_list:
            base_image = pygame.Surface((width, height))
            base_image.fill(pygame.Color(0, 0, 0))
            image_temp = pygame.Surface((int(width * 2 / 3), int(height *2 /3)))
            new_color = pygame.Color(min(255, color.r + 50),
                                     min(255, color.g + 50),
                                     min(255, color.b + 50))
            image_temp.fill(new_color)
            base_image.blit(image_temp, (width / 6, height / 6))
            self.click_image_list.append(base_image)
        # Sets the original image color
        self.image_normal = self.image_list[initial_color]
        self.image_hover = self.hover_image_list[initial_color]
        self.image_down = self.click_image_list[initial_color]

        self.image_ind = initial_color
        self.num_images = len(self.image_list)

        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=(x, y))
        # This function will be called when the button gets pressed.
        self.callback_left = callback_left
        self.callback_right = callback_right
        self.button_down = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.image = self.image_down
                self.button_down = True
        elif event.type == pygame.MOUSEBUTTONUP:
            # If the rect collides with the mouse pos.
            if self.rect.collidepoint(event.pos) and self.button_down:

                if event.button == LEFT:
                    self.callback_left()  # Call the function.
                    # Change color, rolling over to the first index.
                    self.image_ind = (self.image_ind + 1) % self.num_images
                    self.image_normal = self.image_list[self.image_ind]
                    self.image_hover = self.hover_image_list[self.image_ind]
                    self.image_down = self.click_image_list[self.image_ind]
                if event.button == RIGHT:
                    self.callback_right()  # Call the function.
                    # Change color to first color
                    self.image_ind = 0
                    self.image_normal = self.image_list[self.image_ind]
                    self.image_hover = self.hover_image_list[self.image_ind]
                    self.image_down = self.click_image_list[self.image_ind]
                self.image = self.image_hover
            self.button_down = False

        elif event.type == pygame.MOUSEMOTION:
            collided = self.rect.collidepoint(event.pos)
            if collided and not self.button_down:
                self.image = self.image_hover
            elif not collided:
                self.image = self.image_normal

#------------------------------------------------------------------------------

class Beat:
    """
    Describes a group of buttons in a row, as determined by how many
    sixteenth notes are in a single beat. Essentially, the smallest
    grouping of buttons that are more or less identical.
    """
    def __init__(self, screen, x, y, num_sixteenth, beat_map, color_list):
        self.beat_map = beat_map
        self.screen = screen
        x_coord = x
        y_coord = y
        self.all_sprites = pygame.sprite.Group()
        num_notes = len(color_list)
        # Creates a row of buttons with num_sixteenth buttons.
        for i in range(num_sixteenth):
            # Defines a function so that each button changes a certain index
            # on the main beat map.
            def inc_note(i=i):
                beat_map[i] = (beat_map[i] + 1) % num_notes
            def reset_note(i=i):
                beat_map[i] = 0
            button = Button(x_coord + i * 40, y_coord, 30, 30, inc_note, reset_note,
                            color_list, beat_map[i])
            self.all_sprites.add(button)

    def get_sprites(self):
        return self.all_sprites

#------------------------------------------------------------------------------

class Measure:
    """
    Describes a group of beats, also called a bar. For example, a 4 by 4 measure will
    have 12 total Beat classes, 4 beats per measure and 3 instrument tracks.
    x and y coordinates determine where the measure is drawn, sixteenth_per_beat
    determines how many buttons per beat, beats_per_bar desribes how many total
    beats in one row, beat_pattern determines initial conditions and is also the
    same beat map that generates sound.
    """
    def __init__(self, screen, x, y, sixteenth_per_beat,
                 beats_per_bar, beat_pattern, is_active, logos):

        self.is_active = is_active

        self.beat_pattern = beat_pattern
        self.screen = screen

        self.all_sprites = pygame.sprite.Group()

        self.sixteenth_per_beat = sixteenth_per_beat
        self.beats_per_bar = beats_per_bar

        self.x = x
        self.y = y

        self.logos = logos

        spacing = 0
        for i in range(len(self.is_active)):
            if self.is_active[i] == 1:
                self.set_beat_sprites(beats_per_bar, screen, self.x, self.y + spacing * 40,
                                sixteenth_per_beat, beat_pattern[i], main_colors[i])
                spacing += 1

    def set_beat_sprites(self, beats_per_bar, screen, x_coord,
                         y_coord, sixteenth_per_beat, beat_map,
                         color_list):
        """
        Range over the number of beats in the bar and defines a Beat for each one.
        May change to accomodate uneven time signatures.
        """
        for j in range(beats_per_bar):
            new_button = Beat(screen, x_coord + j * 40 * sixteenth_per_beat + 10 * j,
                              y_coord, sixteenth_per_beat,
                              beat_map[j], color_list)
            # Include all the sprites in each Beat into main sprite Group.
            for sprite in new_button.get_sprites():
                self.all_sprites.add(sprite)


    def handle_events(self, event):
        for button in self.all_sprites:
            button.handle_event(event)

    def run_logic(self):
        self.all_sprites.update()

    def draw(self):
        self.all_sprites.draw(self.screen)
        divider = pygame.Surface((4,40 + 40 * (sum(self.is_active) - 1)))
        divider.fill(pygame.Color(200, 200, 200))
        for i in range(1, self.beats_per_bar):
            self.screen.blit(divider,
                            (self.x - 12+ 40 * self.sixteenth_per_beat * i + 10 * i,
                            self.y - 5))

        spacing = 0
        for i in range(len(self.is_active)):
            if self.is_active[i] == 1:
                self.screen.blit(self.logos[i], (self.x - 10, self.y + 40 * spacing))
                spacing += 1



#------------------------------------------------------------------------------

class Metronome:
    """
    Class for displaying the metronome. Draws a number, which describes bpm,
    and a small red square that pulses on every start of a beat. This is done by
    feeding a bool called first_beat into the main draw function.
    """
    def __init__(self, screen, x, y):
        self.screen = screen
        self.x = x
        self.y = y

        image = pygame.Surface((10, 10))
        image.fill(pygame.Color(255, 0, 0))
        self.on_blink = image

        image = pygame.Surface((10, 10))
        image.fill(pygame.Color(0, 0, 0))
        self.off_blink = image

    def draw(self, bpm, first_beat):
        font = pygame.font.Font( 'fonts/digital-7.ttf', 25 )
        image = font.render(str(bpm), True, (255, 255, 255) )
        self.screen.blit(image, (self.x, self.y))

        if first_beat:
            self.screen.blit(self.on_blink, (self.x + 35, self.y + 7))
        else:
            self.screen.blit(self.off_blink, (self.x + 35, self.y + 7))

#------------------------------------------------------------------------------

class RhythmBar:
    """
    Class for drawing the bar that indicates where the current track is on the UI.
    """
    def __init__(self, screen, x, y, end, full):
        self.screen = screen
        self.x = x
        self.y = y
        self.end = end
        self.color = (255,210,10)
        self.full = full
        self.accumulator = 0

    def set_full_amount(self, new_full):
        self.full = new_full

    def reset_bar(self):
        self.accumulator = 0

    def inc_accumulator(self, ticker):
        self.accumulator += ticker
        if self.accumulator >= self.full:
            self.accumulator = 0

    def draw(self, ticker, num_rows):
        self.inc_accumulator(ticker)
        percent = self.accumulator / self.full
        current_location = int(self.x + (self.end - self.x) * percent)

        length = 10 + 40 * num_rows
        block = pygame.Surface((4,length))
        block.fill(pygame.Color(255, 210, 10))
        self.image = block

        # Some weird thing to make sure the bar lines up with the music.
        if current_location > 40:
            self.screen.blit(self.image, (current_location, self.y))

#------------------------------------------------------------------------------

class Message:
    """
    Class for displaying messages that fade away after a certain amount of time.
    """
    def __init__(self, screen):
        self.screen = screen
        self.message = ""
        self.full = 2000
        self.fade = 4000
        self.elapsed = 0
    def set_message(self, str):
        self.message = str
        self.elapsed = 0
    def draw(self, x, y, ticker):
        font = pygame.font.Font( 'fonts/digital-7.ttf', 15 )
        text = font.render(self.message, True, (255, 255, 255) )
        surface=pygame.Surface((80, 15))
        surface.fill((0, 0, 0))
        # need to blit text on to surface, which can then have its alpha value altered.
        surface.blit(text, (0, 0))
        if self.elapsed <= self.fade:
            alpha = 255
            if self.elapsed >= self.full:
                alpha = 255 - int(255 * (self.elapsed - self.full) / (self.fade - self.full))
            surface.set_alpha(alpha)
            self.screen.blit(surface, (x, y))
        self.elapsed += ticker

#------------------------------------------------------------------------------

class InfoBar:
    """
    Class for displaying some parts of the information bar, includes volume,
    swing state, pause state.
    """
    def __init__(self, screen, x, y):
        self.screen = screen
        self.x = x
        self.y = y
    def draw(self, vol, swing, pause, swing_amount, bar_position, num_bars):
        font = pygame.font.Font( 'fonts/digital-7.ttf', 25 )
        volume = font.render('VOL: ' + str(round(vol*10)) + '.0', True, (255, 255, 255) )
        self.screen.blit(volume, (self.x , self.y))
        pos = font.render(str(bar_position + 1) + '/' + str(num_bars), True, (255, 255, 255) )
        self.screen.blit(pos, (self.x + 95, self.y))
        if swing:
            s = font.render('S: ' + str(round(swing_amount * 10)) + '.0', True, (255, 255, 255))
            self.screen.blit(s, (self.x + 150, self.y))
        if pause:
            p = font.render('P', True, (255, 255, 255))
            self.screen.blit(p, (self.x + 240, self.y))
