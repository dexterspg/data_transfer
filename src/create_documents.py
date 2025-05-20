import json
import os

STORE_FILE = "src/store/document_indices.json"

def save_document_to_json(sheet_name, df):
    output_file=f"src/documents/{sheet_name}.json"

    document = df[[ col for col in df.columns if col.endswith("Id")]]
    document["idx"] = df.index.tolist()

    document.to_json(output_file, orient="records", indent=4)

def save_document_indices(sheet_name, indices):
    data={}

    if os.path.exists(STORE_FILE):
       with open(STORE_FILE, "r") as f:
         data = json.load(f)

    data[sheet_name] = indices

    with open(STORE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def retrieve_document_indices(sheet_name: str):
    """Retrieves indices for the given sheet_name from JSON file."""
    if not os.path.exists(STORE_FILE):
        print("No data found!")
        return None

    print(sheet_name)
    with open(STORE_FILE, "r") as f:
        data = json.load(f)
    print(data[sheet_name])

    return data.get(sheet_name, None)

def clear_document_indices():
    """Clears all saved indices by resetting the JSON file."""
    with open(STORE_FILE, "w") as f:
        json.dump({}, f, indent=4)  # Reset file with an empty JSON object

    print("All stored document indices have been cleared.")
