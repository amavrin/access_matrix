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

def get_resource_num(message):
    sys.stdout.write(message)
    r = raw_input(" ")
    if r == "":
        print u"Объект не выбран"
        return True

    try:
        r = int(r)
    except:
        print u"введите целое число"
        return 0

    return r

def process_grant(u, r):
    r = get_resource_num(u"Право на какой объект передается?")
    if r == 0:
        raise Exception(u"не получен номер объекта для передачи прав")

def check_access(u, r, c):
    if r not in range(1,Cfg['resno'] + 1):
        raise Exception(u"ресурс не определён, введите число от 1 до " + str(Cfg['resno']))

    if c in Matrix[u][r]:
        return True
    else:
        return False

def print_matrix():
    for u in (Cfg['users']):
        for r in (Matrix[u].keys()):
            print u"Права " + u + u" на ресурс " + obj_num2name(r) + u": " + " ".join(Matrix[u][r])

def process_user_command(u):
    sys.stdout.write(u"Жду ваших указаний")

    r = 0

    try:
        c = raw_input(" > ")
    except:
        # пользователь нажал control-D, выход из системы
        sys.stdout.write("\n")
        c = "quit"

    c = c.rstrip()
    if c == 'read' or c == 'write':
        r = get_resource_num(u"Над каким объектом производится операция?")

    elif c == "":
        return True
    elif c == 'quit':
        print u"Работа пользователя " + u + u" завершена. До свидания."
        return False
    elif c == 'matrix' and Cfg['matrix_cmd'] == "on":
        print_matrix()
        return True
    else:
        print u"Задана недопустимая операция"
        return True

    try:
        if check_access(u, r, c):
            print u"Операция прошла успешно"
        else:
            print u"Отказ в выполнении операции. У Вас нет прав для ее осуществления"
    except Exception as e:
        m, = e.args
        sys.stdout.write(u" *** ошибка проверки прав доступа: ")
        print m.encode("utf-8")
    return True

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
    while process_user_command(name):
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
