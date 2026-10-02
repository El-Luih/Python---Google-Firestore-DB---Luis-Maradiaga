# Keeps the CLI consistent.
# Rejects empty input before saving data.


# Returns a validator that requires a non-empty field value.
def required(label):
    def check(text):
        text = text.strip()
        if not text:
            raise ValueError(f'{label} is required.')
        return text
    return check