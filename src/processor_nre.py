from configs.config import *
from report_generator import ExcelProcessor
import os
import time
from create_documents import clear_document_indices, clear_json_files_in_folder

def is_file_open(file_path):
    if not os.path.exists(file_path):
        return False  # File doesn't exist, so it's not open
    try:
        with open(file_path, 'a'):  # Try opening in append mode
            return False  # Successfully opened, file is not locked
    except IOError:
        return True  # File is locked/open by another process

def main() -> None:
    input_file = "input_prolease_398.xlsx"
    format=".json"
    config_file = f"{NRE_SHEETS_DIR}/Location{format}"
    other_configs = [
    # 'LocationGroup',
    # 'LocationLegalEntity',
    # 'LocationArea',
    # 'LocationAreaHistory',
    # 'LocationToPartner',
    # 'LocationToPartnerContact',
    'Premise',
    # 'PremiseArea',
    'Lease',
    # 'Terms',
    # 'TermAmounts',
    # 'TermVendor'
    ]
    sheet_names = ["Location"]
    sheet_names += other_configs

    for file in [input_file, TEMPLATE_FILE, config_file]:
        if not os.path.exists(file):
            print(f"Error: File '{file}{format}' not found")
            return

    for file in other_configs:
        if not os.path.exists(f"{NRE_SHEETS_DIR}/{file}{format}"): 
            print(f"Error: File '{file}{format}' not found")
            return

     # ✅ Check if output file is open
    if is_file_open(OUTPUT_FILE):
        print(f" Error: '{OUTPUT_FILE}' is currently open. Close it before running the script.")
        return

    start_time=time.time()
    clear_document_indices()
    clear_json_files_in_folder(ENTITIES_PATH)
    clear_json_files_in_folder(RELATIONSHIP_PATH)
    data_row_start =None 
    processor = ExcelProcessor(input_file=input_file, template_file=TEMPLATE_FILE, output_file=OUTPUT_FILE, config_file=config_file, template_header_row=3, input_header_row=3, data_row_start=data_row_start)
    # processor.set_limit_rows(50)
    processor.set_limit_rows(200)
    # processor.set_number_of_last_rows_to_drop(1)
    processor.process()

    for config in other_configs:
        print(config)
        processor._load_config(f"{NRE_SHEETS_DIR}/{config}{format}")
        processor.process()
    processor._delete_work_sheet_not_in_list(sheet_names)
    processor._save_workbook()
    duration = time.time() - start_time
    print(f"Duration: {duration}")


if __name__ == "__main__":
        main()
