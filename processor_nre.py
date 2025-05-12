from report_generator import ExcelProcessor
import os
import datetime 
import time

def main():
    # input_file = "input_only_propertyname.xlsx"
    # input_file = "input.xlsx"
    current_time= datetime.datetime.now() 
    # formatted_datetime = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    formatted_datetime = ""
    input_file = "input.xlsx"
    template_file = "template.xlsx"
    output_file = f"output_nre{formatted_datetime}.xlsx"
    base_dir = "sheets/nre/"
    config_file = f"{base_dir}/Location.json"
    other_configs = [
    # 'LocationGroup.json',
    # 'LocationLegalEntity.json',
    # 'LocationArea.json',
    # 'LocationAreaHistory.json'
    ]

    for file in [input_file, template_file, config_file]:
        if not os.path.exists(file):
            print(f"Error: File '{file}' not found")
            return

    for file in other_configs:
        if not os.path.exists(f"{base_dir}{file}"): 
            print(f"Error: File '{file}' not found")
            return


    start_time=time.time()
    processor = ExcelProcessor(input_file, template_file, output_file, config_file, 3, 3)
    # processor.set_limit_rows(200)
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
