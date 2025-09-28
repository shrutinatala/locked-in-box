import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
import PIL.Image

# Load environment variables
load_dotenv()
api_key_gemini = os.getenv("GEMINI_API_KEY")
firebase_project_id = "locked-in-box"
firebase_api_key = "AIzaSyClE7hLUOvw2zni2Xv3D2jy2tsGfWnafm4"


# -------------------------------
# Extract name from ID card image
# -------------------------------
def extract_name_from_id(image_path: str) -> str | None:
    if not api_key_gemini:
        print("❌ GEMINI_API_KEY not set in .env")
        return None

    genai.configure(api_key=api_key_gemini)

    try:
        img = PIL.Image.open(image_path)
    except FileNotFoundError:
        print(f"❌ Error: Image '{image_path}' not found.")
        return None

    prompt = (
        "You are a strict extractor. "
        "From the ID card shown, extract ONLY the person's full legal name as printed. "
        "Do not include labels, extra words, or punctuation. "
        "If the name is split into 'Surname' and 'Given Name', combine them as 'GIVEN SURNAME'."
    )

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content([prompt, img])

    name = response.text.strip().replace("\n", " ")
    return name


# -------------------------------
# Get all current names at Table 1
# -------------------------------
def get_table1_names():
    url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents/tables/1/names?key={firebase_api_key}"
    res = requests.get(url)
    if res.status_code != 200:
        print(f"❌ Failed to fetch Table 1. Status code: {res.status_code}")
        return []

    data = res.json()
    documents = data.get("documents", [])
    names = []
    for doc in documents:
        fields = doc.get("fields", {})
        names.append({
            "id": doc["name"].split("/")[-1],  # document ID
            "name": fields.get("name", {}).get("stringValue", "")
        })
    return names


# -------------------------------
# Toggle name in Firestore (add if new, remove if duplicate)
# -------------------------------
def toggle_name_in_firestore(name: str):
    names = get_table1_names()
    existing = next((n for n in names if n["name"].lower() == name.lower()), None)

    if existing:
        # Remove the name (toggle off)
        doc_id = existing["id"]
        url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents/tables/1/names/{doc_id}?key={firebase_api_key}"
        res = requests.delete(url)
        if res.status_code == 200:
            print(f"🗑️ Removed '{name}' from Table 1 (toggle off)")
        else:
            print(f"❌ Failed to remove '{name}'. Status code: {res.status_code}")
            print(res.text)
    else:
        # Add new name if table is not full
        if len(names) >= 4:
            print("⚠️ Table 1 is full. Cannot add new names.")
            return

        url = f"https://firestore.googleapis.com/v1/projects/{firebase_project_id}/databases/(default)/documents/tables/1/names?key={firebase_api_key}"
        timestamp = datetime.utcnow().isoformat() + "Z"
        data = {
            "fields": {
                "name": {"stringValue": name},
                "timestamp": {"timestampValue": timestamp}
            }
        }
        res = requests.post(url, json=data)
        if res.status_code == 200:
            print(f"✅ Added '{name}' to Table 1 (toggle on)")
        else:
            print(f"❌ Failed to add '{name}'. Status code: {res.status_code}")
            print(res.text)


# -------------------------------
# Main
# -------------------------------
def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))  # folder where extract_name.py lives
    image_path = os.path.join(script_dir, "gwyneth.jpeg")  # absolute path

    print(f"📂 Looking for image at: {image_path}")  # debug print

    name = extract_name_from_id(image_path)

    if name:
        print("Extracted Name:", name)
        toggle_name_in_firestore(name)
    else:
        print("❌ Failed to extract name.")


if __name__ == "__main__":
    main()
