import json
import os
import re

import cv2
import pygame.freetype
import pygame.image

pattern = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\s(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\s(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
text = ["Foto Frontale", "Profilo sinistro", "Profilo destro", "Dall'alto", "Dal basso"]


class UserManager:
    def __init__(self, colors_path: str = './data/colors.json', db_path: str = 'data/images/', video_source: int | str = 0):
        self._colors_path = colors_path
        self._db_path = db_path
        self._colors = self._load_colors()
        self._source = video_source

    def add_user(self):
        username = self._check_username()
        self.add_user_color(username)
        screen_width, screen_height = (620, 480)
        screen, cap, font = self._init_pygame(screen_width, screen_height)
        running = True
        num_photo = 0
        while running:
            ret, frame = cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_rgb = cv2.resize(frame_rgb, (screen_width, screen_height))
                pygame_frame = pygame.image.frombuffer(frame_rgb.tostring(), (screen_width, screen_height), 'RGB')
                screen.blit(pygame_frame, (0, 0))

            font.render_to(screen, (screen_width / 2, 50), text[num_photo], (0, 0, 0))
            font.render_to(screen, (50, 400), 'Premi spazio per scattare la foto', (255, 0, 0))
            pygame.display.update()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if num_photo < 5:
                            cv2.imwrite(self._db_path + username + '.jpg', frame)
                            print('Foto scattata!')
                            num_photo += 1
            if num_photo >= 1:
                running = False

        cap.release()
        pygame.quit()

    def update_colors(self, user_name, color):
        with open(self._colors_path, 'w') as file:
            self._colors[user_name] = color
            json.dump(self._colors, file)
        print('Color saved! ')

    def _load_colors(self) -> dict:
        with open(self._colors_path, 'r') as file:
            colors = json.load(file)
        return colors

    def _init_pygame(self, screen_width, screen_height):
        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Photo')

        cap = cv2.VideoCapture(self._source)
        font = pygame.freetype.Font(None, 36)
        return screen, cap, font

    def _check_username(self):
        while True:
            user_name = input('Inserisci il tuo nome ')
            file_path = self._db_path + user_name + '.jpg'
            if os.path.exists(file_path):
                print('Name già usato!')
            else:
                break
        return user_name

    def add_user_color(self, user_name):
        while True:
            color = input('Inserisci il tuo colore preferito(max value: 255 255 255) ')
            if re.match(pattern, color):
                break
            else:
                print('Colore non corretto!')

        color_tuple = (int(color.split()[0]), int(color.split()[1]), int(color.split()[2]))
        self.update_colors(user_name, color_tuple)

    def get_user_color(self, username):
        return tuple(self._colors[username])
