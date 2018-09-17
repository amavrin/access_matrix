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
    elif 'full' in s:
        xstr = u"Полные права"
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
                s = Set(['full'])
                Matrix[u][r] = s
            else:
                s = get_random_set()
                Matrix[u][r] = s
            #print "*** " + u + " " + obj_num2name(r) + ": " + " ".join(Matrix[u][r])

def print_matrix():
    for u in (Cfg['users']):
        for r in (Matrix[u].keys()):
            print u"Права " + u + u" на ресурс " + obj_num2name(r) + u": " + " ".join(Matrix[u][r])

def print_user_rights(u):
    print u"Перечень Ваших прав:"
    for r in (Matrix[u]):
        sys.stdout.write(obj_num2name(r) + ": ")
        print rights2str(Matrix[u][r])

def user_login():
    name = raw_input("User:")
    if name == "":
        return
    if name not in Cfg['users']:
        print u"Ошибка идентификации"
        return
    print u"Идентификация прошла успешно, добро пожаловать в систему"
    print_user_rights(name)


parser = argparse.ArgumentParser(description=u'Матрица доступа к ресурсам (дискреционная модель)')
parser.add_argument('-c', dest='conffile', default="access_matrix.ini", help=u'конфигурационный файл')
args = parser.parse_args()
read_config(args.conffile)
print_config()
gen_matrix()
print_matrix()

while 1:
    try:
        user_login()
    except EOFError:
        print u"\nДо свидания"
        exit(0)
