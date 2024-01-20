import threading
import tkinter as tk
from tkinter import *  # Label, Frame, Text, Widget, ttk
from tkinter import ttk
from tkinter.ttk import Combobox
import os
import importlib
from logging import Logger
from types import ModuleType
import tkinter.filedialog

from src.task.AutomatedTask import AutomatedTask
from src.Constants import ROOT_DIR
from src.common.FileUtil import load_key_value_from_file_properties
from src.common.ResourceLock import ResourceLock
from src.common.ThreadLocalLogger import get_current_logger


class GUIApp(tk.Tk):

    def __init__(self):
        super().__init__()

        self.geometry('900x500')
        self.logger: Logger = get_current_logger()

        style_conner = ttk.Style()
        style_conner.theme_use('clam')
        style_conner.configure('Rounded.TFrame', corner_radius=20, backround='#ffffff')
        style_conner.configure('Rounded.TLabel', corner_radius=20, backround='#ffffff')
        style_conner.configure('Rounded.TCombobox', corner_radius=20, backround='#ffffff')

        self.container_frame = ttk.Frame(self, style='Rounded.TFrame')
        self.container_frame.pack()

        self.myLabel = ttk.Label(self.container_frame,
                                 text='Automation Tool',
                                 font=('Maersk Headline Bold', 16),
                                 foreground='#0073AB',
                                 style='Rounded.TLabel')
        self.myLabel.pack()

        self.automated_tasks_dropdown = Combobox(master=self.container_frame, state="readonly")
        self.automated_tasks_dropdown.pack()

        self.content_frame = ttk.Frame(self.container_frame, width=900, height=500, relief=tk.SOLID,
                                       style='Rounded.TFrame')
        self.content_frame.pack(padx=5, pady=5)

        self.automated_tasks_dropdown.bind("<<ComboboxSelected>>", self.on_selection_change)

        self.populate_dropdown()

        self.current_input_setting_values = {}
        self.current_automated_task_name = None

        def step_procssingbar():
            self.progressbar['value'] += 100
            self.myLabel.config(text=self.progressbar['value'])
            task_thread = threading.Thread(target=self.perform_task)
            task_thread.start()

        self.progressbar = ttk.Progressbar(self, orient=HORIZONTAL, length=500 ,mode="determinate", maximum=100, )
        self.progressbar.pack(pady=20)
        my_button = Button(self, text='process', command=step_procssingbar)
        my_button.pack(pady=20)

    def populate_dropdown(self):
        input_dir: str = os.path.join(ROOT_DIR, "input")
        automated_task_names: list[str] = []

        with ResourceLock(file_path=input_dir):
            for dir_name in os.listdir(input_dir):
                if dir_name.lower().endswith(".properties"):
                    automated_task_names.append(dir_name.replace(".properties", ""))

        automated_task_names.remove("InvokedClasses")
        self.automated_tasks_dropdown['values'] = automated_task_names

    def on_selection_change(self, event):
        self.persist_settings_to_file()
        selected_task = self.automated_tasks_dropdown.get()
        self.update_frame_content(selected_task)


    def update_frame_content(self, selected_task):
        # Clear the content frame
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Create new content based on the selected task
        self.logger.info('Display fields for task {}'.format(selected_task))

        clazz_module: ModuleType = importlib.import_module('src.' + selected_task)
        clazz = getattr(clazz_module, selected_task)

        setting_file = os.path.join(ROOT_DIR, 'input', '{}.properties'.format(selected_task))
        input_setting_values: dict[str, str] = load_key_value_from_file_properties(setting_file)
        input_setting_values['invoked_class'] = selected_task
        input_setting_values['use.GUI'] = 'True' if input_setting_values.get(
            'use.GUI') is None else input_setting_values.get('use.GUI')
        input_setting_values['time.unit.factor'] = '1' if input_setting_values.get(
            'time.unit.factor') is None else input_setting_values.get('time.unit.factor')

        self.current_input_setting_values = input_setting_values
        self.current_automated_task_name = selected_task

        automated_task: AutomatedTask = clazz(input_setting_values)
        mandatory_settings: list[str] = automated_task.mandatory_settings()
        mandatory_settings.append('use.GUI')
        mandatory_settings.append('time.unit.factor')

        index = 0

        for each_setting in mandatory_settings:
            # Create a container frame for each label and text input pair
            setting_frame = Frame(self.content_frame)
            setting_frame.pack(anchor="w", pady=5)
            self.create_setting_widgets(setting_frame, each_setting, index, input_setting_values)
            index += 1


        perform_button = tk.Button(self.content_frame, text='Perform', bg='#42B0D5', font=('Maersk Headline Bold', 10),
                                   activebackground='#0073AB', fg='#F7F7F7', activeforeground='#F7F7F7',
                                   command=lambda: self.perform_task(automated_task))
        perform_button.pack()

        # self.task = selected_task
        # self.cancel_button = ttk.Button(self.content_frame, text="Cancel", command=self.cancel_task)
        # self.cancel_button.pack()
        # self.cancel_flag = threading.Event()

    def create_setting_widgets(self, setting_frame, each_setting, index, input_setting_values):
        field_label = Label(master=setting_frame, text=each_setting, width=20, wraplength=150)
        field_label.special_id = each_setting
        field_label.grid(row=index, column=0, sticky='ew', padx=3, pady=3)

        field_input = Text(master=setting_frame, width=30, height=1)
        field_input.grid(row=index, column=1, sticky='ew', padx=3, pady=3)
        field_input.special_id = each_setting
        field_input.insert("1.0", input_setting_values[each_setting])
        field_input.bind("<KeyRelease>", self.update_field_data)

        path_button_text = "..." if ".path" in each_setting or '.folder' in each_setting else ""

        if path_button_text:
            path_button = tk.Button(master=setting_frame, text=path_button_text)
            path_button.special_id = each_setting
            path_button.grid(row=index, column=2, sticky='ew', padx=3, pady=3)
            path_button.bind('<Button-1>',
                             self.update_file_data if ".path" in each_setting else self.update_folder_data)

    def perform_task(self, AutomatedTask):

        task_thread = threading.Thread(target=AutomatedTask.perform, daemon=False)
        task_thread.start()
        # task.perform()

    def find_children_by_id(self, parent: tk.Widget, special_id: str):
        childs: list[Widget] = parent.winfo_children()
        for widget in childs:
            if widget.special_id is special_id and isinstance(widget, tk.Text):
                return widget
        return None

    def update_file_data(self, event):
        logger: Logger = get_current_logger()
        new_dir_value: str = tkinter.filedialog.askopenfilename()

        dir_button_widget: tk.Widget = event.widget
        field_name = dir_button_widget.special_id

        parent_widget_id = dir_button_widget.winfo_parent()
        parent_widget: Widget = dir_button_widget._nametowidget(parent_widget_id)
        field_input = self.find_children_by_id(parent_widget, field_name)
        if new_dir_value:
            field_input.config(highlightbackground="green")
            field_input.delete("1.0", "end")  # Clear existing text
            field_input.insert("1.0", new_dir_value)  # Insert selected path
            self.current_input_setting_values[field_name] = new_dir_value
        else:
            field_input.config(highlightbackground="red")

        logger.info("Change data on field {} to {}".format(field_name, new_dir_value))

    def update_folder_data(self, event):
        logger: Logger = get_current_logger()
        new_dir_value: str = tkinter.filedialog.askdirectory()  # Use askdirectory for selecting folders
        dir_button_widget: tk.Widget = event.widget
        field_name = dir_button_widget.special_id

        parent_widget_id = dir_button_widget.winfo_parent()
        parent_widget: Widget = dir_button_widget._nametowidget(parent_widget_id)
        field_input = self.find_children_by_id(parent_widget, field_name)
        if new_dir_value:
            field_input.config(highlightbackground="green")
            field_input.delete("1.0", "end")  # Clear existing text
            field_input.insert("1.0", new_dir_value)  # Insert selected path
            self.current_input_setting_values[field_name] = new_dir_value
        else:
            field_input.config(highlightbackground="red")

        logger.info("Change data on field {} to {}".format(field_name, new_dir_value))

    def update_field_data(self, event):
        logger: Logger = get_current_logger()
        text_widget: tk.Widget = event.widget
        new_value = text_widget.get("1.0", "end-1c")
        field_name = text_widget.special_id
        self.current_input_setting_values[field_name] = new_value
        logger.info("Change data on field {} to {}".format(field_name, new_value))

    def persist_settings_to_file(self):
        if self.current_automated_task_name is None:
            return

        logger: Logger = get_current_logger()
        file_path: str = os.path.join(ROOT_DIR, "input", "{}.properties".format(self.current_automated_task_name))
        logger.info("Try to persist data to {}".format(file_path))

        with ResourceLock(file_path=file_path):

            with open(file_path, 'w') as file:
                file.truncate(0)

            with open(file_path, 'a') as file:
                for key, value in self.current_input_setting_values.items():
                    file.write(f"{key} = {value}\n")

    def toggle_theme(self, container_frame):
        global is_dark_mode
        is_dark_mode = not is_dark_mode

        if is_dark_mode:
            app.configure(background='black')  # dark theme
            self.container_frame = ttk.Frame(self, style='Dark.Rounded.TFrame', )
            self.container_frame.pack()
        else:
            app.configure(background='white')  # light theme
            container_frame.configure(style='Rounded.TFrame', background='black')

    # def cancel_task(self):
    #     self.task.cancel()

if __name__ == "__main__":
    app = GUIApp()
    app.mainloop()
