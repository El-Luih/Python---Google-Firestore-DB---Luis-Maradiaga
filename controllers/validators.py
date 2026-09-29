def required(label):
    #Returns a parser that rejects blank text and strips spaces.
    def check(text):
        text = text.strip()
        if not text:
            raise ValueError(f'{label} is required.')
        return text
    return check