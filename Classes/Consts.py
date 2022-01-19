from PyQt5.QtWidgets import QHeaderView

# ___________COLORS___________
NORMAL_LINE_COLOR = '#ffffff'
NORMAL_WINDOW_COLOR = '#f0f0f0'
ERROR_COLOR = '#ff5133'

# ___________SIZES____________
IMAGE_SIZE = (RIGHT_IMAGE_WIDTH, RIGHT_IMAGE_HEIGHT) = (280, 400)

FSW_FILMS_TABLE_COLS_SIZE = [80, 200, 100, 100, QHeaderView.Stretch, QHeaderView.Stretch,
                             QHeaderView.Stretch, QHeaderView.Stretch]
FSW_GENRES_TABLE_COLS_SIZE = [80, QHeaderView.Stretch]
FSW_DIRECTORS_TABLE_COLS_SIZE = [80, QHeaderView.Stretch, QHeaderView.Stretch]
FSW_SESSIONS_TABLE_COLS_SIZE = [80, QHeaderView.Stretch, QHeaderView.Stretch]

UW_FILMS_TABLE_COLS_SIZE = [250, 250, QHeaderView.Stretch, QHeaderView.Stretch]

# __________NUMBERS___________
UW_FILMS_TABLE_COLS_COUNT = 4

FSW_FILMS_TABLE_COLS_COUNT = 8
FSW_GENRES_TABLE_COLS_COUNT = 2
FSW_DIRECTORS_TABLE_COLS_COUNT = 3
FSW_SESSIONS_TABLE_COLS_COUNT = 3

# ___________TITLES___________
UW_FILMS_TABLE_TITLES = ["Называние", "Жанры", "Рейтинг", "Длительность"]

FSW_FILMS_TABLE_TITLES = ["film_id", "title", "country", "rating", "duration",
                          "file_folder_name", "description_file_name", "image_name"]
FSW_GENRES_TABLE_TITLES = ["genre_id", "genre_title"]
FSW_DIRECTORS_TABLE_TITLES = ["director_id", "name", "surname"]
FSW_SESSIONS_TABLE_TITLES = ["session_id", "date", "time"]
