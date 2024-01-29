import os
import threading

import pdfplumber

from pdfplumber import PDF
from logging import Logger
from src.Constants import ROOT_DIR
from src.common import ExcelReaderProvider
from src.common.FileUtil import load_key_value_from_file_properties
from src.common.XlwingProvider import XlwingProvider
from src.task.AutomatedTask import AutomatedTask
from src.common.ThreadLocalLogger import get_current_logger
from src.common.Pywin32Provider import Pywin32Provider

class PDFRead(AutomatedTask):
    def getCurrentPercent(self):
        pass

    def get_current_percent(self) -> float:
        pass

    def __init__(self, settings: dict[str, str]):
        super().__init__(settings)

    def mandatory_settings(self) -> list[str]:
        mandatory_keys: list[str] = ['excel.path', 'excel.sheet', 'folder_docs.folder']
        return mandatory_keys

    def automate(self):

        logger: Logger = get_current_logger()

        excel_reader: ExcelReaderProvider = XlwingProvider()

        path_to_excel_contain_pdfs_content = self._settings['excel.path']
        workbook = excel_reader.get_workbook(path=path_to_excel_contain_pdfs_content)
        logger.info('Loading excel files')

        sheet_name: str = self._settings['excel.sheet']
        worksheet = excel_reader.get_worksheet(workbook, sheet_name)

        # worksheet.delete_contents(worksheet=worksheet, start_cell='A1', end_cell='AZ200')

        path_to_docs = self._settings['folder_docs.folder']
        pdf_counter: int = 1

        # only apply for ticket LOWE
        ic_file_name: str = "_IC_"
        ld_file_name: str = "_LD_"
        fcr_file_name: str = "_FCR_"
        ipt_file_name: str = "_IPT_"
        fc_file_name: str = "_FC_"

        for root, dirs, files in os.walk(path_to_docs):

            for current_pdf in files:

                if not current_pdf.lower().endswith(".pdf"):
                    continue

                if ic_file_name in current_pdf:
                    continue
                if ld_file_name in current_pdf:
                    continue
                if fcr_file_name in current_pdf:
                    continue
                if ipt_file_name in current_pdf:
                    continue
                if fc_file_name in current_pdf:
                    continue

                pdf: PDF = pdfplumber.open(os.path.join(root, current_pdf))
                logger.info("File name : {} PDF counter  = {}".format(current_pdf, pdf_counter))
                excel_reader.change_value_at(worksheet=worksheet, row=1, column=pdf_counter, value=current_pdf)

                current_page_in_current_pdf = 2
                for number, pageText in enumerate(pdf.pages):
                    raw_text = pageText.extract_text()
                    clean_text = raw_text.replace("\x00", "").replace("=", "")

                    # print( "text at page {} : {}".format(current_page_in_current_pdf, clean_text))
                    for line in clean_text.splitlines():
                        excel_reader.change_value_at(worksheet=worksheet, row=current_page_in_current_pdf,
                                                     column=pdf_counter, value=line)
                        current_page_in_current_pdf += 1

                excel_reader.save(workbook=workbook)

                pdf_counter += 1
        excel_reader.close(workbook=workbook)

