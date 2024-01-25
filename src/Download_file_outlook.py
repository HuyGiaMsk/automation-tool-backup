import os
import threading
import time
from datetime import datetime, timedelta
from logging import Logger

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from exchangelib import Credentials, Account
from observer.Event import Event
from src.observer.EventBroker import EventBroker
from src.observer.PercentChangedEvent import PercentChangedEvent

from src.Constants import ZIP_EXTENSION
from src.common.FileUtil import get_excel_data_in_column_start_at_row, extract_zip, \
    remove_all_in_folder
from src.common.ResourceLock import ResourceLock
from src.common.ThreadLocalLogger import get_current_logger

from enum import Enum

from src.task.AutomatedTask import AutomatedTask


# Define an enumeration class

class Download_file_outlook(AutomatedTask):
    def automate(self):
        pass

    def getCurrentPercent(self):
        pass

    def __init__(self, settings: dict[str, str]):
        super().__init__(settings)

    def mandatory_settings(self) -> list[str]:
        mandatory_keys: list[str] = ['username', 'password', 'download.folder', 'excel.path', 'excel.sheet',
                                    'excel.column.booking',
                                    'excel.column.so', 'excel.column.becode']
        return mandatory_keys

    def get_current_percent(self) -> float:
        return self.current_element_index * 100 / self.total_element_size

    def download_attachments_drr(self, account, outlook_folder_drr, download_folder_path_drr):

        logger: Logger = get_current_logger()
        folder = account.root / 'Top of Information Store' / outlook_folder_drr

        for item in folder.all().order_by('-datetime_received')[:20]:
            print(f"Đang xử lý email: {item.subject}")

            for attachment in item.attachments:

                if not attachment.name.lower().endswith('.pdf'):

                    download_path = os.path.join(download_folder_path_drr, attachment.name)
                    with open(download_path, 'wb') as f:
                        f.write(attachment.content)
                    print(f"Đã tải về: {attachment.name}")


    def download_attachments_cfs(self, account, outlook_folder_cfs, download_folder_path_cfs):

        logger: Logger = get_current_logger()

        email_address = self._settings['email']
        password = self._settings['password']

        outlook_folder_drr = self._settings['outlook.folder.drr']
        outlook_folder_cfs = self._settings['outlook.folder.cfs']

        download_folder_path_drr = self._settings['download.drr.folder']
        download_folder_path_cfs = self._settings['download.cfs.folder']

        credentials = Credentials(email_address, password)
        account = Account(email_address, credentials=credentials, autodiscover=True)

        folder_cfs = account.root / 'Top of Information Store' / outlook_folder_cfs
        folder_drr = account.root / 'Top of Information Store' / outlook_folder_drr

        for item in folder_cfs.all().order_by('-datetime_received')[:20]:
            print(f"Đang xử lý email: {item.subject}")

            for attachment in item.attachments:

                if not attachment.name.lower().endswith('.pdf'):
                    download_path = os.path.join(download_folder_path_cfs, attachment.name)
                    with open(download_path, 'wb') as f:
                        f.write(attachment.content)
                    print(f"Đã tải về: {attachment.name}")
                    logger.info('downloaded {}'.format(attachment.name))




