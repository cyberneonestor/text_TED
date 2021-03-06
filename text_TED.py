"""
Скрипт предназначет для автоматического извлечения текста из файлов различных форматов
с последующим автоматическим переводом его. 

Для улучшения качества перевода предусмотрена возможность 
автоматического исправления некоторых ошибок распознования текста, удаления лишних переносов, 
поиска и замены аббревиатур на исходные термины. 

Перевод осуществляется с использованием google либо yandex переводчика, соответственно, 
для проведения перевода требуется подключение к интернету. 

Так же во время перевода должен быть обязательно запущен браузер Tor, 
необходимый для обхода блокировки множественных запросов google переводчиком.

На вход программы подается путь до переводимого файла.

Переведенный текст сохраняется в папке с исходным файлом в формате .txt, название файла составляется из
заранее заданного префикса и исходного имени файла.

Поддерживаемые форматы файлов: .pdf, .txt

По умолчанию язык исходных файлов английский, язык перевода - русский.

Для корректной работы скрипта доблжны быть установлены следующие зависимости:
- ImageMagic (библиотека wang работает через него)
- Ghostscript (нужен для обработки PDF)
- Tesseract-ocr (нужен для распознования текста)
- Браузер Tor (нужен для обхода блокировки доступа к google переводчику)

Используемые функции:
- text_ted - основная функция интерфейса, запускающая последовательно другие функции,
отвечающие за обработку и перевод текста.
- SetFile - класс-контейнер для обрабатываемых файлов
- extract_text - извлекает текст из исходного файла
- spell_text - проверяет текст на наличие ошибок распознования и исправляет их
- ABBREVS_to_termins - находит и заменяет в тексте аббревиатуры на соответствующие им термины
- google_translate_text - переводит текст используя google переводчик
- yandex_translate_text - переводит текст используя yandex переводчик
- save_text - сохраняет текст в выходной фаил
"""





#____________Интерфейс модуля_____________


def text_ted(f, in_lang, out_lang='ru', pref='finally'):
    '''
    Принимает полный путь к рабочему файлу, метку языка файла (eng, ru), метку языка перевода (eng, ru)
    если язык перевода не указан, то по умолчанию используется русский, кроме этого принимает необязательный
    параметр - префикс для выходного файла, по умолчаниь равный 'finally'. В результат работы сохраняет в 
    фаил .txt в папке исходного файла.
    '''
    work_file = SetFile(file_path=f, lang=in_lang)
    work_file.extract_text()
    work_file.text = spell_text(_work_file=work_file)
    work_file.text = ABBREVS_to_termins(_work_file=work_file)
    # work_file.text = google_translate_text(_work_file=work_file, out_lang=out_lang)
    work_file.text = yandex_translate_text(_work_file=work_file, out_lang=out_lang)
    work_file.save_text(pref=pref)

def main():
    f = input('Введите абсолютный путь к рабочему файлу: ')
    in_lang = input('Введите язык рабочего файла (eng, ru): ')
    out_lang = input('Введите язык перевода (ru, eng): ')
    pref = input('Введите произвольный префикс для выходного файла: ')
    text_ted(f=f, in_lang=in_lang, out_lang=out_lang, pref=pref)








#________________Тело модуля________________

import requests
import io
import pytesseract
import re
import os.path
import pyaspeller
import future
import socks
import socket
import time
from googletrans import Translator
from yandex_translate import YandexTranslate
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
from PIL import Image as PI
from wand.image import Image   # У библиотеки Wand существует несколько обязательных зависиместей, которые необходимо устанавливать в операционную систему: ImageMagic(собственно wang работает через него) и Ghostscript(нужен для обработки PDF)
from tqdm import tqdm

# Класс SetFile создает объект файла, с которым будем работать

