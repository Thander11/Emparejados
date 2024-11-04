# MIT License
# Copyright (c) 2024 Raúl Martín-Romo Sánchez
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import cv2
import numpy as np
import random
import os

# Dimensiones del tablero y las cartas
CARD_WIDTH, CARD_HEIGHT = 100, 150
CARD_SPACING = 20  # Espacio entre las cartas

# Dimensiones del tablero por dificultad
DIFFICULTY_SETTINGS = {
    'Facil': (3, 2),   # 3x2
    'Medio': (4, 4),   # 4x4
    'Dificil': (4, 8), # 6x6
    'Experto': (5, 12)  # 8x8
}

# Variables globales de la dificultad seleccionada
selected_difficulty = None
ROWS, COLS = 0, 0

# Definición de colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
RED = (0, 0, 255)
ORANGE = (0, 164, 250)

# Dimensiones predeterminadas para pantalla completa
FULL_SCREEN_WIDTH = 1920
FULL_SCREEN_HEIGHT = 1080

# Tamaño del tablero
BOARD_WIDTH = COLS * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING
BOARD_HEIGHT = ROWS * (CARD_HEIGHT + CARD_SPACING) - CARD_SPACING

# Definir las dimensiones y posición del botón Exit
EXIT_BUTTON_WIDTH = 150
EXIT_BUTTON_HEIGHT = 55
EXIT_BUTTON_MARGIN = 30  # Margen desde los bordes de la pantalla

# Definir las dimensiones y posición del botón Help
HELP_BUTTON_WIDTH = 150
HELP_BUTTON_HEIGHT = 55
HELP_BUTTON_MARGIN = 30

def draw_rounded_rectangle(img, top_left, bottom_right, color, radius=20):
    # Dibuja el rectángulo con esquinas redondeadas
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    # Dibuja los cuatro rectángulos que forman el cuerpo
    cv2.rectangle(img, (x1 + radius, y1), (x2 - radius, y2), color, -1)  # Cuerpo central
    cv2.rectangle(img, (x1, y1 + radius), (x2, y2 - radius), color, -1)  # Cuerpo central

    # Dibuja los cuatro elipses que forman las esquinas
    cv2.ellipse(img, (x1 + radius, y1 + radius), (radius, radius), 180, 0, 90, color, -1)  # Esquina superior izquierda
    cv2.ellipse(img, (x2 - radius, y1 + radius), (radius, radius), 270, 0, 90, color, -1)  # Esquina superior derecha
    cv2.ellipse(img, (x1 + radius, y2 - radius), (radius, radius), 90, 0, 90, color, -1)   # Esquina inferior izquierda
    cv2.ellipse(img, (x2 - radius, y2 - radius), (radius, radius), 0, 0, 90, color, -1)

class Animaciones:
    # Función para dibujar un círculo en el centro de una carta
    def draw_circle_on_card(x, y, color=GREEN, radius=20, thickness=5, duration=500):
        center_x = x + CARD_WIDTH // 2
        center_y = y + CARD_HEIGHT // 2
        cv2.circle(screen, (center_x, center_y), radius, color, thickness)
        cv2.imshow('Memory Game', screen)
        cv2.waitKey(duration)

    # Función para dibujar una cruz en una carta
    def draw_cross_on_card(x, y, color=RED, thickness=5, duration=500):
        start_point1 = (x + 10, y + 10)
        end_point1 = (x + CARD_WIDTH - 10, y + CARD_HEIGHT - 10)
        start_point2 = (x + 10, y + CARD_HEIGHT - 10)
        end_point2 = (x + CARD_WIDTH - 10, y + 10)
        
        cv2.line(screen, start_point1, end_point1, color, thickness)
        cv2.line(screen, start_point2, end_point2, color, thickness)
        cv2.imshow('Memory Game', screen)
        cv2.waitKey(duration)
        
    # Función para voltear una carta con animación de giro
    def flip_card(card_image, x, y, back_image=None, back_color=(255, 0, 0)):
        if back_image is None:
            card_back = np.zeros((CARD_HEIGHT, CARD_WIDTH, 3), dtype=np.uint8)
            cv2.rectangle(card_back, (0, 0), (CARD_WIDTH, CARD_HEIGHT), back_color, -1)
        else:
            card_back = back_image

        for scale in np.linspace(1, 0, num=10):
            screen[y:y + CARD_HEIGHT, x:x + CARD_WIDTH] = (0, 0, 0)
            scaled_width = max(1, int(CARD_WIDTH * scale))
            scaled_image = cv2.resize(card_back, (scaled_width, CARD_HEIGHT))
            offset_x = (CARD_WIDTH - scaled_width) // 2
            screen[y:y + CARD_HEIGHT, x + offset_x:x + offset_x + scaled_width] = scaled_image
            cv2.imshow('Memory Game', screen)
            cv2.waitKey(15)

        for scale in np.linspace(0, 1, num=10):
            screen[y:y + CARD_HEIGHT, x:x + CARD_WIDTH] = (0, 0, 0)
            scaled_width = max(1, int(CARD_WIDTH * scale))
            scaled_image = cv2.resize(card_image, (scaled_width, CARD_HEIGHT))
            offset_x = (CARD_WIDTH - scaled_width) // 2
            screen[y:y + CARD_HEIGHT, x + offset_x:x + offset_x + scaled_width] = scaled_image
            cv2.imshow('Memory Game', screen)
            cv2.waitKey(15)

        screen[y:y + CARD_HEIGHT, x:x + CARD_WIDTH] = card_image
        cv2.imshow('Memory Game', screen)
        cv2.waitKey(120)
        
