#!/usr/bin/env python2
# coding=utf-8

import ConfigParser
import argparse
from sets import Set
import random
import sys

# позволяет редактировать строку, вводимую через raw_input
import readline


# конфигурационные параметры сохраняем в переменной Cfg
Cfg = {}

# матрица доступов, организована в виде словаря; первый ключ - имя пользователя, второй - номер ресурса
# значение - множество (Set) прав доступа к ресурсу. Права доступа - read, write и grant
Matrix = {}

# возвразщает удобочитаемое название права доступа
def verbose_x(x):
    r_s = {}
    r_s['read'] = u"Доступ на чтение"
    r_s['write'] = u"Доступ на запись"
    r_s['grant'] = u"Передача прав"

    if x not in r_s:
        print "no such access: " + x
        return "NO NAME"
    return r_s[x]
    

# возращает описание прав доступа для множества в виде строки, разделённой запятыми
def rights2str(s):

    xstr = ""
    if len(s) == 0:
        xstr = u"Запрет"
    else:
        xstr = ", ".join(map( verbose_x, s))

    return xstr


# возвращает удобочитаемое имя ресурса по его номеру
def obj_num2name(num):
    return u'Объект' + str(num)

# чтение конфигурационного файла, путь к которому задан в качестве аргумента
def read_config(conffile):
    config = ConfigParser.ConfigParser()
    config.read(conffile)

    # количество ресурсов в системе
    Cfg['resno'] = int( config.get('config','number_of_resources') )

    # список пользователей системы
    Cfg['users'] = config.get('config','users').split()

    # имя администратора
    Cfg['admin'] = config.get('config','admin')

    # вывод дополнительной информации по ходу выполнения программы
    if config.get('config','verbose') == "on":
        Cfg['verbose'] = True
    else:
        Cfg['verbose'] = False

    # дополнительная команда пользователя - matrix, выводит текущую матрицу доступов. Удобно для демонстрации операции grant
    Cfg['matrix_cmd'] = config.get('config','matrix_cmd')

# вывод основных конфигурационных параметров
def print_config():
    print u'Количество ресурсов: '.encode('utf8') + str( Cfg['resno'] )
    print u'Количество пользователей: ' + str(len(Cfg['users']))
    print u'Список пользователей: ' + u" ".join(Cfg['users'])
    print u'Администратор: ' + Cfg['admin']

# Вспомогательная функция для заполнения матрицы доступа.
# Случайным образом возвращает набор прав.
# Варианты: нет прав, только read, read+write, read+grant, read+write+grant
def get_random_set():
    rnd = random.randint(0,4)
    s = Set()
    if rnd == 1:
        s.add('read')
    elif rnd == 2:
        s.add('read')
        s.add('write')
    elif rnd == 3:
        s.add('read')
        s.add('grant')
    elif rnd == 4:
        s.add('read')
        s.add('write')
        s.add('grant')
    # если rnd был равен 0, вернётся пустое множество (без прав)
    return s

# Генерация матрицы доступов.
def gen_matrix():
    for u in (Cfg['users']):
        Matrix[u] = {}
        for r in range(1, Cfg['resno'] + 1):
            if u == Cfg['admin']:
                # администратору добавить все права
                s = Set(['read', 'write', 'grant'])
                Matrix[u][r] = s
            else:
                # обычным пользователям назначить случайным образом
                s = get_random_set()
                Matrix[u][r] = s

# вспомогательная функция - получить имя пользователя с консольного ввода.
# в случае, если был нажат Enter без указания имени - выводит предупреждение
def get_user(message):
    sys.stdout.write(message)
    u = raw_input(" ")
    if u == "":
        print u"Пользователь не выбран"
        return ""

    return u

# вспомогательная функция для операции передачи прав - получить название права с консольного ввода.
# в случае, если был нажат Enter без указания права - выводит предупреждение
# проверяет допустимый набор прав для передачи (read, write)
def get_access_name(message):
    sys.stdout.write(message)
    x = raw_input(" ")
    if x == "":
        print u"Право не выбрано"
        return ""

    if x not in ('read', 'write'):
        print u"Доступные права для передачи: read, write"
        return ""

    return x


# вспомогательная функция - получить номер ресурса с консольного ввода.
# в случае, если был нажат Enter без указания номера ресурса - выводит предупреждение
# если был недопустимый ввод (не числовое значение) - выводит предупреждение
def get_resource_num(message):
    sys.stdout.write(message)
    r = raw_input(" ")
    if r == "":
        print u"Объект не выбран"
        return 0

    try:
        r = int(r)
    except:
        print u"введите целое число"
        return 0

    return r

# добавляет в матрицу доступов право x на ресурс r пользователю u
# проверяет наличие ресурса и пользователя в системе, и вхождение права в допустимый набор прав (read, write)
def process_grant(u, r, x):
    if r not in range(1,Cfg['resno'] + 1):
        print u"ресурс не определён, введите число от 1 до " + str(Cfg['resno'])
        return False

    if u not in Cfg['users']:
        print u"пользователь " + u + u" не зарегистрирован в системе"
        return False

    if x not in ('read', 'write'):
        print u"Можно передавать права только на чтение или запись"
        return False

    Matrix[u][r].add(x)
    return True

