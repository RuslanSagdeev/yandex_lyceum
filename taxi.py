# encoding: utf - 8
import os
import pickle
import traceback
from datetime import datetime
from functools import wraps
import telegram
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.ext import Updater
import sqlite3
import threading
import sched, time
import random

token = '1263996451:AAHASeBMY-5tHbtJU6Ib72ZlBrumJ7nxVU0'

# DataBase

conn = sqlite3.connect("data_base.db", check_same_thread=False)  # или :memory: чтобы сохранить в RAM
cursor = conn.cursor()

# Timer
time_for_bussines = sched.scheduler(time.time, time.sleep)


# Создание таблицы


def catch_error(f):
    @wraps(f)
    def wrap(update, context):
        try:
            return f(update, context)
        except Exception as e:
            send_everyone(update, "Error occured: " + traceback.format_exc())

    return wrap


bot = telegram.Bot(token=token)
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

count_do_sub, count_do_money, count_money_for_hour, bussines = 0, 0, 0, 'Нету'

list_chanel_for_subcrime = {
    '@testruslan1': 0
}
prize_chanel_for_subcrime = {
    '@testruslan1': 0
}
many_works = {
    'Получать пособие по безработице [Прибль - 5]': (555, 1),
    'Дворник [Прибль - 5]': (15, 2)
}
cirk_bussines = {
    'Доход в час': 25,
    'Стоимость': 100,
    'Уровень': 2
}
autosalon = {
    'Доход в час': 100,
    'Стоимость': 400,
    'Уровень': 3
}
many_bussines = {
    'Цирк': cirk_bussines,
    'Автосалон': autosalon
}
many_lvls = {
    1: 10,
    2: 50,
    3: 250
}
# Менюшки
works_menu = [['Устроиться'], ['Уволиться'], ['Работать'], ['В главное меню']]
bussines_menu = [['Купить бизнес'], ['Меню бизнеса'], ['В главное меню']]
my_bussines_menu = [['Информация о бизнесе'], ['Собрать доход'], ['Продать бизнес']]
glavnoe_menu_keyboard = [['Профиль'], ['Работа'], ['Бизнес'], ['Развлечения'], ['Секта']]
entertainments_menu = [['Казино'], ['В главное меню']]
sect_menu = [['Создать секту'], ['Посмотреть приглашения'], ['Меню секты'], ['В главное меню']]
sect_player = [['Управление сектой'], ['Сектанты'], ['Покинуть секту'], ['В главное меню']]
sect_control = [['Пригласить в секту'], ['Выгнать из секты'], ['В главное меню']]
#donate_menu = [['Заработать донат'], ['Пополнить баланс'], ['Донат меню'], ['В главное меню']]
get_payday = [['Работать'], ['В главное меню']]
get_money_buss = [['Снять деньги с бизнеса'], ['В главное меню']]
clans_invites = []
#

current_day = datetime.now()


def send_everyone(update, text):
    bot.send_message(
        chat_id=update.message.chat_id, text=text, disable_web_page_preview=True)


@catch_error
def start(update, context):
    user = update.message.from_user
    data = cursor.execute('SELECT chat_id FROM info where chat_id = ?', (update.message.chat_id,)).fetchall()
    if not data:
        argument = (str(update.message.chat_id))
        cursor.execute("INSERT INTO info VALUES (NULL, ?, ?, 0, 0, 'Безработен', 'Нету', 0, 1, 0, 10, 'No')", (argument,
                                                                                                               user[
                                                                                                                   'first_name'],))
    default_test(update, glavnoe_menu_keyboard, "Приветствую!")


def default_test(update, custom_keyboard, text):
    reply_markup = telegram.ReplyKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
                     text=text,
                     reply_markup=reply_markup)


def count_time_add(update):
    count_work_time = 10
    cursor.execute('UPDATE info SET count_work_time = ? WHERE chat_id = ?',
                   (str(count_work_time), str(update.message.chat_id),))


