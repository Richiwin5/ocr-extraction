import re

def extract_fields(text):

    data = {}

    name = re.search(r'NAME[: ]+(.*)', text, re.I)
    dob = re.search(r'(\d{2}/\d{2}/\d{4})', text)

    if name:
        data["full_name"] = name.group(1)

    if dob:
        data["date_of_birth"] = dob.group(1)

    return data