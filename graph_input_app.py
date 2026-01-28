import tkinter as tk
from tkinter import ttk, colorchooser, filedialog
from graph import GraphRenderer
from loguru import logger
import json


class GraphInputApp(tk.Tk):
    """
    Основное окно приложения для создания диаграмм Graphviz.
    """

    def __init__(self):
        """
        Инициализирует главное окно приложения.
        """
        super().__init__()
        self.title("Graphviz Diagram Creator")
        self.geometry("470x600")
        self.graph = GraphRenderer()
        self.create_widgets()

    def create_widgets(self) -> None:
        """
        Создает основные виджеты интерфейса приложения.
        """
        try:
            # Метка и поле ввода для имени узла
            self.node_name_label = tk.Label(self, text="Название узла:")
            self.node_name_label.grid(row=0, column=0, padx=5, pady=5)
            self.node_name_entry = self.create_entry()
            self.node_name_entry.grid(row=0, column=1, padx=5, pady=5)

            # Метка и выпадающее меню для выбора типа узла
            self.node_type_label = tk.Label(self, text="Тип узла:")
            self.node_type_label.grid(row=1, column=0, padx=5, pady=5)
            self.node_type_var = tk.StringVar(value="Прямоугольник")
            self.node_type_menu = ttk.Combobox(self, textvariable=self.node_type_var)
            self.node_type_menu['values'] = list(self.graph.node_shapes.keys())
            self.node_type_menu.grid(row=1, column=1, padx=5, pady=5)

            # Кнопка для выбора цвета узла
            self.node_color_button = tk.Button(self, text="Выбрать цвет узла", command=self.choose_color)
            self.node_color_button.grid(row=2, column=1, padx=5, pady=5)
            self.node_color = "#000000"  # Цвет по умолчанию

            # Кнопка для добавления узла
            self.add_node_button = tk.Button(self, text="Добавить узел", command=self.insert_node)
            self.add_node_button.grid(row=3, column=1, padx=5, pady=5)

            # Вызов функции для создания виджетов для связей
            self.create_edge_widgets()

            # Поле для отображения списка узлов и связей
            self.info_display = tk.Text(self, height=10, width=50)
            self.info_display.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

            # Кнопки для сохранения и загрузки графа
            self.save_button = tk.Button(self, text="Сохранить граф", command=self.save_graph)
            self.save_button.grid(row=11, column=0, padx=5, pady=5)
            self.load_button = tk.Button(self, text="Загрузить граф", command=self.load_graph)
            self.load_button.grid(row=11, column=1, padx=5, pady=5)

            # Кнопка для отображения графа
            self.show_graph_button = tk.Button(self, text="Показать граф", command=self.graph.render_graph)
            self.show_graph_button.grid(row=12, column=1, padx=5, pady=10)

            # Кнопка для удаления последнего узла
            self.delete_node_button = tk.Button(self, text="Удалить последний узел", command=self.delete_last_node)
            self.delete_node_button.grid(row=13, column=1, padx=5, pady=10)


        except Exception as e:
            logger.exception("Ошибка при создании виджетов")
            self.graph.show_error("Ошибка", f"Ошибка при создании интерфейса: {e}")

    def create_edge_widgets(self) -> None:
        """
        Создает виджеты для управления связями между узлами.
        """
        try:
            # Метка и выпадающее меню для выбора начального узла
            self.edge_from_label = tk.Label(self, text="Из узла:")
            self.edge_from_label.grid(row=4, column=0, padx=5, pady=5)
            self.edge_from_menu = ttk.Combobox(self)
            self.edge_from_menu.grid(row=4, column=1, padx=5, pady=5)

            # Метка и выпадающее меню для выбора конечного узла
            self.edge_to_label = tk.Label(self, text="В узел:")
            self.edge_to_label.grid(row=5, column=0, padx=5, pady=5)
            self.edge_to_menu = ttk.Combobox(self)
            self.edge_to_menu.grid(row=5, column=1, padx=5, pady=5)

            # Поле для запроса на добавление метки перехода
            self.edge_label_question = tk.Label(self, text="Добавить метку перехода?")
            self.edge_label_question.grid(row=6, column=0, padx=5, pady=5)

            # Переключатели для добавления или исключения метки
            self.edge_label_var = tk.StringVar(value="нет")
            self.yes_button = tk.Radiobutton(self, text="Да", variable=self.edge_label_var, value="да")
            self.yes_button.grid(row=6, column=1, padx=5, pady=5, sticky="w")
            self.no_button = tk.Radiobutton(self, text="Нет", variable=self.edge_label_var, value="нет")
            self.no_button.grid(row=6, column=1, padx=5, pady=5)

            # Поле ввода для метки, отображается только если выбран вариант "Да"
            self.edge_label_entry = self.create_entry()
            self.edge_label_entry.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

            # Кнопка добавления связи
            self.add_edge_button = tk.Button(self, text="Добавить связь", command=self.insert_edge)
            self.add_edge_button.grid(row=8, column=0, padx=5, pady=5)

        except Exception as e:
            logger.exception("Ошибка при создании полей для связей")
            self.graph.show_error("Ошибка", f"Ошибка при создании полей для связей: {e}")

    def create_entry(self):
        """
        Создает виджет ввода текста (Entry) с обработчиком для вставки текста.
        """
        entry = tk.Entry(self)
        entry.bind("<Control-v>", self.paste_text)
        return entry

    def paste_text(self, event):
        """
        Обработчик вставки текста из буфера обмена.
        """
        entry = event.widget
        try:
            entry.delete(0, tk.END)
            entry.insert(0, self.clipboard_get())
        except tk.TclError as e:
            logger.error("Ошибка вставки текста из буфера обмена")
            self.graph.show_error("Ошибка вставки", f"Не удалось вставить текст: {e}")

    def insert_edge(self):
        """
        Обработчик для добавления связи (ребра) между узлами графа.
        """
        try:
            edge_from = self.edge_from_menu.get()
            edge_to = self.edge_to_menu.get()
            edge_label = self.edge_label_entry.get()

            if edge_label == "" and self.edge_label_var.get() == "да":
                self.graph.show_error("Ошибка", "Если выбрано 'Да', необходимо ввести метку.")
                return

            self.graph.add_edge(edge_from, edge_to, label=edge_label)
            self.update_display()
        except Exception as e:
            logger.exception("Ошибка при добавлении связи")
            self.graph.show_error("Ошибка", f"Ошибка при добавлении связи: {e}")

    def insert_node(self):
        """
        Обработчик для добавления нового узла в граф.
        """
        try:
            node_name = self.node_name_entry.get()
            node_type = self.node_type_var.get()

            if node_name == "":
                self.graph.show_error("Ошибка", "Введите название узла.")
                return

            self.graph.add_node(node_name, node_type, color=self.node_color)
            self.update_display()
            self.update_edge_menus()

            # Очистка поля ввода после добавления узла
            self.node_name_entry.delete(0, tk.END)

        except Exception as e:
            logger.exception("Ошибка при добавлении узла")
            self.graph.show_error("Ошибка", f"Ошибка при добавлении узла: {e}")

    def delete_last_node(self):
        """
        Обработчик для удаления последнего добавленного узла в графе.
        """
        try:
            self.graph.delete_last_node()  # Вызов функции удаления узла
            self.update_display()  # Обновление отображения
            self.update_edge_menus()  # Обновление меню выбора узлов
        except Exception as e:
            logger.exception("Ошибка при удалении узла")
            self.graph.show_error("Ошибка", f"Ошибка при удалении узла: {e}")

    def choose_color(self):
        """
        Открывает окно выбора цвета и устанавливает выбранный цвет для узлов.
        """
        color = colorchooser.askcolor(title="Выберите цвет узла")[1]
        if color:
            self.node_color = color

    def save_graph(self):
        """
        Сохраняет текущий граф в JSON-файл.
        """
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "w") as f:
                json.dump(self.graph.to_dict(), f)
            logger.info("Граф сохранен в файл")

    def load_graph(self):
        """
        Загружает граф из JSON-файла.
        """
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            with open(file_path, "r") as f:
                data = json.load(f)
                self.graph.from_dict(data)
            self.update_display()
            self.update_edge_menus()
            logger.info("Граф загружен из файла")

    def update_display(self):
        """
        Обновляет текстовое поле для отображения текущего состояния графа.
        """
        self.info_display.delete(1.0, tk.END)  # Очищаем текстовое поле

        # Получаем только последние логи о добавлении узлов и связей
        relevant_logs = [log for log in self.graph.graph_logs if "добавлен" in log or "связь добавлена" in log]

        # Вставляем текст в текстовое поле
        if relevant_logs:
            self.info_display.insert(tk.END, "\n".join(relevant_logs))
        else:
            self.info_display.insert(tk.END, "Нет добавленных узлов или связей.")

    def update_edge_menus(self):
        """
        Обновляет выпадающие списки для выбора узлов в графе.
        """
        nodes = list(self.graph.nodes)
        self.edge_from_menu['values'] = nodes
        self.edge_to_menu['values'] = nodes


if __name__ == "__main__":
    app = GraphInputApp()
    app.mainloop()