class Menu:
    # Función para mostrar el menú de selección de dificultad
    @staticmethod
    def draw_difficulty_menu():
        # Cargar la imagen de fondo
        menu_background_image = cv2.imread('./imagenes/FondoMenu.jpg')
        menu_background_image = cv2.resize(menu_background_image, (FULL_SCREEN_WIDTH, FULL_SCREEN_HEIGHT))
        
        # Crear la pantalla usando el fondo
        menu_screen = menu_background_image.copy()
        
        # Título del menú
        title = 'EMPAREJADOS'
        title_size = cv2.getTextSize(title, cv2.FONT_HERSHEY_SIMPLEX, 5, 2)[0]
        title_x = (FULL_SCREEN_WIDTH - title_size[0]) // 2
        cv2.putText(menu_screen, title, (title_x, 200), 
                    cv2.FONT_HERSHEY_SIMPLEX, 5, RED, 11)

        # Crear botones para cada dificultad
        button_height = 80
        button_width = 300
        button_spacing = 40
        start_y = 300
        
        # Almacenar las posiciones de los botones
        button_positions = []
        
        # Agregar botones de dificultad
        for i, difficulty in enumerate(DIFFICULTY_SETTINGS.keys()):
            # Calcular posición del botón
            button_x = (FULL_SCREEN_WIDTH // 2 - button_width) // 2
            button_y = start_y + i * (button_height + button_spacing)
            
            # Dibujar el botón con esquinas redondeadas
            draw_rounded_rectangle(menu_screen, 
                                (button_x, button_y),
                                (button_x + button_width, button_y + button_height),
                                ORANGE, radius=20)
            
            # Añadir texto al botón
            text_size = cv2.getTextSize(difficulty, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
            text_x = button_x + (button_width - text_size[0]) // 2
            text_y = button_y + (button_height + text_size[1]) // 2
            cv2.putText(menu_screen, difficulty, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2)
            
            # Guardar la posición y dimensiones del botón
            button_positions.append((button_x, button_y, button_width, button_height, difficulty))
        
        # Agregar botón de salida
        exit_button_x = (FULL_SCREEN_WIDTH // 2 - button_width) // 2
        exit_button_y = start_y + len(DIFFICULTY_SETTINGS) * (button_height + button_spacing)
        
        draw_rounded_rectangle(menu_screen,
                            (exit_button_x, exit_button_y),
                            (exit_button_x + button_width, exit_button_y + button_height),
                            RED, radius=20)
        
        exit_text = "Salir"
        text_size = cv2.getTextSize(exit_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = exit_button_x + (button_width - text_size[0]) // 2
        text_y = exit_button_y + (button_height + text_size[1]) // 2
        cv2.putText(menu_screen, exit_text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2)
        
        # Agregar el botón de salida a las posiciones
        button_positions.append((exit_button_x, exit_button_y, button_width, button_height, "EXIT"))
        
        return menu_screen, button_positions

    @staticmethod
    def handle_menu_click(x, y, button_positions):
        # Verificar si el clic fue en algún botón
        for button_x, button_y, width, height, action in button_positions:
            if (button_x <= x <= button_x + width and 
                button_y <= y <= button_y + height):
                return action
        return None

    @staticmethod
    def select_difficulty():
        menu_screen, button_positions = Menu.draw_difficulty_menu()
        selected_action = [None]  # Usar lista para poder modificarla desde el callback
        
        def menu_mouse_callback(event, x, y, flags, param):
            if event == cv2.EVENT_LBUTTONDOWN:
                action = Menu.handle_menu_click(x, y, button_positions)
                if action:
                    selected_action[0] = action

        cv2.namedWindow('Memory Game', cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty('Memory Game', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback('Memory Game', menu_mouse_callback)
        
        while selected_action[0] is None:
            cv2.imshow('Memory Game', menu_screen)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                selected_action[0] = "EXIT"
        
        return selected_action[0]
            
class Botones:
    # Función para dibujar el botón Exit
    def draw_exit_button(screen):
        x = FULL_SCREEN_WIDTH - EXIT_BUTTON_WIDTH - EXIT_BUTTON_MARGIN
        y = EXIT_BUTTON_MARGIN
        
        # Dibujar el botón con esquinas redondeadas
        draw_rounded_rectangle(screen, 
                            (x, y), 
                            (x + EXIT_BUTTON_WIDTH, y + EXIT_BUTTON_HEIGHT), 
                            BLUE, radius=20)
        
        # Añadir texto al botón
        cv2.putText(screen, 'Menu', (x + 40, y + 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2)
        
        return x, y


    # Función para dibujar el botón Help
    def draw_help_button(screen):
        x = HELP_BUTTON_MARGIN
        y = EXIT_BUTTON_MARGIN
        
        # Dibujar el botón con esquinas redondeadas
        draw_rounded_rectangle(screen, 
                            (x, y), 
                            (x + HELP_BUTTON_WIDTH, y + HELP_BUTTON_HEIGHT), 
                            BLUE, radius=20)
        
        # Añadir texto al botón
        cv2.putText(screen, 'Help', (x + 40, y + 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2)
        
        return x, y


    # Función para detectar si se ha hecho clic en el botón Exit
    def is_exit_button_clicked(mouse_x, mouse_y, button_x, button_y):
        return (button_x <= mouse_x <= button_x + EXIT_BUTTON_WIDTH and
                button_y <= mouse_y <= button_y + EXIT_BUTTON_HEIGHT)

    # Función para detectar si se ha hecho clic en el botón Help
    def is_help_button_clicked(mouse_x, mouse_y, button_x, button_y):
        return (button_x <= mouse_x <= button_x + HELP_BUTTON_WIDTH and
                button_y <= mouse_y <= button_y + HELP_BUTTON_HEIGHT)

    # Función para encontrar una pareja no descubierta
    def find_unmatched_pair(board, flipped):
        # Crear un diccionario para almacenar las posiciones de las cartas
        card_positions = {}
        
        for i in range(ROWS):
            for j in range(COLS):
                if not flipped[i, j]:  # Solo considerar cartas no volteadas
                    card_value = board[i, j]
                    if card_value in card_positions:
                        # Encontramos un par
                        return (i, j), card_positions[card_value]
                    else:
                        card_positions[card_value] = (i, j)
        return None, None

    # Función para resaltar una carta con borde rojo
    def highlight_card(screen, row, col, margin_x, margin_y):
        x = margin_x + col * (CARD_WIDTH + CARD_SPACING)
        y = margin_y + row * (CARD_HEIGHT + CARD_SPACING)
        thickness = 3
        cv2.rectangle(screen, 
                    (x - thickness, y - thickness), 
                    (x + CARD_WIDTH + thickness, y + CARD_HEIGHT + thickness), 
                    BLUE, 
                    thickness)
        
class Tablero:
    # Función para cargar las imágenes
    def load_images(image_folder):
        images = []
        for filename in os.listdir(image_folder):
            img_path = os.path.join(image_folder, filename)
            img = cv2.imread(img_path)
            if img is not None:
                img = cv2.resize(img, (CARD_WIDTH, CARD_HEIGHT))
                images.append(img)
        return images

    # Función para centrar el tablero en la pantalla completa
    def center_board():
        margin_x = (FULL_SCREEN_WIDTH - BOARD_WIDTH) // 2
        margin_y = (FULL_SCREEN_HEIGHT - BOARD_HEIGHT) // 2
        return margin_x, margin_y

    # Función para crear el tablero con las cartas
    def create_board(rows, cols, images):
        num_pairs = (rows * cols) // 2
        if len(images) < num_pairs:
            print(f"Error: Necesitas al menos {num_pairs} imágenes diferentes.")
            exit()
        selected_images = random.sample(images, num_pairs)
        card_indices = list(range(num_pairs)) * 2
        random.shuffle(card_indices)
        return np.array(card_indices).reshape((rows, cols)), selected_images

    # Dibuja el tablero
    def draw_board(board, flipped, images, screen, back_image):
        margin_x, margin_y = Tablero.center_board()
        for i in range(ROWS):
            for j in range(COLS):
                x, y = margin_x + j * (CARD_WIDTH + CARD_SPACING), margin_y + i * (CARD_HEIGHT + CARD_SPACING)
                if flipped[i, j]:
                    screen[y:y + CARD_HEIGHT, x:x + CARD_WIDTH] = images[board[i, j]]
                else:
                    screen[y:y + CARD_HEIGHT, x:x + CARD_WIDTH] = back_image

        return screen

class Game:
    #Funcion para detectar el click
    @staticmethod
    def detect_click(x, y):
        # Calcular la columna en la que se ha hecho clic
        col = x // (CARD_WIDTH + CARD_SPACING)
        # Calcular la fila en la que se ha hecho clic
        row = y // (CARD_HEIGHT + CARD_SPACING)
        
        # Verificar que el clic esté dentro del tablero
        if col < COLS and row < ROWS:
            return int(row), int(col)
        else:
            return None  # Retorna None si el clic está fuera del área del tablero
    
    @staticmethod
    def run_game(difficulty):
        global first_card, second_card, pairs_found, flipped, selectable, board, screen
        global ROWS, COLS, BOARD_WIDTH, BOARD_HEIGHT  # Asegurar que se actualicen las variables globales
        
        # Obtener el número de filas y columnas para la dificultad seleccionada
        ROWS, COLS = DIFFICULTY_SETTINGS[difficulty]
        
        # Calcular las dimensiones del tablero basadas en el tamaño de las cartas y el espacio entre ellas
        BOARD_WIDTH = COLS * (CARD_WIDTH + CARD_SPACING) - CARD_SPACING
        BOARD_HEIGHT = ROWS * (CARD_HEIGHT + CARD_SPACING) - CARD_SPACING
        
        # Cargar la imagen de fondo
        background_image = cv2.imread('./imagenes/FondoTablero.jpg')
        background_image = cv2.resize(background_image, (FULL_SCREEN_WIDTH, FULL_SCREEN_HEIGHT))
        
        # Crear la pantalla usando el fondo
        screen = background_image.copy()
        
        # Cargar imágenes y crear el tablero
        image_folder = './imagenes/cartas'
        images = Tablero.load_images(image_folder)
        back_image = cv2.imread('./imagenes/CartaAtras.png')
        back_image = cv2.resize(back_image, (CARD_WIDTH, CARD_HEIGHT))
        
        board, selected_images = Tablero.create_board(ROWS, COLS, images)
        flipped = np.zeros((ROWS, COLS), dtype=bool)
        first_card, second_card = None, None
        pairs_found = 0
        selectable = True

        # Definir función de callback para el ratón
        def game_mouse_callback(event, x, y, flags, param):
            global selectable, first_card, second_card, selectable, pairs_found
            if event == cv2.EVENT_LBUTTONDOWN:
                if Botones.is_exit_button_clicked(x, y, exit_button_x, exit_button_y):
                    param['return_to_menu'] = True
                    return
                    
                if Botones.is_help_button_clicked(x, y, help_button_x, help_button_y):
                    margin_x, margin_y = Tablero.center_board()
                    card1, card2 = Botones.find_unmatched_pair(board, flipped)
                    
                    if card1 and card2:
                        Botones.highlight_card(screen, card1[0], card1[1], margin_x, margin_y)
                        Botones.highlight_card(screen, card2[0], card2[1], margin_x, margin_y)
                        cv2.imshow('Memory Game', screen)
                        cv2.waitKey(1500)
                    return

                margin_x, margin_y = Tablero.center_board()
                row, col = Game.detect_click(x - margin_x, y - margin_y)
                if row < ROWS and col < COLS and not flipped[row, col] and selectable:
                    card_image = images[board[row, col]]
                    Animaciones.flip_card(card_image, margin_x + col * (CARD_WIDTH + CARD_SPACING),
                            margin_y + row * (CARD_HEIGHT + CARD_SPACING), back_image)

                    flipped[row, col] = True
                    if first_card is None:
                        first_card = (row, col)
                    else:
                        second_card = (row, col)
                        selectable = False

                        card1 = board[first_card[0], first_card[1]]
                        card2 = board[second_card[0], second_card[1]]

                        if card1 == card2:
                            pairs_found += 1

                            Animaciones.draw_circle_on_card(margin_x + first_card[1] * (CARD_WIDTH + CARD_SPACING),
                                                margin_y + first_card[0] * (CARD_HEIGHT + CARD_SPACING))
                            Animaciones.draw_circle_on_card(margin_x + second_card[1] * (CARD_WIDTH + CARD_SPACING),
                                                margin_y + second_card[0] * (CARD_HEIGHT + CARD_SPACING))

                            first_card, second_card = None, None
                            selectable = True
                        else:
                            Animaciones.draw_cross_on_card(margin_x + first_card[1] * (CARD_WIDTH + CARD_SPACING),
                                            margin_y + first_card[0] * (CARD_HEIGHT + CARD_SPACING))
                            Animaciones.draw_cross_on_card(margin_x + second_card[1] * (CARD_WIDTH + CARD_SPACING),
                                            margin_y + second_card[0] * (CARD_HEIGHT + CARD_SPACING))

                            cv2.waitKey(1000)
                            Animaciones.flip_card(back_image, margin_x + col * (CARD_WIDTH + CARD_SPACING),
                                    margin_y + row * (CARD_HEIGHT + CARD_SPACING), back_image)
                            Animaciones.flip_card(back_image, margin_x + first_card[1] * (CARD_WIDTH + CARD_SPACING),
                                    margin_y + first_card[0] * (CARD_HEIGHT + CARD_SPACING), back_image)
                            flipped[first_card[0], first_card[1]] = False
                            flipped[second_card[0], second_card[1]] = False
                            first_card, second_card = None, None
                            selectable = True

        callback_params = {'return_to_menu': False}
        cv2.setMouseCallback('Memory Game', game_mouse_callback, callback_params)
        
        # Game loop
        while not callback_params['return_to_menu']:
            # Restablece el fondo antes de dibujar el tablero
            screen = background_image.copy()
            
            # Dibuja el tablero, el botón de salida y el botón de ayuda en la pantalla
            screen = Tablero.draw_board(board, flipped, images, screen, back_image)
            exit_button_x, exit_button_y = Botones.draw_exit_button(screen)
            help_button_x, help_button_y = Botones.draw_help_button(screen)
            cv2.imshow('Memory Game', screen)
            cv2.imshow('Memory Game', screen)

            if pairs_found == (ROWS * COLS) // 2:
                print("¡Has ganado!")
                # Cargar la imagen
                img = cv2.imread('./imagenes/Eliberio_fiesta.png')

                # Crear una ventana y configurarla en modo pantalla completa
                cv2.namedWindow('Victoria', cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty('Victoria', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

                # Mostrar la imagen
                cv2.imshow('Victoria', img)

                # Esperar a que se presione una tecla
                cv2.waitKey(0)
                
                # Cerrar solo la ventana de la imagen
                cv2.destroyWindow('Victoria')
                
                return True

            key = cv2.waitKey(30) & 0xFF
            if key == 27:  # ESC
                return True

        return True


def main():
    while True:
        # Mostrar menú y obtener selección
        selected_action = Menu.select_difficulty()
        
        # Si se selecciona salir, terminar el programa
        if selected_action == "EXIT":
            break
            
        # Si se selecciona una dificultad, iniciar el juego
        Game.run_game(selected_action)
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()