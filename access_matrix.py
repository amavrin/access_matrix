#!/usr/bin/env python2
# coding=utf-8

import ConfigParser
import argparse
from sets import Set
import random
import readline
import sys

# конфигурационные параметры сохраняем в переменной Cfg
Cfg = {}

# матрица доступов
Matrix = {}

def verbose_x(x):
    r_s = {}
    r_s['read'] = u"Доступ на чтение"
    r_s['write'] = u"Доступ на запись"
    r_s['grant'] = u"Передача прав"

    if x not in r_s:
        print "no such access: " + x
        return "NO NAME"
    return r_s[x]
    

# возращает описание прав доступа
def rights2str(s):

    xstr = ""
    if len(s) == 0:
        xstr = u"Запрет"
    else:
        xstr = ", ".join(map( verbose_x, s))

    return xstr


def obj_num2name(num):
    return u'Объект' + str(num)

# чтение конфигурационного файла, путь к которому задан в качестве аргумента
def read_config(conffile):
    config = ConfigParser.ConfigParser()
    config.read(conffile)
    Cfg['resno'] = int( config.get('config','number_of_resources') )
    Cfg['users'] = config.get('config','users').split()
    Cfg['admin'] = config.get('config','admin')

    if config.get('config','verbose') == "on":
        Cfg['verbose'] = True
    else:
        Cfg['verbose'] = False

    Cfg['matrix_cmd'] = config.get('config','matrix_cmd')

# вывод конфигурационных параметров
def print_config():
    print u'Количество ресурсов: '.encode('utf8') + str( Cfg['resno'] )
    print u'Количество пользователей: ' + str(len(Cfg['users']))
    print u'Список пользователей: ' + u" ".join(Cfg['users'])
    print u'Администратор: ' + Cfg['admin']

def get_random_set():
    # варианты: none, read, read+write, read+grant, read+write+grant
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
    return s

def gen_matrix():
    for u in (Cfg['users']):
        Matrix[u] = {}
        for r in range(1, Cfg['resno'] + 1):
            if u == Cfg['admin']:
                s = Set(['read', 'write', 'grant'])
                Matrix[u][r] = s
            else:
                s = get_random_set()
                Matrix[u][r] = s
            #print "*** " + u + " " + obj_num2name(r) + ": " + " ".join(Matrix[u][r])

def get_user(message):
    sys.stdout.write(message)
    u = raw_input(" ")
    if u == "":
        print u"Пользователь не выбран"
        return ""

    return u

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

def print_matrix():
    for u in (Cfg['users']):
        for r in (Matrix[u].keys()):
            print u"Права " + u + u" на ресурс " + obj_num2name(r) + u": " + " ".join(Matrix[u][r])

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
            return "CONTUNUE"
        if check_access(u, r, c):
            print u"Операция прошла успешно"
        return "CONTUNUE"

    elif c == 'grant':
        r = get_resource_num(u"Право на какой объект передается?")
        if r == 0:
            return "CONTUNUE"

        if not check_access(u, r, c):
            return "CONTUNUE"

        x = get_access_name(u"Какое право передается?")
        if x == "":
            return "CONTUNUE"

        if not check_access(u, r, x):
            return "CONTUNUE"

        u2 = get_user(u"Какому пользователю передается право?")
        if u2 == "":
            return "CONTUNUE"
        
        if check_grant(u, r, u2, x):
            process_grant(u2, r, x)
        return "CONTUNUE"

    elif c == "":
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

def print_user_rights(u):
    print u"Перечень Ваших прав:"
    for r in (Matrix[u]):
        sys.stdout.write(obj_num2name(r) + ": ")
        print rights2str(Matrix[u][r])

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
        1
        


parser = argparse.ArgumentParser(description=u'Матрица доступа к ресурсам (дискреционная модель)')
parser.add_argument('-c', dest='conffile', default="access_matrix.ini", help=u'конфигурационный файл')
args = parser.parse_args()

read_config(args.conffile)
if Cfg['verbose']:
    print_config()

gen_matrix()
if Cfg['verbose']:
    print_matrix()

while 1:
    try:
        user_login()
    except EOFError:
        print u"\nРабота системы завершена. До свидания"
        exit(0)
