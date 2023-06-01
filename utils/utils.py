# converts cyrillic month to int
def month_to_int(month_string):
    months = {
        "јан": 1,
        "феб": 2,
        "мар": 3,
        "апр": 4,
        "мај": 5,
        "јун": 6,
        "јул": 7,
        "авг": 8,
        "сеп": 9,
        "окт": 10,
        "нов": 11,
        "дец": 12,
    }
    return months[month_string]
