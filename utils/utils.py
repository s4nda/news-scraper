#converts cyrillic month to int
def month_to_int(month_string):
    months = {
        "Јан": 1,
        "Феб": 2,
        "Мар": 3,
        "Апр": 4,
        "Мај": 5,
        "Јун": 6,
        "Јул": 7,
        "Авг": 8,
        "Сеп": 9,
        "Окт": 10,
        "Нов": 11,
        "Дец": 12,
    }
    return months[month_string]