class SetFile():

    def __init__(self, file_path: str, lang: str):
        #Принимает путь к обрабатываемому файлу и язык исходного файла в виде строк

        if '/' in file_path:
            file_dir_index = file_path.rfind('/') + 1
        else:
            file_dir_index = file_path.rfind('\\') + 1

        self.path = file_path
        self.dir = file_path[:file_dir_index]
        self.name = file_path[file_dir_index:file_path.rfind('.')]
        self.type = file_path[file_path.rfind('.')+1:]
        self.lang = lang
        self.text = []


    def extract_text(self):
        """ В зависимостие от формата файла вызывает функции, 
            извлекающие текст из файла и записывающие полученный текст в виде list'а в аттрибут text

        """
        if self.type == 'txt':
            return self._get_text_TXT()

        elif self.type == 'pdf':
            return self._get_text_PDF()

        else:
            # Добавить вызов исключения
            print('Не поддерживаемый формат файла')


    def save_text(self, pref = None):
        """ Сохраняет текст, хранящийся в аттрибуте text, в фаил в формате .txt
            Имя файла составляется из имени входного файла с добавлением префикса pref.
            По умолчанию префикс приравнивается "флагу" языка входного файла.
            По желанию можно задать произвольный префикс, передав его в качестве аргумента при вызове этого метода.
        """
        if pref == None:
            pref = self.lang

        output_name = '{0}{1}_{2}.txt'.format(self.dir, pref, self.name)
        with open(output_name, 'w', encoding="utf-8") as output:
            for text_page in self.text:
                output.write(text_page)

        print("Текст из файла \"{0}.{1}\" сохранен в формате txt в папке {2}".format(self.name, self.type, self.dir), end='\n\n')


    def _get_text_TXT(self):
        """ Читает построчно текстовый фаил (в формате .txt) и
            записывает полученный список строк в аттрибут text.

        """
        self.text = []

        print("Пристапаю к извлечению текста из файла \"{0}.{1}\"".format(self.name, self.type), end='\n')

        encoding = ['utf-8', 'windows-1251', 'ASCII', 'US-ASCII', 'Big5', 'cp500', 'utf-16', 'GBK']

        for enc in encoding:
            try:
                with open(self.path, 'r', encoding=enc) as f_text:
                    for string in tqdm(f_text, desc='Прогресс обработки файла '):
                        self.text.append(string)
            except (UnicodeDecodeError, LookupError):
                pass
            else:
                break
        
        print("Текст из файла \"{0}.{1}\" извлечен".format(self.name, self.type), end='\n')

        return self.text


    def _get_text_PDF(self):
        """ Распознает текст из файла в формате .pdf , 
            вызывает функцию remove_line_breaks, удаляющую лишние переносы строк из текста,
            записывает полученный откоректированный список строк в аттрибут text.

        """
        # Придумать как получать не все станицы из файла сразу, а по одной, то есть получить объект в формате "генератора"

        img = Image(filename=self.path, resolution=300)   # Извлекаю страницы из файла PDF в формате "jpeg", разрешением 300dpi
        img_jpeg = img.convert('jpeg')
        img_bloobs = (Image(image=im).make_blob('jpeg') for im in img_jpeg.sequence)

        print("Фаил \"{0}.{1}\" подготовлен для извлечения текста".format(self.name, self.type), end='\n\n')

        raw_text = []
        page_num = 0

        print("Начинаю распознование текста в файле \"{0}.{1}\"".format(self.name, self.type), end='\n\n')

        for img_blob in img_bloobs:
            page_image = PI.open(io.BytesIO(img_blob))
            text = pytesseract.image_to_string(page_image, lang=self.lang)
            raw_text.append(text)

            page_num += 1
            print("Распознан текст на странице {0}".format(page_num), end='\n\n')

        self.text = self.remove_line_breaks(raw_text)

        print("Текст из файла \"{0}.{1}\" распознан и извлечен".format(self.name, self.type), end='\n\n')

        return self.text


    def remove_line_breaks(self, text: list):
        """ Удаляет лишние переносы строк из текста 
            (чтобы абзацы были записаны одной строкой, так они будут правильно обработаны в дальнейшем)

        """
        mod_text = []

        for page_text in text:

            pattern = r'\n\n'
            mod_page_text = re.sub(pattern, 'FFFFF', page_text)

            pattern = r'-?\n'
            mod_page_text = re.sub(pattern, ' ', mod_page_text)

            pattern = r'FFFFF'
            mod_page_text = re.sub(pattern, '\n\n', mod_page_text)

            mod_text.append(mod_page_text)

        print('Текст извлеченный из файла \"{0}.{1}\" откорректирован'.format(self.name, self.type), end='\n\n')

        return mod_text


