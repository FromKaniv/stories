# engine.py
import os
import yaml
import base64
from collections import deque

class StoryEngine:
    def __init__(self, story_dir="stories"):
        self.story_dir = story_dir
        self.story_data = None
        self.unlocked_endings = set()

    # Завантаження однієї історії
    def load_story(self, folder):
        story_path = os.path.join(self.story_dir, folder, "story.yaml")
        unlocked_path = os.path.join(self.story_dir, folder, "unlocked.dat")

        # Завантаження історії
        with open(story_path, "r", encoding="utf-8") as f:
            self.story_data = yaml.safe_load(f)

        # Завантаження розблокованих кінцівок
        self.unlocked_endings = set()
        if os.path.isfile(unlocked_path):
            with open(unlocked_path, "r", encoding="utf-8") as f:
                encoded = f.read()
                try:
                    decoded = base64.b64decode(encoded).decode("utf-8")
                    self.unlocked_endings = set(line.strip() for line in decoded.splitlines() if line.strip())
                except Exception:
                    pass

    # Зберегти розблоковані кінцівки
    def save_unlocked_endings(self, folder):
        unlocked_path = os.path.join(self.story_dir, folder, "unlocked.dat")
        encoded = base64.b64encode(
            "\n".join(self.unlocked_endings).encode("utf-8")
        ).decode("utf-8")
        with open(unlocked_path, "w", encoding="utf-8") as f:
            f.write(encoded)

    # Перевірка вузлів на існування
    def validate_story_nodes(self):
        nodes = self.story_data.get("story", {})
        endings = set(self.story_data.get("endings", {}).keys())

        invalid_nodes = []
        for node_id, node in nodes.items():
            for choice in node.get("choices", []):
                nxt = choice.get("next")
                if nxt not in nodes and nxt not in endings:
                    invalid_nodes.append(f"{node_id} -> {nxt}")
        return invalid_nodes

    # Обчислення мінімальної та максимальної довжини шляхів
    def compute_path_lengths(self):
        nodes = self.story_data.get("story", {})
        start = self.story_data.get("start")
        endings = set(self.story_data.get("endings", {}).keys())

        if not start or not nodes:
            return 0, 0

        queue = deque()
        queue.append((start, 0, set([start])))
        lengths = []

        while queue:
            node_id, depth, path_set = queue.popleft()

            if node_id in endings:
                lengths.append(depth)
                continue

            node = nodes.get(node_id)
            if not node:
                continue

            for choice in node.get("choices", []):
                nxt = choice.get("next")
                if nxt and nxt not in path_set:
                    new_path = set(path_set)
                    new_path.add(nxt)
                    queue.append((nxt, depth + 1, new_path))

        if lengths:
            return min(lengths), max(lengths)
        return 0, 0

    # Повернення списку кінцівок із назвами та описами
    def get_endings_info(self):
        endings = self.story_data.get("endings", {})
        result = {}
        for eid, desc in endings.items():
            if isinstance(desc, dict):
                name = desc.get("name", f"Кінець {eid}")
                text = desc.get("text", "")
            else:
                name = f"Кінець {eid}"
                text = desc
            result[eid] = {"name": name, "text": text}
        return result

    # Показати текст кінцівок, залежно від розблокованих
    def get_display_endings(self):
        info = self.get_endings_info()
        display = {}
        for eid, data in info.items():
            if eid in self.unlocked_endings:
                display[eid] = data
            else:
                display[eid] = {"name": "???", "text": "???"}
        return display

    # Розблокувати кінцівку (і одразу зберегти)
    def unlock_ending(self, folder, ending_id):
        self.unlocked_endings.add(ending_id)
        self.save_unlocked_endings(folder)
