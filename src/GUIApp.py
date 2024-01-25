import importlib
import os
import threading
import tkinter as tk
import tkinter.filedialog
from logging import Logger
from tkinter import *  # Label, Frame, Text, Widget, ttk
from tkinter import ttk, Text
from tkinter.ttk import Combobox
from types import ModuleType

from observer.EventBroker import EventBroker
from observer.EventHandler import EventHandler
from observer.PercentChangedEvent import PercentChangedEvent
from src.Constants import ROOT_DIR
from src.common.FileUtil import load_key_value_from_file_properties
from src.common.ResourceLock import ResourceLock
from src.common.ThreadLocalLogger import get_current_logger, setup_textbox_logger
from src.task.AutomatedTask import AutomatedTask


class GUIApp(tk.Tk, EventHandler):

    def __init__(self):
        super().__init__()

        self.protocol("WM_DELETE_WINDOW", self.handle_close_app)
        EventBroker.get_instance().register(topic=PercentChangedEvent.event_name,
                                            observer=self)

        self.geometry('1920x1080')
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
        self.automated_tasks_dropdown.bind("<<ComboboxSelected>>", self.on_selection_change)

        self.content_frame = ttk.Frame(self.container_frame, width=900, height=500, relief=tk.SOLID,
                                       style='Rounded.TFrame')
        self.content_frame.pack(padx=5, pady=5)

        self.populate_dropdown()

        self.current_input_setting_values = {}
        self.current_automated_task_name = None

        self.progressbar = ttk.Progressbar(self.container_frame, orient=HORIZONTAL, length=500, mode="determinate",
                                           maximum=100)
        self.progressbar.pack(pady=20)

        textbox: Text = tk.Text(self.container_frame, wrap="word", state=tk.DISABLED, width=40, height=10)
        textbox.pack()
        setup_textbox_logger(textbox)

    def handle_close_app(self):
        self.persist_settings_to_file()
        self.destroy()

    def handle_incoming_event(self, event: Event) -> None:
        self.logger.info("Receive the event")
        if isinstance(event, PercentChangedEvent):
            self.logger.info("Update the percent bar")
            self.progressbar['value'] = event.current_percent

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
        selected_task: str = self.automated_tasks_dropdown.get()
        if selected_task is not None:
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

    def create_setting_widgets(self, setting_frame, each_setting, index, input_setting_values: dict[str, str]):
        field_label = Label(master=setting_frame, text=each_setting, width=20, wraplength=150)
        field_label.special_id = each_setting
        field_label.grid(row=index, column=0, sticky='ew', padx=3, pady=3)

        field_input = Text(master=setting_frame, width=30, height=1)
        field_input.grid(row=index, column=1, sticky='ew', padx=3, pady=3)
        field_input.special_id = each_setting
        initial_value: str = input_setting_values.get(each_setting)
        field_input.insert("1.0", '' if initial_value is None else initial_value)
        field_input.bind("<KeyRelease>", self.update_field_data)

        path_button_text = "..." if ".path" in each_setting or '.folder' in each_setting else ""

        if path_button_text:
            path_button = tk.Button(master=setting_frame, text=path_button_text)
            path_button.special_id = each_setting
            path_button.grid(row=index, column=2, sticky='ew', padx=3, pady=3)
            path_button.bind('<Button-1>',
                             self.update_file_data if ".path" in each_setting else self.update_folder_data)

    def perform_task(self, automated_task: AutomatedTask):
        task_thread = threading.Thread(target=automated_task.perform, daemon=False)
        task_thread.start()

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
        logger.info("Persist config data completely")

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


if __name__ == "__main__":
    app = GUIApp()
    app.mainloop()