# Методы обработки текста

# Методы, относящиеся к исправлению ошибок распознования текста

def _speller(text):
    """ Создает обработчик текста,
        объект необходим для работы с Яндекс.спеллером

    """
    speller = pyaspeller.YandexSpeller(lang='en', find_repeat_words=False, ignore_digits=True)

    return speller.spell(text)
    
def spell_text(_work_file):
    """ Исправляет ошибки распознования текста (в виде разчлененных слов).
        На вход принимает объект work_file().
        Возвращает текст построчно в виде list'а

    """
    print('\nПриступаю к исправлению ошибок распознования (разчлененных слов) в тексте из файла {}.{} \n'.format(_work_file.name, _work_file.type))

    spelled_text = []

    for string in tqdm(_work_file.text, desc='Прогресс обработки текста '):

        if re.search(r'\S', string) != None:

            for i in _speller(string):

                if isinstance(i, dict) and ' ' in i['word']:

                    pattern = r'[a-z]+\s[a-z]+'

                    if re.search(pattern, i['word']) != None:

                        string = re.sub(i['word'], i['s'][0], string)

        spelled_text.append(string)

    print('\nОшибки распознования в тексте из файла {}.{} исправлены \n'.format(_work_file.name, _work_file.type))

    return spelled_text


# Методы, относящиеся к замене аббривиатур в тексте

def ABBREVS_to_termins(_work_file):
    """
    Интерфейс декодера аббривиатур в термины. Декодер находит все аббривеатуры в тексте,
    затем находит соответствующие им термины, а потом заменяет те аббревиатуры,
    которым был найден соответствующий термин. Алгоритм не идеален, не всегда находит все аббревиатуры,
    не всегда подбирает правильные термины к аббревиатурам.
    Возвращает измененный текст. В настоящий момент умеет работать только с текстами,
    напечатанными латинскими буквами. 
    """
    ABBREVS = _ABBREV_parser(_work_file)
    ABBREVS_and_termins = _ABBREV_and_termin(_work_file, ABBREVS)
    changed_text = _change_ABBREVS_on_termins(_work_file, ABBREVS_and_termins)
    return changed_text

def _ABBREV_parser(_work_file):
    """ Находит аббревеатуры в тексте, сохраняет их в список, возврящает получившийся список. 
        На вход подается объект класса work_file.
    """
    print('\nПриступаю к поиску аббревиатур в тексте из файла {}.{} \n'.format(_work_file.name, _work_file.type))
    ABBREVS = []
    for string in tqdm(_work_file.text, desc='Прогресс обработки текста '):
        pattern = r'\([A-Z]{2,8}\)'
        ABBREV = re.findall(pattern, string)
        ABBREVS.extend(ABBREV)

    print('\nПоик аббревеатур в файле {}.{} закончен, найдено {} аббревеатур \n'.format(_work_file.name, _work_file.type, len(ABBREVS)))

    return ABBREVS

