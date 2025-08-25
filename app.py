import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QListWidget, QStackedWidget, QMessageBox, QDialog,
    QDialogButtonBox, QCheckBox, QScrollArea
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from engine import StoryEngine

class StoryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Історії")
        self.stories_dir = "stories"
        self.engine = StoryEngine(self.stories_dir)

        self.stories = sorted([f for f in os.listdir(self.stories_dir)
                               if os.path.isdir(os.path.join(self.stories_dir, f))])
        self.current_story_folder = None

        self.stack = QStackedWidget()
        self.init_main_menu()
        self.init_story_selection()
        self.init_story_info()
        self.init_game_screen()
        self.init_settings_page()

        layout = QVBoxLayout()
        layout.addWidget(self.stack)
        self.setLayout(layout)

        self.setMinimumSize(600, 300)
        self.stack.setCurrentIndex(0)
        self.resize(self.stack.currentWidget().sizeHint())

    # ----------------- Головне меню -----------------
    def init_main_menu(self):
        page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Ласкаво просимо!")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(title)

        layout.addStretch()

        play_button = QPushButton("Грати")
        play_button.clicked.connect(lambda: self.show_page(1))
        layout.addWidget(play_button)

        settings_button = QPushButton("Налаштування")
        settings_button.clicked.connect(lambda: self.show_page(4))
        layout.addWidget(settings_button)

        exit_button = QPushButton("Вийти")
        exit_button.clicked.connect(self.close)
        layout.addWidget(exit_button)

        page.setLayout(layout)
        self.stack.addWidget(page)

    # ----------------- Вибір історії -----------------
    def init_story_selection(self):
        page = QWidget()
        layout = QVBoxLayout()

        self.selection_title = QLabel("Оберіть історію")
        self.selection_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.selection_title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(self.selection_title)

        self.story_list = QListWidget()
        for folder in self.stories:
            self.engine.load_story(folder)
            self.story_list.addItem(self.engine.story_data.get("title", folder))
        layout.addWidget(self.story_list)

        select_button = QPushButton("Обрати")
        select_button.clicked.connect(self.select_story)
        layout.addWidget(select_button)

        back_button = QPushButton("Назад")
        back_button.clicked.connect(lambda: self.show_page(0))
        layout.addWidget(back_button)

        page.setLayout(layout)
        self.stack.addWidget(page)

    # ----------------- Сторінка інформації про історію -----------------
    def init_story_info(self):
        page = QWidget()
        self.story_info_layout = QVBoxLayout()

        self.story_title = QLabel("")
        self.story_title.setFont(QFont("Arial", 14, QFont.Bold))
        self.story_title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.story_info_layout.addWidget(self.story_title)

        self.story_stats = QLabel("")
        self.story_stats.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.story_info_layout.addWidget(self.story_stats)

        self.endings_list_widget = QListWidget()
        self.story_info_layout.addWidget(self.endings_list_widget)

        self.start_button = QPushButton("Почати")
        self.start_button.clicked.connect(self.start_game)
        self.back_button_info = QPushButton("Назад")
        self.back_button_info.clicked.connect(lambda: self.show_page(1))

        self.story_info_layout.addWidget(self.start_button)
        self.story_info_layout.addWidget(self.back_button_info)

        page.setLayout(self.story_info_layout)
        self.stack.addWidget(page)

    # ----------------- Сторінка гри -----------------
    def init_game_screen(self):
        page = QWidget()
        self.game_layout = QVBoxLayout()

        self.text_label = QLabel("")
        self.text_label.setWordWrap(True)
        self.text_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.game_layout.addWidget(self.text_label)

        self.buttons_layout = QVBoxLayout()
        self.game_layout.addLayout(self.buttons_layout)

        page.setLayout(self.game_layout)
        self.stack.addWidget(page)

    # ----------------- Сторінка налаштувань -----------------
    def init_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Налаштування")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(title)

        # Кнопка стерти дані — одразу під заголовком
        clear_button = QPushButton("Стерти дані гравця")
        clear_button.clicked.connect(self.show_clear_dialog)
        layout.addWidget(clear_button)

        layout.addStretch()

        ok_button = QPushButton("Гаразд")
        ok_button.clicked.connect(lambda: self.show_page(0))
        layout.addWidget(ok_button)

        page.setLayout(layout)
        self.stack.addWidget(page)

    # ----------------- Перехід між сторінками -----------------
    def show_page(self, index):
        self.stack.setCurrentIndex(index)
        self.resize(self.stack.currentWidget().sizeHint())

    # ----------------- Вибір історії -----------------
    def select_story(self):
        selected = self.story_list.currentRow()
        if selected == -1:
            return

        folder = self.stories[selected]
        self.engine.load_story(folder)
        self.current_story_folder = folder

        # Перевірка на помилки
        invalid_nodes = self.engine.validate_story_nodes()
        if invalid_nodes:
            msg = QMessageBox(self)
            msg.setWindowTitle("Помилка")
            msg.setText(f"Історія «{self.engine.story_data.get('title', folder)}» має помилку в дереві шляхів.\n"
                        f"Список помилкових шляхів:\n" + "\n".join(invalid_nodes))
            msg.setIcon(QMessageBox.Warning)
            msg.exec_()
            return

        self.story_title.setText(self.engine.story_data.get("title", folder))

        # Оновлення списку кінцівок та статистики
        self.update_endings_list()
        self.start_button.setEnabled(True)
        self.show_page(2)

    def update_endings_list(self):
        self.endings_list_widget.clear()
        endings_info = self.engine.get_endings_info()
        total = len(endings_info)
        unlocked_count = 0

        for i, eid in enumerate(endings_info.keys(), start=1):
            if eid in self.engine.unlocked_endings:
                name = endings_info[eid]["name"]
                unlocked_count += 1
            else:
                name = "???"
            self.endings_list_widget.addItem(f"№{i}. {name}")

        self.story_stats.setText(f"{unlocked_count} із {total} кінців розблоковано в цій історії")

    # ----------------- Почати гру -----------------
    def start_game(self):
        self.nodes = self.engine.story_data.get("story", {})
        self.endings_info = self.engine.get_display_endings()
        self.show_node(self.engine.story_data.get("start"))
        self.show_page(3)

    # ----------------- Показ вузла -----------------
    def show_node(self, node_id):
        for i in reversed(range(self.buttons_layout.count())):
            w = self.buttons_layout.itemAt(i).widget()
            if w:
                w.setParent(None)

        all_endings = self.engine.get_endings_info()
        if node_id in all_endings:
            if node_id not in self.engine.unlocked_endings:
                self.engine.unlock_ending(self.current_story_folder, node_id)
            self.update_endings_list()

            data = self.engine.get_display_endings()[node_id]
            idx = list(self.engine.get_endings_info().keys()).index(node_id) + 1

            self.text_label.setText(f"<b>КІНЕЦЬ №{idx}. {data['name']}</b>\n\n{data['text']}")

            play_again = QPushButton("Грати знову")
            play_again.clicked.connect(lambda: self.show_page(2))
            main_menu = QPushButton("Домівка")
            main_menu.clicked.connect(lambda: self.show_page(0))
            self.buttons_layout.addWidget(play_again)
            self.buttons_layout.addWidget(main_menu)

            self.resize(self.stack.currentWidget().sizeHint())
            return

        node = self.nodes.get(node_id)
        if not node:
            self.text_label.setText("Помилка: вузол не знайдено.")
            return

        self.text_label.setText(node.get("text", ""))
        for choice in node.get("choices", []):
            btn = QPushButton(choice.get("text", ""))
            btn.clicked.connect(lambda _, nxt=choice.get("next"): self.show_node(nxt))
            self.buttons_layout.addWidget(btn)

        self.resize(self.stack.currentWidget().sizeHint())

    # ----------------- Діалог для очищення даних -----------------
    def show_clear_dialog(self):
        selected_titles = []
        dialog = QDialog(self)
        dialog.setWindowTitle("Стерти дані")
        layout = QVBoxLayout(dialog)

        label = QLabel("Будь ласка, оберіть історії, дані яких мають бути стерті:")
        layout.addWidget(label)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        vbox = QVBoxLayout(container)
        self.checkboxes = []

        for folder in self.stories:
            self.engine.load_story(folder)
            title = self.engine.story_data.get("title", folder)
            cb = QCheckBox(title)
            cb.folder_name = folder
            vbox.addWidget(cb)
            self.checkboxes.append(cb)

        container.setLayout(vbox)
        scroll.setWidget(container)
        layout.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Cancel | QDialogButtonBox.Ok)
        buttons.button(QDialogButtonBox.Ok).setText("Стерти")
        buttons.button(QDialogButtonBox.Cancel).setText("Скасувати")
        buttons.accepted.connect(lambda: self.confirm_clear(dialog))
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        dialog.exec_()

    def confirm_clear(self, dialog):
        selected = [cb for cb in self.checkboxes if cb.isChecked()]
        if not selected:
            dialog.reject()
            return

        titles = [cb.text() for cb in selected]
        confirm = QMessageBox.question(
            self, "Підтвердження",
            f"Ви дійсно бажаєте стерти дані гравця таких історій: {', '.join(titles)}?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            for cb in selected:
                unlocked_path = os.path.join(self.stories_dir, cb.folder_name, "unlocked.dat")
                if os.path.isfile(unlocked_path):
                    os.remove(unlocked_path)
            QMessageBox.information(self, "Готово", "Дані гравця з певних історій видалено успішно.")
            dialog.accept()
        else:
            dialog.reject()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StoryApp()
    window.show()
    sys.exit(app.exec_())
