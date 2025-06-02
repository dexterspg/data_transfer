import json
import os
from configs.config import INDICES_STORE_FILE


def save_document_to_json(sheet_name, df):
    output_file=f"src/documents/{sheet_name}.json"

    document = df[[ col for col in df.columns if col.endswith("Id")]]
    document["idx"] = df.index.tolist()

    document.to_json(output_file, orient="records", indent=4)

def save_document_indices(sheet_name, indices):
    data={}

    if os.path.exists(INDICES_STORE_FILE):
       with open(INDICES_STORE_FILE, "r") as f:
         data = json.load(f)

    data[sheet_name] = indices

    with open(INDICES_STORE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def retrieve_document_indices(sheet_name: str):
    """Retrieves indices for the given sheet_name from JSON file."""
    if not os.path.exists(INDICES_STORE_FILE):
        print("No data found!")
        return None

    # print(sheet_name)
    with open(INDICES_STORE_FILE, "r") as f:
        data = json.load(f)
    # print(data[sheet_name])

    return data.get(sheet_name, None)

def clear_document_indices():
    """Clears all saved indices by resetting the JSON file."""
    with open(INDICES_STORE_FILE, "w") as f:
        json.dump({}, f, indent=4)  # Reset file with an empty JSON object

    print("All stored document indices have been cleared.")


def clear_json_files_in_folder(folder_path: str):
    if not os.path.exists(folder_path):
        print("Folder does not exist:", folder_path)
        return
    
    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):  # Only process JSON files
            file_path = os.path.join(folder_path, filename)
            
            # Overwrite the JSON file with an empty dictionary
            with open(file_path, "w") as json_file:
                json.dump({}, json_file)
            
            print(f"Cleared {filename}")


