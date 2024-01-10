import os
import pdfplumber

from pdfplumber import PDF
from logging import Logger
from src.Constants import ROOT_DIR
from src.common import ExcelReaderProvider
from src.common.FileUtil import load_key_value_from_file_properties
from src.common.XlwingProvider import XlwingProvider
from src.task.AutomatedTask import AutomatedTask
from src.common.ThreadLocalLogger import get_current_logger


class PDFRead(AutomatedTask):

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

        for root, dirs, files in os.walk(path_to_docs):

            for current_pdf in files:
                if not current_pdf.lower().endswith(".pdf"):
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

        # @staticmethod
        # def delete_and_create_new_sheet(work_book: Workbook, sheet_name: str, path_to_excel: str) -> None:
        #     if sheet_name in work_book.sheetnames:
        #         sheet_to_delete = work_book[sheet_name]
        #         work_book.remove(sheet_to_delete)
        #
        #     work_book.create_sheet(sheet_name)
        #     work_book.save(path_to_excel)

if __name__ == '__main__':
    invoked_class = 'PDFRead'
    setting_file = os.path.join(ROOT_DIR, 'input', '{}.properties'.format(invoked_class))
    settings: dict[str, str] = load_key_value_from_file_properties(setting_file)
    settings['invoked_class'] = invoked_class
    task: AutomatedTask = PDFRead(settings)
    task.perform()