def _ABBREV_and_termin(_work_file, ABBREVS: list):
    """ Выделяет из текста термины, соответствующие аббревеатурам, 
        результат сохраняет в виде словаря по форме АББРЕВЕАТУРА: значение,
        на вход подается объект класса work_file и список аббревеатур 
        возвращает получившийся словарь.
    """
    termins = dict()
    text = ''.join(_work_file.text)

    print('\nПриступаю к поиску терминов, соответствующих найденным аббревиатурам \n')

    for i in ABBREVS:
        ABBREV = i[1:-1]
        pattern = r'('
        n = 0
        for symbol in ABBREV:
            suff = r'([Ii]s\s)?([Ff]or\s)?([Oo]f\s)?([Tt]he\s)?(in\s)?(and\s)?'
            n += 1
            if n == 1:
                pattern += r'(\"|\')?' + suff + r'(\b((?i)' + symbol + r')[\S]+)\s'
            else:
                pattern += suff + r'(((\b((?i)' + symbol + r')[\S]+)\s)|' + r'((\b[\S]+' + symbol + r'[\S]+)\s)|' + r'((\b[\S]+)\s))?'
        pattern += r'\(' + ABBREV + r'\))'
        termin = re.findall(pattern, text)
        termins[ABBREV] = termin

    for key, value in termins.items():
        pattern = r'\(' + key + r'\)'
        if value != []:
            clear_termin = re.sub(pattern, '', value[0][0]).rstrip()
            clear_termin = re.sub(r'[\S\s]+[),:;]', '', clear_termin).strip()
            clear_termin = re.sub(r'\'|\"', '', clear_termin).strip()
            clear_termin = re.sub(r'^the\s|^of\s|^is\s|^for\s|^and\s|^in\s', '', clear_termin).strip()
            clear_termin = re.sub(r'^the\s|^of\s|^is\s|^for\s|^and\s|^in\s', '', clear_termin).strip()
            termins[key] = clear_termin

    yes_termins = 0
    no_termins = 0
    for value in termins.values():
        if value != [] and value != '' and value != ' ':
            yes_termins += 1
        else:
            no_termins += 1
    
    print('\nПоиск терминов завершен. Найдено {} соответстветствующих терминов. У {} аббревеатур не найдено соответствий. \n'.format(yes_termins, no_termins))
    
    return termins

def _change_ABBREVS_on_termins(_work_file, termins: dict):
    """ Заменяет в тексте аббревеатуры на термины.
        На вход принимает объект типа work_file и словарь по форме АББРЕВЕАТУРА: значение.
        Возвращает исправленный текст в виде списка строк.
    """
    text = ''.join(_work_file.text)

    print('\nПриступаю к замене аббревиатур в тексте на термины \n')

    for ABBREV, termin in termins.items():
        if termin != [] and termin != '' and termin != ' ':
            text = re.sub(ABBREV, termin, text)

    text = [i + '\n' for i in text.split('\n')]

    print('\nЗамена аббревиатур в тексте из файла {}.{} завершена \n'.format(_work_file.name, _work_file.type))

    return text


# Методы перевода текста

