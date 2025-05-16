from report_generator import ExcelProcessor
import os
import datetime 
import time

def is_file_open(file_path):
    """Checks if a file is open by another process."""
    if not os.path.exists(file_path):
        return False  # File doesn't exist, so it's not open

    try:
        with open(file_path, 'a'):  # Try opening in append mode
            return False  # Successfully opened, file is not locked
    except IOError:
        return True  # File is locked/open by another process

def main() -> None:
    # input_file = "input_only_propertyname.xlsx"
    # input_file = "input.xlsx"
    current_time= datetime.datetime.now() 
    formatted_datetime = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    input_file = "input_prolease_398.xlsx"
    # input_file = "input_200rows.xlsx"
    template_file = "template_init_accounting_on_complete.xlsx"
    # output_file = f"output_nre{formatted_datetime}.xlsx"
    output_file = f"output_nre.xlsx"
    base_dir = "src/sheets/nre/"
    config_file = f"{base_dir}/Location.json"
    other_configs = [
    'LocationGroup.json',
    'LocationLegalEntity.json',
    'LocationArea.json',
    'LocationAreaHistory.json',
    'LocationToPartner.json',
    'LocationToPartnerContact.json',
    'Premise.json',
    'PremiseArea.json',
    'Lease.json',
    'Terms.json',
    'TermAmounts.json'
    ]

    for file in [input_file, template_file, config_file]:
        if not os.path.exists(file):
            print(f"Error: File '{file}' not found")
            return

    for file in other_configs:
        if not os.path.exists(f"{base_dir}{file}"): 
            print(f"Error: File '{file}' not found")
            return

     # ✅ Check if output file is open
    if is_file_open(output_file):
        print(f" Error: '{output_file}' is currently open. Close it before running the script.")
        return

    start_time=time.time()
    processor = ExcelProcessor(input_file, template_file, output_file, config_file, 3, 3)
    processor.set_limit_rows(100)
    # processor.set_number_of_last_rows_to_drop(1)
    processor.process()

    for config in other_configs:
        print(config)
        processor._load_config(f"{base_dir}{config}")
        processor.process()
    processor._save_workbook()
    duration = time.time() - start_time
    print(f"Duration: {duration}")


if __name__ == "__main__":
        main()
