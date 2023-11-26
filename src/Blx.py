import os
import threading
import time
from datetime import datetime, timedelta
from logging import Logger

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from src.AutomatedTask import AutomatedTask
from src.Constants import ZIP_EXTENSION
from src.FileUtil import get_excel_data_in_column_start_at_row, extract_zip, \
    check_parent_folder_contain_all_required_sub_folders, remove_all_in_folder
from src.ResourceLock import ResourceLock
from src.StringUtil import join_set_of_elements
from src.ThreadLocalLogger import get_current_logger

from enum import Enum


# Define an enumeration class
class BookingToInfoIndex(Enum):
    SO_INDEX_IN_TUPLE = 0
    BECODE_INDEX_IN_TUPLE = 1


class Blx(AutomatedTask):
    booking_to_info = {}

    def __init__(self, settings: dict[str, str]):
        super().__init__(settings)

    def mandatory_settings(self) -> set[str]:
        mandatory_keys: set[str] = {'username', 'password', 'excel.path', 'excel.sheet',
                                    'excel.read_column.start_cell.bill', 'download.path',}
        return mandatory_keys

    def automate(self) -> None:
        logger: Logger = get_current_logger()
        logger.info(
            "---------------------------------------------------------------------------------------------------------")
        logger.info("Start processing")

        self._driver.get('https://apll.get-traction.com/')

        logger.info('Try to login')
        self.__login()
        logger.info("Login successfully")
        logger.info("Navigate to overview page the first time")


        bills: list[str] = get_excel_data_in_column_start_at_row(self._settings['excel.path'],
                                                                       self._settings['excel.sheet'],
                                                                       self._settings[
                                                                           'excel.read_column.start_cell.bill'])

        # becodes: list[str] = get_excel_data_in_column_start_at_row(self._settings['excel.path'],
        #                                                            self._settings['excel.sheet'],
        #                                                            self._settings[
        #                                                                'excel.read_column.start_cell.becode'])
        #
        # so_numbers: list[str] = get_excel_data_in_column_start_at_row(self._settings['excel.path'],
        #                                                               self._settings['excel.sheet'],
        #                                                               self._settings['excel.read_column.start_cell.so'])
        if len(bills) == 0:
            logger.error('Input booking id list is empty ! Please check again')

        # if len(bills) != len(becodes) or len(booking_ids) != len(becodes):
        #     raise Exception("Please check your input data length of becode, sonumber and booking are not equal")


        # # info means becode and so number
        # index: int = 0
        # for bill in bills:
        #     self.booking_to_info[booking] = (so_numbers[index], becodes[index])
        #     index += 1

        last_booking: str = ''
        for bill in bills:
            logger.info("Processing bill : " + bill)
            self.__navigate_and_download(bill)
            last_booking = bill

        self._driver.close()
        logger.info(
            "---------------------------------------------------------------------------------------------------------")
        logger.info("End processing")
        logger.info("Summary info about list of successful and unsuccessful attempts to download each "
                    "booking's documents during the program")

        # Display summary info to the user
        self.__check_up_all_downloads(set(bills))

        # Pause and wait for the user to press Enter
        logger.info("It ends at {}. Press any key to end program...".format(datetime.now()))

    def __login(self) -> None:
        username: str = self._settings['username']
        password: str = self._settings['password']

        self._type_when_element_present(by=By.ID, value='username', content=username)
        self._type_when_element_present(by=By.ID, value='password', content=password)
        self._click_and_wait_navigate_to_other_page(by=By.CSS_SELECTOR, value='input[type=button]')

    def __check_up_all_downloads(self, booking_ids: set[str]) -> None:
        logger: Logger = get_current_logger()
        time.sleep(10 * self._timingFactor)
        is_all_contained, successful_bookings, unsuccessful_bookings = check_parent_folder_contain_all_required_sub_folders(
            parent_folder=self._download_folder, required_sub_folders=booking_ids)

        logger.info('{} successful booking folders containing documents has been download'
                    .format(len(successful_bookings)))
        successful_bookings = join_set_of_elements(successful_bookings, " ")
        logger.info(successful_bookings)

        if not is_all_contained:
            logger.error('{} fail attempts for downloading documents in all these bookings'
                         .format(len(unsuccessful_bookings)))
            successful_bookings = join_set_of_elements(unsuccessful_bookings, " ")
            logger.info(successful_bookings)

    def __navigate_and_download(self, bill: str) -> None:
        logger: Logger = get_current_logger()
        search_box: WebElement = self._type_when_element_present(by=By.CSS_SELECTOR,
                                                                 value='div.fm.fm-html input[type=text]',
                                                                 content=bill)

        # click detail booking
        self._click_when_element_present(by=By.CSS_SELECTOR, value='div.content.clear button[type=button]')
        # click tab document
        self._click_when_element_present(by=By.CSS_SELECTOR, value='div.entry h3.ti a')
        time.sleep(1)

        full_file_path: str = os.path.join(self._download_folder, bill + ZIP_EXTENSION)
        self._wait_download_file_complete(full_file_path)
        extract_zip_task = threading.Thread(target=extract_zip,
                                            args=(full_file_path, self._download_folder,
                                                  self.delete_redundant_opening_pdf_files,
                                                  None),
                                            daemon=False)

        extract_zip_task.start()
        # click to back to the overview Booking page
        self._click_and_wait_navigate_to_other_page(by=By.CSS_SELECTOR,
                                                    value='#loc li.loc-place a.gwt-InlineHyperlink')
        logger.info("Navigating back to overview page")

    @staticmethod
    def delete_redundant_opening_pdf_files(download_folder: str) -> None:
        # aim to perform in root folder which is actually the defined download folder
        remove_all_in_folder(folder_path=download_folder,
                             only_files=True,
                             file_extension="pdf",
                             elapsed_time=timedelta(minutes=2))