def google_translate_text(_work_file, out_lang = 'ru'):
    """ Переводит текст с использованием Гугл переводчика.
        Принимает на вход объект класса work_file и "флаг" языка, на который будет осуществлятся перевод.
        Исходный язык определяется автоматически на сервере Гугл переводчика.
        По умолчанию язык перевода - русский.
        Возвращяет переведенный текст в виде списка строк.
        Так как метод работает не через API, а имитирует реального пользователя, переодически google выдает бан на ip,
        бан обходим путем смены ip по средствам Tor браузера, который должен быть запущен во время работы скрипта.
    """

    socks.set_default_proxy(socks.SOCKS5, "localhost", 9150) #нужен для смены ip - это необходимо для обхода бана от google переводчика, возникающего из за множества запросов
    socket.socket = socks.socksocket                         #для правильной работы нужен запущенный Tor браузер  

    translated_text = []
    _translator = Translator()

    print('\nПриступаю к переводу текста \n')

    for string in tqdm(_work_file.text, desc='Прогресс обработки текста '):
        if re.search(r'\S', string) != None:
            cykle = "yes"
            while cykle == "yes":
                try:
                    translation = _translator.translate(string, dest=out_lang)
                    string = translation.text + '\n\n'
                    cykle = "no"
                except Exception as error:
                    # Выделить этот блок обработки исключенияй в отдельную фунцию

                    x = len(string)

                    # У google переводчика есть ограничение на перевод текста, он должен содержать не более 5000 тыс символов,
                    # если перевидимый кусок текста больше - его нужно разбить на меньшие куски. Сейчас разбиваю грубо, 
                    # как правило теряется слово и разбивается предложение, нужно сделать более
                    if x < 4000:
                        print('\nВозникла ошибка', error, ', жду 10 секунд и возобновляю работу')
                        time.sleep(10)
                        # Пересоздаю сокет
                        socks.set_default_proxy(socks.SOCKS5, "localhost", 9150) 
                        socket.socket = socks.socksocket 
                        # Вывожу на печать текущий ip
                        ip = requests.get('http://checkip.dyndns.org').content
                        soup = BeautifulSoup(ip, 'html.parser')
                        print(soup.find('body').text)

                    else:
                        strings = [string[:3000], string[3000:]]
                        for st in strings:
                            cy = 'yes'
                            while cy == 'yes':
                                try:
                                    translation = _translator.translate(st, dest=out_lang)
                                    st = translation.text + '\n\n'
                                    translated_text.append(st)
                                    cy = 'no'
                                except Exception as error:
                                    print('\nВозникла ошибка', error, ', жду 10 секунд и возобновляю работу')
                                    time.sleep(10)
                                    socks.set_default_proxy(socks.SOCKS5, "localhost", 9150) 
                                    socket.socket = socks.socksocket 

                        cykle = 'no'
                        string = '\n'
                                
        translated_text.append(string)

    print('\nПеревод текста из файла {}.{} завершен \n'.format(_work_file.name, _work_file.type))

    return translated_text

def yandex_translate_text(_work_file, out_lang = 'ru'):
    """ Переводит текст с использованием Яндекс переводчика через API.
        Принимает на вход объект класса work_file и "флаг" языка, на который будет осуществлятся перевод.
        Исходный язык определяется автоматически на сервере переводчика.
        По умолчанию язык перевода - русский.
        Возвращяет переведенный текст в виде списка строк.
    """
    translated_text = []
    _translator = YandexTranslate('trnsl.1.1.20190309T225837Z.98217cfce0c89cbe.5436b7fe2c5f1c7c2acc266ad4c2f0095a9634a2')

    print('\nПриступаю к переводу текста \n')

    for string in tqdm(_work_file.text, desc='Прогресс обработки текста '):
        if re.search(r'\S', string) != None:
            translation = _translator.translate(string, out_lang)
            string = translation['text'][0]
        translated_text.append(string)

    print('\nПеревод текста из файла {}.{} завершен \n'.format(_work_file.name, _work_file.type))

    return translated_text


def google_translate_text2(_work_file, in_lang = 'en', out_lang = 'ru'):
    """ Переводит текст с использованием API Гугл переводчика.
        Принимает на вход объект класса work_file и "флаг" языка, на который будет осуществлятся перевод.
        Исходный язык определяется автоматически на сервере Гугл переводчика.
        По умолчанию язык перевода - русский.
        Возвращяет переведенный текст в виде списка строк.
    """
    translated_text = []

    _translator = build('translate', 'v2',
                        developerKey='AIzaSyCyXVxLd1Fa4Cb83UF4fiR_MYQjIqG_HR8')

    for string in tqdm(_work_file.text, desc='Прогресс обработки текста '):
        if re.search(r'\S', string) != None:                        
            string = _translator.translations().list(
                source=in_lang,
                target=out_lang,
                q=string
                ).execute()
        translated_text.append(string)

    print('\nПеревод текста из файла {}.{} завершен \n'.format(_work_file.name, _work_file.type))

    return translated_text


if __name__ == '__main__':
    main()