#!/usr/bin/python
# -*- coding: iso-8859-2 -*-
import csv
import codecs
import sys
import datetime
import os

config = dict()

char_pipe = chr(124)
char_new_line = "\r\n"

reload(sys)
sys.setdefaultencoding('ISO-8859-2')

def parse_config_file():
    with open("config.txt", 'r') as f:
        config_lines = f.readlines()

    for line in config_lines:
        splitted_line = line.split('#')
        if len(splitted_line) == 2:
            config[splitted_line[0]] = splitted_line[1].rstrip('\n')


def overwrite_config_file():
    with open("config.txt", 'r+') as f:
        for (key, value) in config.iteritems():
            f.write("{}#{}\n".format(key, value))


def generate_file_name():
    filename = "J"
    extension = ".vny"

    if "telephely_engedely" in config:
        filename += config["telephely_engedely"]
    else:
        print("A telephely enged�ly sz�ma (13 karakter) hi�nyzik a konfigur�ci�s f�jlb�l")
        exit(1)

    if "utolso_adat_osszehasonlitas_idoszaka" in config:
        last_date = config["utolso_adat_osszehasonlitas_idoszaka"]

        now = datetime.datetime.now()
        year = now.year - 2000
        month = now.month

        filename += '{0:02d}'.format(year)
        filename += '{0:02d}'.format(month)

        last_year = int(last_date[:2])
        last_month = int(last_date[2:])

        if not ("adatallomany_sorszama" in config):
            print("Az sorsz�ma (00-99) hi�nyzik a konfigur�ci�s f�jlb�l")
            exit(1)

        document_id = '00'

        if last_year == year and last_month == month:
            # in this month we had an other generated file increment the id
            document_id = '{0:02d}'.format(int(config["adatallomany_sorszama"]) + 1)
            filename += document_id
        else:
            filename += config["adatallomany_sorszama"]

        config["utolso_adat_osszehasonlitas_idoszaka"] = '{0:02d}'.format(year) + '{0:02d}'.format(month)
        config["adatallomany_sorszama"] = document_id

    else:
        print("Az adat �sszehasonl�t�s id�szaka (��HH) hi�nyzik a konfigur�ci�s f�jlb�l")
        exit(1)

    overwrite_config_file()

    filename += extension
    return filename


def get_output_directory():
    if not config["output_directory"] == "not_set":
        if os.path.isdir(config["output_directory"]):
            return config["output_directory"]
        else:
            try:
                os.makedirs(config["output_directory"])
                return config["output_directory"]
            except OSError as exception:
                print("Hib�s kimeneti mappa. Jelen munkak�nyvt�rban hozom l�tre a f�jlt.")
                return os.getcwd()
    else:
        if os.path.isdir(os.path.join(os.getcwd(), "documents")):
            return os.path.join(os.getcwd(), "documents")
        else:
            try:
                os.makedirs(os.path.join(os.getcwd(), "documents"))
                return os.path.join(os.getcwd(), "documents")
            except OSError as exception:
                print("Hib�s kimeneti mappa. Jelen munkak�nyvt�rban hozom l�tre a f�jlt.")
                return os.getcwd()


