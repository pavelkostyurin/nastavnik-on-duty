import os
from slack_bolt import App
from dotenv import load_dotenv
import datetime as dt
import pandas as pd

load_dotenv()

TOKEN = os.getenv('SLACK_BOT_TOKEN')
SIGNING_SECRET = os.getenv('SIGNING_SECRET')
SHEET_ID = os.getenv('SCHEDULE_SHEET_ID')
NASTAVNIK_ON_DUTY_COMMAND = '/nastavnik-on-duty'
NUMBERS_ROW = 'Unnamed: 1'
NAMES_ROW = 'Unnamed: 2'
DUTY_MARKER = '1'
DATES_ROW = 5
MENTORS: dict = {}

app = App(token=TOKEN, signing_secret=SIGNING_SECRET)


@app.command(NASTAVNIK_ON_DUTY_COMMAND)
def post_to_slack(ack, say, command):
    ack()
    today = current_date()
    say(nastavnik(today))


def get_nastavnik_rows():
    """Вычисляет число наставников и сохраняет номера
    соответствующих строк."""
    num = 0
    rows = []
    mentors_numbers = df.get(NUMBERS_ROW)
    for i in range(len(mentors_numbers)):
        cur_val = mentors_numbers[i]
        if str(cur_val).isdigit():
            cur_number = int(cur_val)
            if cur_number > num:
                rows.append(i)
                num = cur_number

    print('Найдено наставников: ', len(rows))

    return rows


def current_date():
    """Возвращает сегодняшнюю дату в формате float (day.month).
    Это нужно для поиска даты в формате расписания дежурств."""
    return float(f'{dt.date.today().day}.{dt.date.today().month}')


def nastavnik(today):
    """Возвращает имя дежурного наставника. Ну или ничего не возвращает."""
    # Строка с датами
    dates = df.iloc[DATES_ROW]

    for i in range(len(dates)):
        cur_date = dates[i]

        # Точка в ячейке даты - маркер её валидности.
        # На все прочие не смотрим.
        if '.' not in str(cur_date):
            continue

        # Отсекаем день недели
        cur_date = str(cur_date).split(' ')[0]

        # Будем сравнивать в формате float, чтобы корректно сравнивать
        # даты с ведущим нулём (05.10 == 5.10)
        if float(cur_date) == today:
            # Ищем заветную единичку в колонке с датой
            for row in rows:
                if str(df.iat[row, i]) == DUTY_MARKER:
                    # Дежурный нашёлся
                    return MENTORS[row]

    # Праздник, выходной, или даты такой нет - никто не дежурит
    return None


if __name__ == "__main__":
    # Файл длинный, увеличим число колонок, которые сохраним в CSV
    pd.options.display.max_columns = 999

    df = pd.read_csv(
        f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv')

    rows = get_nastavnik_rows()
    mentors = df.get(NAMES_ROW)

    # Заполняем словарь, в котором ключом является номер строки наставника,
    # а значением - его имя.
    for row in rows:
        MENTORS[row] = mentors.iloc[row]

    # Погнали
    app.start(port=int(os.environ.get("PORT", 3000)))
