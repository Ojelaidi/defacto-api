def extract_texts(data, texts=[]):
    if isinstance(data, dict):
        if "text" in data:
            texts.append(data["text"])
        for value in data.values():
            extract_texts(value, texts)
    elif isinstance(data, list):
        for item in data:
            extract_texts(item, texts)
    return texts