def money_add_in_hours():
    global count_money_for_hour, bussines
    count_money_for_hour += many_bussines[bussines]['Доход в час']
    threading.Timer(5, money_add_in_hours).start()


@catch_error
def text(update, context):
    global count_do_sub, count_do_money, count_money_for_hour, bussines
    text = update.message.text
    user = update.message.from_user
    count_do_money += count_money_for_hour
    # Обновления
    cursor.execute('UPDATE info SET count_do_subscribe = ? WHERE chat_id = ?',
                   (str(count_do_sub), str(update.message.chat_id),))
    cursor.execute('UPDATE info SET count_money = ? WHERE chat_id = ?',
                   (str(count_do_money), str(update.message.chat_id),))
    cursor.execute('UPDATE info SET count_money_for_hour = ? WHERE chat_id = ?',
                   (str(count_money_for_hour), str(update.message.chat_id),))
    conn.commit()

    # Переменные

    count_work_time = cursor.execute('SELECT count_work_time FROM info WHERE chat_id = ?',
                                     (update.message.chat_id,)).fetchall()[0][0]
    lvl_player = cursor.execute('SELECT lvl FROM info WHERE chat_id = ?',
                                (update.message.chat_id,)).fetchall()[0][0]
    exp_player = cursor.execute('SELECT exp FROM info WHERE chat_id = ?',
                                (update.message.chat_id,)).fetchall()[0][0]
    count_do_sub = cursor.execute('SELECT count_do_subscribe FROM info WHERE chat_id = ?',
                                  (update.message.chat_id,)).fetchall()[0][0]
    count_do_money = cursor.execute('SELECT count_money FROM info WHERE chat_id = ?',
                                    (update.message.chat_id,)).fetchall()[0][0]
    working = cursor.execute('SELECT working FROM info WHERE chat_id = ?',
                             (update.message.chat_id,)).fetchall()[0][0]
    bussines = cursor.execute('SELECT bussines FROM info WHERE chat_id = ?',
                              (update.message.chat_id,)).fetchall()[0][0]
    # Проверка уровня
    if exp_player == many_lvls[lvl_player]:
        lvl_player += 1
        exp_player = 0
        # Добовление работы нового уровня
        cursor.execute('UPDATE info SET lvl = ? WHERE chat_id = ?',
                       (str(lvl_player), str(update.message.chat_id),))
        cursor.execute('UPDATE info SET exp = ? WHERE chat_id = ?',
                       (str(exp_player), str(update.message.chat_id),))
        bot.send_message(chat_id=update.message.chat_id,
                         text='Вы подняли новый уровень, возможно вам открылись новые работы, бизнесы..')
    # Логика
    if text.lower() == 'профиль':
        # Проверка на подписку каналов
        for i in list_chanel_for_subcrime.keys():
            if bot.getChatMember(i, update.message.chat_id) and list_chanel_for_subcrime[i] == 0:
                count = prize_chanel_for_subcrime[i]
                list_chanel_for_subcrime[i] += prize_chanel_for_subcrime[i]

                count_do_money += list_chanel_for_subcrime[i]
                count_do_sub += 1
                # Вывод данных
        text_profile = f"ID - {update.message.chat_id} \nПользователь - {user['first_name']} \nУровень - {lvl_player} [{exp_player} / {many_lvls[lvl_player]}]"
        text_profile2 = f"\nКоличество денег - {count_do_money} \nРабота - {working} \nБизнес - {bussines}"
        send_everyone(update, text_profile + text_profile2)
    # Секта
    elif text.lower() == 'секта':
        default_test(update, sect_menu, 'Выберите нужный пункт')
        # Создание секты
    elif text.lower() == 'посмотреть приглашения':
        if cursor.execute("SELECT in_sect FROM info WHERE chat_id = ?",
                          (str(update.message.chat_id),)).fetchall()[0][0] == 'Yes':
            print('Вы уже в секте')
            clans_invites.clear()
        else:
            invites = conn.execute("SELECT * FROM invitations WHERE player_id = ?",
                                   (str(update.message.chat_id),)).fetchall()
            for i in invites:
                clan = conn.execute("SELECT name_sect FROM secta WHERE id_sect = " + str(i[0])).fetchall()
                clans_invites.append(['Клан - ' + clan[0][0] + ' Приглашает вас'])
            clans_invites.append(['В главное меню'])
            default_test(update, clans_invites, 'Выберите секту для вступления')
    elif 'организовать секту' in text.lower():
        if count_do_money >= 100:
            count_do_money -= 100
            conn.execute('INSERT INTO secta VALUES (NULL, ?)', (text.lower().split()[2],))
            conn.commit()
            id_sect = conn.execute('SELECT id_sect FROM secta WHERE name_sect = ?',
                                   (text.lower().split()[2],)).fetchall()
            conn.execute("INSERT INTO player_in_sect VALUES (?, ?, 'Создатель')",
                         (id_sect[0][0], update.message.chat_id,))
            cursor.execute('UPDATE info SET in_sect = ? WHERE chat_id = ?',
                           ('Yes', str(update.message.chat_id),))
            conn.commit()
        else:
            print('Нету бабла')
    elif text.lower() == 'создать секту':
        flag = True
        for chat_id in conn.execute('SELECT chat_id FROM info').fetchall():
            for founds in conn.execute('SELECT id_sect FROM player_in_sect').fetchall():
                if chat_id[0] == founds[0]:
                    flag = False
        if flag == False:
            default_test(update, sect_menu, 'Вы уже находитесь в секте')
        else:
            bot.send_message(chat_id=update.message.chat_id,
                             text='Стоимость создания секты 100 рублей\nВведите Организовать секту [name_sect], для того чтобы создать секту')
    if conn.execute('SELECT in_sect FROM info WHERE chat_id = ?',
                         (str(update.message.chat_id),)).fetchall()[0][0] == 'Yes':
        if text.lower() == 'меню секты':
            default_test(update, sect_player, 'Выберите нужный пункт')
        elif text.lower() == 'сектанты':
            list_sectants = {}
            id_sect = conn.execute('SELECT id_sect FROM player_in_sect WHERE id_player = ?',
                                   (str(update.message.chat_id),)).fetchall()
            for i in conn.execute('SELECT id_player FROM player_in_sect WHERE id_sect = ?',
                                  (str(id_sect[0][0]),)).fetchall():
                list_sectants[i[0]] = \
                    conn.execute('SELECT name FROM info WHERE chat_id = ?', (str(i[0]),)).fetchall()[0][0]
            sectants = ''
            for i in list_sectants.keys():
                sectants += '[' + str(i) + '] ' + str(list_sectants[i]) + ' - ' + \
                            conn.execute('SELECT role_man FROM player_in_sect WHERE id_player = ?',
                                         (str(i),)).fetchall()[0][0] + '\n'
            bot.send_message(chat_id=update.message.chat_id,
                             text=sectants)
        elif text.lower() == 'покинуть секту':
            role = conn.execute('SELECT role_man FROM player_in_sect WHERE id_player = ?',
                                (update.message.chat_id,)).fetchall()[0][0]
            if role == 'Создатель':
                print('Вы создатель, сначала расформируйте состав')
            else:
                print('Вы покинули секту')
                cursor.execute("DELETE FROM player_in_sect WHERE id_player = ?", (str(update.message.chat_id),))
                conn.commit()
        elif text.lower() == 'управление сектой':
            if conn.execute('SELECT in_sect FROM info WHERE chat_id = ?', (str(
                    update.message.chat_id),)).fetchall()[0][0] == 'Yes':
                role = conn.execute('SELECT role_man FROM player_in_sect WHERE id_player = ?',
                                    (update.message.chat_id,)).fetchall()
                if role[0][0] == 'Создатель':
                    default_test(update, sect_control, 'Меню управления сектой')
                else:
                    print('Достпу запрещен')
            else:
                print('Вы не состоите в секте')
        elif 'пригласить в секту' == text.lower() and \
                conn.execute('SELECT role_man FROM player_in_sect WHERE id_player = ?',
                             (update.message.chat_id,)).fetchall()[0][0] == 'Создатель':
            bot.send_message(chat_id=update.message.chat_id,
                             text='Введите:\n Законтролировать [ID приглашённого]')
        elif 'выгнать из секты' == text.lower() and \
                conn.execute('SELECT role_man FROM player_in_sect WHERE id_player = ?',
                             (update.message.chat_id,)).fetchall()[0][0] == 'Создатель':
            bot.send_message(chat_id=update.message.chat_id,
                             text='Введите:\n уничтожить [ID жертвы]')
        elif 'ничтожить' in text.lower() and \
                conn.execute('SELECT role_man FROM player_in_sect WHERE id_player = ?',
                             (update.message.chat_id,)).fetchall()[0][0] == 'Создатель':
            print(123)
            cursor.execute("DELETE FROM player_in_sect WHERE id_player = ?", (str(text.lower().split()[1]),))
            conn.commit()
            bot.send_message(chat_id=int(text.lower().split()[1]), text='Вас выгнали из секты')


        elif 'аконтролировать' in text.lower() and \
                conn.execute('SELECT role_man FROM player_in_sect WHERE id_player = ?',
                             (update.message.chat_id,)).fetchall()[0][0] == 'Создатель':
            print('Попробуй')
            id_sect = conn.execute('SELECT id_sect FROM player_in_sect WHERE id_player = ?',
                                   (str(update.message.chat_id),)).fetchall()
            conn.execute('INSERT INTO invitations VALUES (NULL, ?, ?)', (text.lower().split()[1], id_sect[0][0],))
            conn.commit()
    else:
        print('Вы не в секте')
    # Развлечения
    if text.lower() == 'развлечения':
        default_test(update, entertainments_menu, 'Выберите один из видов развлечения')
    # Казино
    elif text.lower() == 'казино':
        bot.send_message(chat_id=update.message.chat_id,
                         text='Введите \' Поставить (Сумму ставки) (Против сколько человек[Максимум:9])')
    elif 'поставить' in text.lower():
        summa_win = 0
        summa = int(text.lower().split(' ')[1])
        counts_man = int(text.lower().split(' ')[2])
        if summa <= count_do_money and summa > 0:
            if counts_man <= 10 and counts_man > 0:
                if random.randint(0, 100) <= 100 // (counts_man + 1):
                    summa_win = summa * (counts_man + 1)
                    count_do_money += summa_win
                    default_test(update, entertainments_menu,
                                 'Вы выиграли - {} [x{}]'.format(summa_win, 100 // (counts_man + 1)))
                else:
                    default_test(update, entertainments_menu,
                                 'Вы проиграли - {}'.format(summa))
                    count_do_money -= summa
            else:
                default_test(update, entertainments_menu,
                             'Максимальное количество соперников - 9')
        else:
            default_test(update, entertainments_menu,
                         'Недостаточно средств на вашем балансе.')
    elif text.lower() == 'бизнес':
        default_test(update, bussines_menu, 'Выберите нужный пункт')
    elif text.lower() == 'меню бизнеса':
        if bussines != 'Нету':
            default_test(update, get_money_buss,
                         'Название бизнеса - ' + bussines +
                         '\nСтоимость бизнеса - ' + str(many_bussines[bussines]['Стоимость']) +
                         '\nПрибыль в час - ' + str(many_bussines[bussines]['Доход в час']) +
                         '\nЗаработано - ' + str(count_money_for_hour)
                         )
        else:
            default_test(update, glavnoe_menu_keyboard, 'У вас нету бизнеса')
    elif text.lower() == 'купить бизнес':
        busses = []
        for key in many_bussines:
            print(key)
            if lvl_player >= many_bussines[key]['Уровень']:
                busses.append([str(key) + ', доход в час - ' + str(many_bussines[key]['Доход в час'])])
        default_test(update, busses, 'Выберите один из вариантов')
    elif text.lower() == 'снять деньги с бизнеса':
        if bussines != 'Нету':
            default_test(update, bussines_menu, 'Вы успешно сняли деньги с бизнеса')
            count_do_money += count_money_for_hour

    elif text.lower() == 'работа':
        default_test(update, works_menu, 'Выберите нужный пункт')
    elif text.lower() == 'устроиться':
        works = []
        if working == 'Безработен':
            for i in many_works.items():
                if lvl_player >= i[1][1]:
                    becouse_error = []
                    becouse_error.append(i[0])
                    works.append(becouse_error)
                    becouse_error = []
            default_test(update, works, 'Выберите один из вариантов трудоустройства')
        else:
            default_test(update, works_menu, 'Вы уже работаете')
    elif text.lower() == 'уволиться':
        if working != 'Безработен':
            working = 'Безработен'
            cursor.execute('UPDATE info SET working = ? WHERE chat_id = ?',
                           (str(working), str(update.message.chat_id),))
            default_test(update, works_menu, 'Вы успешно уволились')
        else:
            default_test(update, works_menu, 'Вы и так никем не работаете')
    elif text.lower() == 'в главное меню':
        default_test(update, glavnoe_menu_keyboard, 'Вы перешли в главное меню')
    elif text.lower() == 'работать':
        if working != 'Безработен' and count_work_time > 0:
            default_test(update, get_payday, f'Вы заработали - {many_works[working][0]}')
            exp_player += 1
            cursor.execute('UPDATE info SET exp = ? WHERE chat_id = ?',
                           (str(exp_player), str(update.message.chat_id),))
            count_do_money += many_works[working][0]
            count_work_time -= 1
            cursor.execute('UPDATE info SET count_work_time = ? WHERE chat_id = ?',
                           (str(count_work_time), str(update.message.chat_id),))

        elif count_work_time == 0:
            default_test(update, glavnoe_menu_keyboard, 'Вы устали, приходите через один час.')
            Timer = threading.Timer(3600, count_time_add)
            Timer.start()
        else:
            default_test(update, works_menu, 'Вы и так никем не работаете')

    # Система бизнеса и работ
    try:
        for key in many_bussines:
            if text.lower()[:text.lower().index(',')] == key.lower() and bussines == 'Нету' and many_bussines[key]['Уровень'] <= lvl_player:
                if count_do_money >= many_bussines[key]['Стоимость']:
                    bussines = key
                    cursor.execute('UPDATE info SET bussines = ? WHERE chat_id = ?',
                                   (str(bussines), str(update.message.chat_id),))
                    default_test(update, bussines_menu, f'Вы успешно купили бизнес - {bussines}')
                    Timer2 = threading.Timer(5, money_add_in_hours)
                    Timer2.start()

                else:
                    default_test(update, bussines_menu, f'У вас недостаточно средств')
            elif bussines != 'Нету' and text.lower() == key.lower():
                default_test(update, bussines_menu, f'У вас уже есть бизнес')
    except:
        pass
    for i in clans_invites:
        if text == i[0]:
            id_sect = id_sect = conn.execute('SELECT id_sect FROM secta WHERE name_sect = ?',
                                             (text.split()[2],)).fetchall()
            conn.execute('INSERT INTO player_in_sect VALUES (?, ?, ?)',
                         (str(id_sect[0][0]), str(update.message.chat_id), 'Участник',))
            conn.commit()
            print('Всё работает')
            clans_invites.clear()
            break

    for wor in many_works.keys():
        if text.lower() == wor.lower() and working == 'Безработен':
            if lvl_player < many_works[wor][1]:
                default_test(update, works_menu, f'Вам не хватает игрового уровня, вам нужен - {many_works[wor][1]}')
            else:
                working = wor
                cursor.execute('UPDATE info SET working = ? WHERE chat_id = ?',
                               (str(working), str(update.message.chat_id),))
                default_test(update, works_menu, f'Вы успешно устроились на работу - {working}')
        elif text.lower() == wor.lower():
            default_test(update, works_menu, 'Для начала нужно уволиться.')


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

text_handler = MessageHandler(Filters.text, text)
dispatcher.add_handler(text_handler)
updater.start_polling()
