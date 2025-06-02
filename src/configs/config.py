import os
import datetime
from openpyxl.styles import NamedStyle, Font

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, "..")
current_time= datetime.datetime.now() 
formatted_datetime = current_time.strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_FILE = os.path.join(SRC_DIR, "..", "output_nre.xlsx")
OUTPUT_FILE_TIMED = os.path.join(SRC_DIR, "..", f"output_nre{formatted_datetime}.xlsx")


NRE_DIR= os.path.join(BASE_DIR, "nre")
NRE_SHEETS_DIR= os.path.join(NRE_DIR, "sheets" )
TEMPLATE_FILE = os.path.join(NRE_DIR, "templates", "template_init_accounting_on_complete.xlsx")
PREFIX_FILE = os.path.join(NRE_DIR, "ids", "prefix.json")

ENTITIES_PATH =  os.path.join(SRC_DIR, "store", "ids")
RELATIONSHIP_PATH =  os.path.join(SRC_DIR, "store")

# STORE_FILE = "src/store/document_indices.json"
INDICES_STORE_FILE= os.path.join(SRC_DIR, "store", "document_indices.json")
# for directory in [LOGS_DIR, ASSETS_DIR]:
    # if not os.path.isdir(directory):
        # os.makedirs(directory)

DATE_STYLE = NamedStyle("date_style")
DATE_STYLE.number_format = "DD/MM/YYYY"

MANDATORY_FONT_STYLE= Font(color="00FF9B9B")