def generate_headers():
    headers = ""
    id_numbers = []

    with codecs.open('fejlec.csv', 'r', 'ISO-8859-2') as csvfile:
        row_num = 0
        header_reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in header_reader:
            # the row contains the data. using the line_num of the reader is not safe, since inserting \n in the header
            # can change the starting number
            if row_num >= 1:
                headers += "VF" + char_pipe
                # add version
                headers += row[0]
                headers += char_pipe

                # J�ved�ki enged�lyes ad�sz�ma
                headers += row[1]
                headers += char_pipe
                # J�ved�ki enged�lyes enged�lysz�ma
                headers += row[2]
                headers += char_pipe
                # Vev� vagy c�mzett neve
                headers += row[3]
                headers += char_pipe
                # Vev� vagy c�mzett ad�sz�ma
                if row[4] == '0':
                    headers += '00000000'
                else:
                    headers += row[4]
                headers += char_pipe
                # Doh�nygy�rtm�ny eset�n a j�ved�ki kiskeresked� m�k�d�si
                # enged�lysz�ma, nyilv�ntart�sba v�teli sz�ma vagy doh�ny
                # kiskereskedelmi enged�lysz�ma
                if row[9] == '1':
                    headers += row[5]
                headers += char_pipe
                # Vev� vagy c�mzett ir�ny�t�sz�m
                if row[6] == '0':
                    headers += '0000'
                else:
                    headers += row[4]
                headers += char_pipe
                # Vev� vagy c�mzett telep�l�s
                headers += row[7]
                headers += char_pipe
                # Vev� vagy c�mzett utca �s h�zsz�m
                headers += row[8]
                headers += char_pipe
                # Forgalom t�pusa
                if not row[9] in ['1', '2', '3', '4']:
                    print("{} HIBA: lehets�ges forgalom t�pusok: \n1 = Belf�ldre kisz�ll�t�s \n2 = Tag�llamba kisz�ll�t�s \n3 = Exportra kisz�ll�t�s \n4 = L�giutas - ell�t�si tev�kenys�ghez kisz�ll�t�s.".format(row[4]))
                    exit(1)
                    
                headers += row[9]
                headers += char_pipe
                # Sz�ll�t�lev�l, EKO vagy egy�b a kit�rol�sr�l sz�l� bizonylat
                # sz�ma
                headers += row[10]
                id_numbers.append(row[10])
                headers += char_pipe
                # Sz�ll�t�lev�l, EKO vagy egy�b a kit�rol�sr�l sz�l� bizonylat kelte
                # (����HHNN)
                headers += row[11]
                headers += char_pipe
                # Kisz�ll�t�s id�pontja (����HHNN)
                headers += row[12]

                headers += char_new_line

            row_num += 1
    return headers.encode('iso-8859-2').splitlines(), id_numbers


def generate_data():
    (headers, id_numbers) = generate_headers()

    # initialize temporary data storage, where they are separeatd by id (bizonylatsz�m)
    data_id_storage = {}
    for id in id_numbers:
        data_id_storage[id] = ""

    with codecs.open('tetelek.csv', 'r', 'ISO-8859-2') as csvfile:
        row_num = 0
        data_reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in data_reader:
            # the rows that contains the data. using the line_num of the reader is not safe, since inserting \n in the
            # data can change the starting number
            if row_num >= 1:
                current_id = ""
                data = ""

                data += "VT" + char_pipe

                # Sz�ll�t   �lev�l, EKO vagy egy�b a kit�rol�sr�l sz�l� bizonylatsz�ma
                data += row[0]
                current_id = row[0]
                if current_id not in id_numbers:
                    print("Adatsor bizonylatsz�m�hoz nem tartozik fejadat. program befejez�sre ker�l.")
                    exit(1)
                data += char_pipe

                # �rt�kes�tett term�k KN-k�dja [1-8 sz�mjegyig]
                data += row[1]
                data += char_pipe

                # �rt�kes�tett term�k megnevez�se
                data += row[2]
                data += char_pipe

                # �rt�kes�tett term�k mennyis�ge
                # [(negat�v el�jel opcion�lis) 12 eg�sz �s 2 tizedes, ponttal
                # elv�lasztva]
                data += row[3]
                data += char_pipe

                # �rt�kes�tett term�k mennyis�gi egys�ge
                if not row[4].upper() in ['DB', 'L', 'KG', 'M3']:
                    print("HIBA: lehets�ges mennyis�gi egys�gek: 'DB', 'L', 'KG', 'M3'")
                    exit(1)
                    
                data += row[4].upper()
                data += char_pipe

                # �rt�kes�tett term�k kiszerel�s�nek t�pusa
                # [4 eg�sz �s 3 tizedes, ponttal elv�lasztva]
                data += row[5]
                data += char_pipe

                # Alkoholterm�k/s�r alkoholfoka (%)
                # [3 eg�sz �s 2 tizedes, ponttal elv�lasztva]
                data += row[6]

                data += char_new_line

                data_id_storage[current_id] += data

            row_num += 1

        if row_num == 1:
            print("Egy t�tel sem tal�lhat� a tetelek.csv f�jl-ban.")
            exit(1)

    final_data = ""

    for i in range(0, len(headers)):
        final_data += headers[i] + char_new_line
        final_data += data_id_storage[id_numbers[i]]

    return final_data.encode('ISO-8859-2')


parse_config_file()


data = (generate_data()).encode('ISO-8859-2')
with codecs.open(os.path.join(get_output_directory(), generate_file_name()), "w", "ISO-8859-2") as f:
    f.write(data)


