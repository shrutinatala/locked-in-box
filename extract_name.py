import argparse
import google.generativeai as genai
import PIL.Image
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")


def extract_name_from_id():
    # Configure Gemini API
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    # image_path = "C:/Users/grish/OneDrive/Desktop/GitHub/breaktomake/usc-card-2-1.png"
    image_path = "C:/Users/grish/OneDrive/Desktop/GitHub/breaktomake/charlotte_chang.jpg"
    # Load image
    try:
        img = PIL.Image.open(image_path)
    except FileNotFoundError:
        print(f"Error: Image '{image_path}' not found.")
        return None

    # Prompt Gemini
    prompt = (
        "You are a strict extractor. "
        "From the ID card shown, extract ONLY the person's full legal name as printed. "
        "Do not include labels, extra words, or punctuation. "
        "If the name is split into 'Surname' and 'Given Name', combine them as 'GIVEN SURNAME'."
    )

    # Send request
    # model = genai.GenerativeModel("gemini-1.5-pro")
    model = genai.GenerativeModel("gemini-2.5-flash")
    # model = genai.GenerativeModel("gemini-pro-vision")
    response = model.generate_content([prompt, img])

    # Clean response
    name = response.text.strip()
    name = name.replace("\n", " ")

    return name

def main():
    # parser = argparse.ArgumentParser(description="Extract person's name from an ID card using Gemini Vision.")
    # parser.add_argument("--image", type=str, required=True, help="Path to the ID image file")
    # parser.add_argument("--api_key", type=str, required=True, help="Your Google Gemini API key")

    # args = parser.parse_args()

    result = extract_name_from_id()
    # result = extract_name_from_id(args.image, args.api_key)

    if result:
        print("\n✅ Extracted Name:", result)
    else:
        print("\n❌ Failed to extract name.")

if __name__ == "__main__":
    main()
