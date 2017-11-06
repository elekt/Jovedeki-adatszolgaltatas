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

                # Jövedéki engedélyes adószáma
                headers += row[1]
                headers += char_pipe
                # Jövedéki engedélyes engedélyszáma
                headers += row[2]
                headers += char_pipe
                # Vevő vagy címzett neve
                headers += row[3]
                headers += char_pipe
                # Vevő vagy címzett adószáma
                if row[4] == '0':
                    headers += '00000000'
                else:
                    headers += row[4]
                headers += char_pipe
                # Dohánygyártmány esetén a jövedéki kiskereskedő működési
                # engedélyszáma, nyilvántartásba vételi száma vagy dohány
                # kiskereskedelmi engedélyszáma
                if row[9] == '1':
                    headers += row[5]
                headers += char_pipe
                # Vevő vagy címzett irányítószám
                if row[6] == '0':
                    headers += '0000'
                else:
                    headers += row[4]
                headers += char_pipe
                # Vevő vagy címzett település
                headers += row[7]
                headers += char_pipe
                # Vevő vagy címzett utca és házszám
                headers += row[8]
                headers += char_pipe
                # Forgalom típusa
                if not row[9] in ['1', '2', '3', '4']:
                    print("{} HIBA: lehetséges forgalom típusok: \n1 = Belföldre kiszállítás \n2 = Tagállamba kiszállítás \n3 = Exportra kiszállítás \n4 = Légiutas - ellátási tevékenységhez kiszállítás.".format(row[4]))
                    exit(1)
                    
                headers += row[9]
                headers += char_pipe
                # Szállítólevél, EKO vagy egyéb a kitárolásról szóló bizonylat
                # száma
                headers += row[10]
                id_numbers.append(row[10])
                headers += char_pipe
                # Szállítólevél, EKO vagy egyéb a kitárolásról szóló bizonylat kelte
                # (ÉÉÉÉHHNN)
                headers += row[11]
                headers += char_pipe
                # Kiszállítás időpontja (ÉÉÉÉHHNN)
                headers += row[12]

                headers += char_new_line

            row_num += 1
    return headers.encode('iso-8859-2').splitlines(), id_numbers


def generate_data():
    (headers, id_numbers) = generate_headers()

    # initialize temporary data storage, where they are separeatd by id (bizonylatszám)
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

                # Szállít   ólevél, EKO vagy egyéb a kitárolásról szóló bizonylatszáma
                data += row[0]
                current_id = row[0]
                if current_id not in id_numbers:
                    print("Adatsor bizonylatszámához nem tartozik fejadat. program befejezésre kerül.")
                    exit(1)
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

                data_id_storage[current_id] += data

            row_num += 1

        if row_num == 1:
            print("Egy tétel sem található a tetelek.csv fájl-ban.")
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