# проверяет условие передачи права x: наличие права grant и передаваемого права у передающего пользователя
# также проверяет вхождеие права в допустимый для передачи набор, и наличие обоих пользователей в системе
def check_grant(u, r, u2, x):
    if x not in ('read', 'write'):
        print u"Можно передавать права только на чтение или запись"
        return False

    if u not in Cfg['users']:
        print u"пользователь " + u + u", передающий права, не зарегистрирован в системе"
        return False

    if u2 not in Cfg['users']:
        print u"пользователь " + u2 + u", которому передаются права, не зарегистрирован в системе"
        return False

    # пользователь, передающий права, должен иметь право grant и передаваемое право на объект
    if 'grant' in Matrix[u][r] and x in Matrix[u][r]:
        print u"Операция прошла успешно"
        return True
    else:
        print u"Отказ в выполнении операции передачи прав. У Вас нет прав для ее осуществления"
        return False

# проверяет наличие прав read, write или grant для указанного пользователя на указанный ресурс
def check_access(u, r, c):
    if r not in range(1,Cfg['resno'] + 1):
        print u"ресурс не определён, введите число от 1 до " + str(Cfg['resno'])
        return False

    if u not in Cfg['users']:
        print u"пользователь " + u + u" не зарегистрирован в системе"
        return False

    if c in Matrix[u][r]:
        return True
    else:
        print u"Отказ в выполнении операции. У Вас нет прав для ее осуществления"
        return False

# выводит матрицу доступов
def print_matrix():
    for u in (Cfg['users']):
        for r in (Matrix[u].keys()):
            print u"Права " + u + u" на ресурс " + obj_num2name(r) + u": " + " ".join(Matrix[u][r])

# вызывается в цикле, обрабатывает ввод пользователя.
# получает параметром имя зарегистрированного пользователя
# возвращает "CONTINUE" для всех операций, кроме случая завершения сеанса, тогда возвращает "QUIT"
def process_user_command(u):
    sys.stdout.write(u"Жду ваших указаний")

    try:
        c = raw_input(" > ")
    except:
        # пользователь нажал control-D, выход из системы
        sys.stdout.write("\n")
        c = "quit"

    c = c.rstrip()

    if c == 'read' or c == 'write':
        r = get_resource_num(u"Над каким объектом производится операция?")
        if r == 0:
            # не смогли получить номер ресурса
            return "CONTUNUE"
        if check_access(u, r, c):
            print u"Операция прошла успешно"
        return "CONTUNUE"

    elif c == 'grant':
        r = get_resource_num(u"Право на какой объект передается?")
        if r == 0:
            # не смогли получить номер ресурса
            return "CONTUNUE"

        if not check_access(u, r, c):
            # у пользователя нет права grant для данного ресурса
            return "CONTUNUE"

        x = get_access_name(u"Какое право передается?")
        if x == "":
            # не смогли получить имя передаваемого права
            return "CONTUNUE"

        if not check_access(u, r, x):
            # у пользователя нет передаваемого права для данного ресурса
            return "CONTUNUE"

        u2 = get_user(u"Какому пользователю передается право?")
        if u2 == "":
            # не смогли получить имя принимающего право пользователя
            return "CONTUNUE"
        
        if check_grant(u, r, u2, x):
            # успешно прошли проверку возможности передачи права, производим модификацию матрицы доступа
            process_grant(u2, r, x)
        return "CONTUNUE"

    elif c == "":
        # пользователь нажал Enter
        return "CONTUNUE"

    elif c == 'quit':
        print u"Работа пользователя " + u + u" завершена. До свидания."
        return "QUIT"

    elif c == 'matrix' and Cfg['matrix_cmd'] == "on":
        print_matrix()
        return "CONTUNUE"
    else:
        print u"Задана недопустимая операция"
        return "CONTUNUE"

# выводит права пользователя в удобочитаемом виде
def print_user_rights(u):
    print u"Перечень Ваших прав:"
    for r in (Matrix[u]):
        sys.stdout.write(obj_num2name(r) + ": ")
        print rights2str(Matrix[u][r])

# производит регистрацию пользователя: получает имя пользователя и проверяет его наличие в системе
def user_login():
    name = raw_input("User: ")
    if name == "":
        return
    if name not in Cfg['users']:
        print u"Ошибка идентификации"
        return
    print u"Идентификация прошла успешно, добро пожаловать в систему"
    print_user_rights(name)
    while process_user_command(name) != "QUIT":
        continue
        

# получаем возможное имя конфигурационного файла (ключ -c)
parser = argparse.ArgumentParser(description=u'Матрица доступа к ресурсам (дискреционная модель)')
parser.add_argument('-c', dest='conffile', default="access_matrix.ini", help=u'конфигурационный файл')
args = parser.parse_args()

try:
    read_config(args.conffile)
except Exception as e:
    print u"ошибка чтения конфигурационного файла"
    print e
    sys.exit(1)

# вывод конфигурационных параметров
if Cfg['verbose']:
    print_config()

# генерация матрицы доступа
gen_matrix()
if Cfg['verbose']:
    print_matrix()

# цикл регистрации пользователей в системе
while True:
    try:
        user_login()
    except EOFError:
        # пользователь нажал control-D, завершаем работу
        print u"\nРабота системы завершена. До свидания"
        exit(0)
