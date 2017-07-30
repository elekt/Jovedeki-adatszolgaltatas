#!/usr/bin/python
# -*- coding: iso-8859-2 -*-
import csv
import codecs
import sys
import datetime
import os

config = dict()

char_pipe = chr(124)
char_new_line = chr(10) + chr(13)

reload(sys)
sys.setdefaultencoding('ISO-8859-2')

def parse_config_file():
    with open("config.txt", 'r') as f:
        config_lines = f.readlines()

    for line in config_lines:
        splitted_line = line.split(':')
        if len(splitted_line) == 2:
            config[splitted_line[0]] = splitted_line[1].rstrip('\n')


def overwrite_config_file():
    with open("config.txt", 'r+') as f:
        for (key, value) in config.iteritems():
            f.write("{}:{}\n".format(key, value))


def generate_file_name():
    filename = "J"
    extension = ".vny"

    if "telephely_engedely" in config:
        filename += config["telephely_engedely"]
    else:
        print("A telephely engedély száma (13 karakter) hiányzik a konfigurációs fájlból")
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
            print("Az sorszáma (00-99) hiányzik a konfigurációs fájlból")
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
        print("Az adat összehasonlítás időszaka (ÉÉHH) hiányzik a konfigurációs fájlból")
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
                print("Hibás kimeneti mappa. Jelen munkakönyvtárban hozom létre a fájlt.")
                return os.getcwd()
    else:
        if os.path.isdir(os.path.join(os.getcwd(), "documents")):
            return os.path.join(os.getcwd(), "documents")
        else:
            try:
                os.makedirs(os.path.join(os.getcwd(), "documents"))
                return os.path.join(os.getcwd(), "documents")
            except OSError as exception:
                print("Hibás kimeneti mappa. Jelen munkakönyvtárban hozom létre a fájlt.")
                return os.getcwd()


def generate_header():
    header = "VF" + char_pipe

    with codecs.open('fejlec.csv', 'r', 'ISO-8859-2') as csvfile:
        row_num = 0
        header_reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        for row in header_reader:
            # the row contains the data. using the line_num of the reader is not safe, since inserting \n in the header
            # can change the starting number
            if row_num == 1:
                # add version
                header += row[0]
                header += char_pipe

                # Jövedéki engedélyes adószáma
                header += row[1]
                header += char_pipe
                # Jövedéki engedélyes engedélyszáma
                header += row[2]
                header += char_pipe
                # Vevő vagy címzett neve
                header += row[3]
                header += char_pipe
                # Vevő vagy címzett adószáma
                header += char_pipe
                header += row[4]
                # Dohánygyártmány esetén a jövedéki kiskereskedő működési
                # engedélyszáma, nyilvántartásba vételi száma vagy dohány
                # kiskereskedelmi engedélyszáma
                header += row[5]
                header += char_pipe
                # Vevő vagy címzett irányítószám
                header += row[6]
                header += char_pipe
                # Vevő vagy címzett település
                header += row[7]
                header += char_pipe
                # Vevő vagy címzett utca és házszám
                header += row[8]
                header += char_pipe
                # Forgalom típusa
                if not row[9] in ['1', '2', '3', '4']:
                    print("{} HIBA: lehetséges forgalom típusok: \n1 = Belföldre kiszállítás \n2 = Tagállamba kiszállítás \n3 = Exportra kiszállítás \n4 = Légiutas - ellátási tevékenységhez kiszállítás.".format(row[4]))
                    exit(1)
                    
                header += row[9]
                header += char_pipe
                # Szállítólevél, EKO vagy egyéb a kitárolásról szóló bizonylat
                # száma
                header += row[10]
                header += char_pipe
                # Szállítólevél, EKO vagy egyéb a kitárolásról szóló bizonylat kelte
                # (ÉÉÉÉHHNN)
                header += row[11]
                header += char_pipe
                # Kiszállítás időpontja (ÉÉÉÉHHNN)
                header += row[12]

                header += char_new_line

            row_num += 1
    return header.encode('iso-8859-2')


def generate_data():
    with codecs.open('tetelek.csv', 'r', 'ISO-8859-2') as csvfile:
        row_num = 0
        data_reader = csv.reader(csvfile, delimiter=';', quotechar='"')
        data = ""
        for row in data_reader:
            # the rows that contains the data. using the line_num of the reader is not safe, since inserting \n in the
            # data can change the starting number
            if row_num >= 1:
                data += "VT" + char_pipe

                # Szállítólevél, EKO vagy egyéb a kitárolásról szóló bizonylatszáma
                data += row[0]
                data += char_pipe

                # Értékesített termék KN-kódja [1-8 számjegyig]
                data += row[1]
                data += char_pipe

                # Értékesített termék megnevezése
                data += row[2]
                data += char_pipe

                # Értékesített termék mennyisége
                # [(negatív előjel opcionális) 12 egész és 2 tizedes, ponttal
                # elválasztva]
                data += row[3]
                data += char_pipe

                # Értékesített termék mennyiségi egysége
                if not row[4] in ['DB', 'L', 'KG', 'M3']:
                    print("HIBA: lehetséges mennyiségi egységek: 'DB', 'L', 'KG', 'M3'")
                    exit(1)
                    
                data += row[4]
                data += char_pipe

                # Értékesített termék kiszerelésének típusa
                # [4 egész és 3 tizedes, ponttal elválasztva]
                data += row[5]
                data += char_pipe

                # Alkoholtermék/sör alkoholfoka (%)
                # [3 egész és 2 tizedes, ponttal elválasztva]
                data += row[6]

                data += char_new_line

            row_num += 1

        if row_num == 1:
            print("Egy tétel sem található a tetelek.csv fájl-ban.")
            exit(1)

    return data.encode('ISO-8859-2')


parse_config_file()

with codecs.open(os.path.join(get_output_directory(), generate_file_name()), "w", "ISO-8859-2") as f:
    f.write((generate_header() + generate_data()).encode('ISO-8859-2'))


