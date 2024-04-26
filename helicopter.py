import os
import random
import json

class Shop:
    def __init__(self):
        self.upgrades = {
            'health': {'name': 'Увеличение жизней', 'cost': 10},
            'capacity': {'name': 'Увеличение вместимости воды', 'cost': 10}
        }

    def display_upgrades(self):
        print("Магазин улучшений:")
        for i, (key, value) in enumerate(self.upgrades.items(), 1):
            print(f"{i}. {value['name']} - Стоимость: {value['cost']} очков")

class Helicopter:
    def __init__(self, x, y, map_width, map_height, water_capacity, max_lives, points):
        self.x = x
        self.y = y
        self.map_width = map_width
        self.map_height = map_height
        self.water_capacity = water_capacity
        self.current_water = 0
        self.max_lives = max_lives
        self.lives = max_lives
        self.points = points
        self.turns_since_last_fire = 0  # Счетчик ходов с момента последнего пожара

    def move(self, direction):
        self.turns_since_last_fire += 1
        if direction == 'w':
            self.y = max(0, self.y - 1)
        elif direction == 's':
            self.y = min(self.map_height - 1, self.y + 1)
        elif direction == 'a':
            self.x = max(0, self.x - 1)
        elif direction == 'd':
            self.x = min(self.map_width - 1, self.x + 1)

    def fill_water(self):
            self.current_water = self.water_capacity
            print(f"Вертолет наполнился водой. Текущий запас воды: {self.current_water}/{self.water_capacity}")

    def lose_life(self):
        self.lives -= 1
        print(f"Вертолет потерял жизнь. Осталось жизней: {self.lives}/{self.max_lives}")

    def restore_lives(self):
        self.lives = self.max_lives
        print(f"Жизни вертолета восстановлены до максимального значения: {self.max_lives}/{self.max_lives}")

    def random_teleport(self):
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        dx, dy = random.choice(directions)
        new_x = max(0, min(self.map_width - 1, self.x + dx))
        new_y = max(0, min(self.map_height - 1, self.y + dy))
        self.x = new_x
        self.y = new_y

    def buy_upgrade(self, upgrade, shop):
        if upgrade.isdigit():  # Проверяем, является ли введенное значение цифрой
            upgrade_index = int(upgrade) - 1  # Преобразуем введенную цифру в индекс списка улучшений
            if 0 <= upgrade_index < len(shop.upgrades):  # Проверяем, что индекс находится в допустимых пределах
                upgrade_key = list(shop.upgrades.keys())[upgrade_index]  # Получаем ключ улучшения по индексу
                upgrade_info = shop.upgrades[upgrade_key]
                if self.points >= upgrade_info['cost']:
                    if upgrade_key == 'health':
                        self.max_lives += 1
                        print("Вы улучшили жизни вертолета.")
                    elif upgrade_key == 'capacity':
                        self.water_capacity += 1
                        print("Вы увеличили вместимость вертолета для воды.")
                    self.points -= upgrade_info['cost']
                else:
                    print("Недостаточно очков для покупки этого улучшения.")
            else:
                print("Улучшение с таким номером не найдено.")
        else:
            print("Некорректный выбор улучшения. Введите номер улучшения.")

    def extinguish_fire(self, game_map):
        if game_map.board[self.y][self.x] == '🔥':
            if self.current_water > 0:
                game_map.board[self.y][self.x] = '🌲'
                self.points += 10
                game_map.fire_counter -= 1
                self.current_water -= 1
                self.turns_since_last_fire = 0
                print("Пожар потушен.")
            else:
                print("Недостаточно воды для тушения пожара.")

