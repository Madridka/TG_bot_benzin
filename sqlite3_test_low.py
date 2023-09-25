import sqlite3


db = sqlite3.connect('benzin.sql')
cur = db.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS benzin ('
            'id INTEGER PRIMARY KEY,'
            'day INT,'
            'Probeg INT,'
            'Raschod FLOAT)')
db.commit()


def calc_raschod():
    # ввод данных
    day = str(input('Дата заправки: '))
    if day == 'delete' or day == 'удалить':
        vivod()
        what_id = int(input('Какую запись?: '))
        cur.execute(f"DELETE FROM benzin where id = {what_id}")
        db.commit()
        print(f'Удалена запись № {what_id}')
        return
    if day == 'print' or day == 'таблица':
        vivod()
    try:
        tprob = int(input('Текущий пробег: '))
        pprob = int(input('Прошлый пробег: '))
        probeg = tprob - pprob
        summa = float(input('На сколько заправился?: '))
        stbenz = float(input('Стоимость литра бенза?: '))
    except ValueError:
        print('Вводи цифры')
        return

    # расчет + вывод в ДБ
    raschod = round((summa/stbenz) / (probeg/100), 0)
    cur.execute(f"INSERT INTO benzin (day, Probeg, Raschod) VALUES ('{day}', '{probeg}', '{raschod}')")
    db.commit()


def vivod():
    for value in cur.execute('SELECT id, day, probeg, raschod from benzin'):
        print(f'{value[0]}. Дата: {value[1]}, Пробег: {value[2]}км, Расход: {value[3]}л/100км')


def main():
    calc_raschod()
    vivod()
    db.close()


if __name__ == '__main__':
    main()