class Map:
    def __init__(self, width, height, num_trees, num_rivers):
        self.width = width
        self.height = height
        self.board = [['🟩' for _ in range(self.width)] for _ in range(self.height)]
        self.fire_counter = 0
        self.burn_timers = {}  # Словарь для отслеживания времени горения деревьев
        self.helicopter = Helicopter(self.width // 2, self.height // 2, self.width, self.height, water_capacity=1, max_lives=3, points=0)
        self.shop = Shop()
        self.turns = 0  # Счетчик ходов
        self.generate_trees(num_trees)
        self.generate_rivers(num_rivers)
        self.generate_storm()
        self.generate_clouds()
        self.generate_shop()
        self.generate_hospitals()

    def generate_fires(self, num_fires):
        for _ in range(num_fires):
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if self.board[y][x] == '🌲':
                    self.board[y][x] = '🔥'
                    self.burn_timers[(y, x)] = 0  # Начинаем отсчет горения для каждого нового пожара
                    break

    def start_fires(self):
        self.turns += 1  # Счетчик ходов
        if self.turns % 5 == 0:
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if self.board[y][x] == '🌲':
                    self.board[y][x] = '🔥'  # Новое дерево загорается
                    self.burn_timers[(y, x)] = 0  # Начинаем отсчет
                    break
        if random.random() < 0.25:
            while True:
                x = random.randint(0, self.width - 1)
                y = random.randint(0, self.height - 1)
                if self.board[y][x] == '🟩':  # Убедитесь, что здесь нет других объектов
                    self.board[y][x] = '🌲'  # Добавляем новое дерево
                    break        

    def draw(self):
        print(f"Вертолет: Вода - {self.helicopter.current_water}/{self.helicopter.water_capacity}, Жизни - {self.helicopter.lives}/{self.helicopter.max_lives}, Очки - {self.helicopter.points}")
        for y in range(self.height):
            for x in range(self.width):
                if x == self.helicopter.x and y == self.helicopter.y:
                    print('🚁', end=' ')
                else:
                    print(self.board[y][x], end=' ')
            print()

    def check_water_source(self):
        if self.board[self.helicopter.y][self.helicopter.x] == '🌊':
            return True
        else:
            return False

    def check_clouds(self):
        if self.board[self.helicopter.y][self.helicopter.x] == '☁️':
            return True
        else:
            return False

    def check_shop(self):
        if self.board[self.helicopter.y][self.helicopter.x] == '🛒':
            return True
        else:
            return False
        
    def check_hospital(self):
        if self.board[self.helicopter.y][self.helicopter.x] == '🏥':
            return True
        else:
            return False
        
        
    def check_storm(self):
        if self.board[self.helicopter.y][self.helicopter.x] == '⛈️':
            return True
        else:
            return False
        
    def check_fire(self):
        if self.board[self.helicopter.y][self.helicopter.x] == '⛈️':
            return True
        else:
            return False   
    def generate_trees(self, num_trees):
        for _ in range(num_trees):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.board[y][x] = '🌲'

    def generate_rivers(self, num_rivers):
        for _ in range(num_rivers):
            x = random.randint(0, self.width - 1)
            y = random.randint(0, self.height - 1)
            self.board[y][x] = '🌊'

    def generate_storm(self):
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < 0.05:
                    self.board[y][x] = '⛈️'

    def generate_clouds(self):
        for y in range(self.height):
            for x in range(self.width):
                if random.random() < 0.1:
                    self.board[y][x] = '☁️'

    def generate_shop(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        self.board[y][x] = '🛒'

    def generate_hospitals(self):
        x = random.randint(0, self.width - 1)
        y = random.randint(0, self.height - 1)
        self.board[y][x] = '🏥'

    def check_fire(self):
        if self.board[self.helicopter.y][self.helicopter.x] == '🔥':
            return True
        else:
            return False

    def check_burnt_trees(self):
        trees_to_remove = []
        for (y, x), burn_turns in self.burn_timers.items():
            self.burn_timers[(y, x)] += 1  # Увеличиваем время горения
            if burn_turns >= 10:
                self.board[y][x] = '⬜'  # Дерево сгорело
                self.helicopter.points -= 10  # Штраф за сгоревшее дерево
                trees_to_remove.append((y, x))
        for tree in trees_to_remove:
            del self.burn_timers[tree]  # Удаляем из словаря

    def available_actions(self):
        if self.check_water_source():
            return " F - Набрать воду"
        elif self.check_shop():
            return " F - Залеть в магазин"
        elif self.check_hospital():
            return " F - Залеть в больницу"
        elif self.check_fire():
            return " F - Потушить пожар"
        else:
            return ""
def clear_screen():
    if os.name == 'nt':  # Если ОС Windows
        os.system('cls')
    else:  # Если другие ОС (Linux, MacOS, Unix)
        os.system('clear')
def save_game(game_map, filename="game_save.json"):
    # Собираем данные для сохранения
    save_data = {
        "helicopter": {
            "x": game_map.helicopter.x,
            "y": game_map.helicopter.y,
            "water_capacity": game_map.helicopter.water_capacity,
            "current_water": game_map.helicopter.current_water,
            "lives": game_map.helicopter.lives,
            "points": game_map.helicopter.points,
        },
        "turns": game_map.turns,
        "fire_counter": game_map.fire_counter,
        "burn_timers": [
            {"y": k[0], "x": k[1], "burn_turns": v} for k, v in game_map.burn_timers.items()
        ],
        "board": [{"y": y, "x": x, "symbol": game_map.board[y][x]} for y in range(game_map.height) for x in range(game_map.width)],  # Записываем каждую координату
    }

    # Запись данных в файл JSON
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(save_data, f, ensure_ascii=False, indent=4)  # Сохраняем с форматированием
    
    print("Игра сохранена!")
def load_game(filename="game_save.json"):
    if not os.path.exists(filename):
        print("Файл сохранения не найден.")
        return None

    with open(filename, 'r', encoding='utf-8') as f:
        save_data = json.load(f)

    # Восстанавливаем размеры карты
    board_data = save_data["board"]
    map_width = max(item["x"] for item in board_data) + 1
    map_height = max(item["y"] for item in board_data) + 1

    # Создаем объект карты с нужными размерами
    game_map = Map(map_width, map_height, 0, 0)

    # Восстанавливаем доску по координатам
    game_map.board = [['🟩' for _ in range(map_width)] for _ in range(map_height)]
    for item in board_data:
        y = item["y"]
        x = item["x"]
        game_map.board[y][x] = item["symbol"]

    # Восстанавливаем данные о вертолете
    helicopter_data = save_data["helicopter"]
    game_map.helicopter.x = helicopter_data["x"]
    game_map.helicopter.y = helicopter_data["y"]
    game_map.helicopter.water_capacity = helicopter_data["water_capacity"]
    game_map.helicopter.current_water = helicopter_data["current_water"]
    game_map.helicopter.lives = helicopter_data["lives"]
    game_map.helicopter.points = helicopter_data["points"]
    game_map.turns = save_data["turns"]
    game_map.fire_counter = save_data["fire_counter"]

    # Восстановление времени горения деревьев
    burn_timers = {}
    for item in save_data["burn_timers"]:
        y = item["y"]
        x = item["x"]
        burn_timers[(y, x)] = item["burn_turns"]

    game_map.burn_timers = burn_timers  # Восстанавливаем словарь времени горения
    
    print("Игра загружена!")
    return game_map

def main():
    game_map = None
    
    while game_map is None:
        command = input("Нажмите 'r' для загрузки игры или любую другую клавишу для начала новой игры: ").lower()
        if command == 'r':
            game_map = load_game()  # Пытаемся загрузить игру
        else:
            # Если загрузка не удалась, создаем новую игру
            width = int(input("Введите ширину карты: "))
            height = int(input("Введите высоту карты: "))
            num_trees = int(input("Введите количество деревьев: "))
            num_rivers = int(input("Введите количество рек: "))
            game_map = Map(width, height, num_trees, num_rivers)
    
    game_running = True  # Флаг, указывающий, идет ли игра

    while game_running:
        clear_screen()  # Очищаем экран перед обновлением карты
        game_map.draw()  # Отображаем карту после очистки

        # Проверка завершения игры
        if game_map.helicopter.lives <= 0:
            print("Game Over! Вертолет потерял все жизни.")
            game_running = False  # Завершаем игровой цикл
            break

        prompt = game_map.available_actions()
        command = input(f"Введите команду (WASD для перемещения {prompt} или 'q' для сохранения игры): ").lower()

        if command in ['w', 'a', 's', 'd']:
            game_map.helicopter.move(command)
            if game_map.check_clouds():
                game_map.helicopter.random_teleport()
                print("Вертолет перемещен из-за облаков.")
            elif game_map.check_storm():
                game_map.helicopter.lose_life()  # Потеря жизни при шторме
            game_map.check_burnt_trees()  # Проверяем сгоревшие деревья
            game_map.start_fires()  # Создаем новые пожары
        
        elif command == 'f':
            if game_map.check_water_source():
                game_map.helicopter.fill_water()
            elif game_map.check_shop():
                game_map.shop.display_upgrades()
                upgrade_choice = input("Введите улучшение для покупки: ").lower()
                game_map.helicopter.buy_upgrade(upgrade_choice, game_map.shop)
            elif game_map.check_hospital():
                game_map.helicopter.restore_lives()
            elif game_map.check_fire():
                game_map.helicopter.extinguish_fire(game_map)
        elif command == 'q':  # Сохранение игры
            save_game(game_map)  # Сохраняем текущее состояние
        elif command == 'r':  # Загрузка игры
            game_map = load_game()  # Загружаем последнее сохраненное состояние
        else:
            print("Некорректная команда!")

if __name__ == "__main__":
    main()           