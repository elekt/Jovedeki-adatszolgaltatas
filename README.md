# Jövedéki adatszolgáltatás generáló
Ez a program a “A Nemzeti Adó- és Vámhivatal által kiadott 4006/2017. tájékoztatás a jövedéki engedélyes kereskedő által teljesítendő adatszolgáltatás műszaki követelményeiről” dokumentum (4006_2017.pdf -ként csatolva) alapján formailag helyes jövedéki adatszolgáltatás fájlokat generál, a csatolt táblázatok alapján (fejlec.csv, tetelek.csv)

A program futtatásához Python 2.7 szükséges,hogy telepítve legyen és a PATH változók közé fel legyen véve.

## Windows 

Letöltés:
https://www.python.org/download/releases/2.7/

A telepítőn végighaladva ennél a képernyőnél fontos, hogy a bekarikázott jel hozzá legyen adva:

![Adding to path](https://realpython.com/learn/python-first-steps/images/msi_install_path.png)

Telepítés után a “jovedeki_adatszolgaltatas_generalas.bat” fájlt futtatva generálhat új jövedéki adatszolgáltatást.

## Linux / Mac OS

Python ezekre a rendszerekre előre telepítve szokott lenni. Amennyiben nem:
Linux: sudo apt-get install python
Mac OS: brew install python
Parancsokkal illetve a fenti oldalról letöltve lehet telepíteni.

Futtatáshoz lépjünk a program könyvtárába majd: “python main.py”-t futtassunk. 

## Használat 
A program abban a mappában keresi a szükséges fájlokat ahonnan futtatva lett. Ezért kérem együtt mozgassa őket, illetve a fájlokat ne nevezze át.

### MAIN.PY
A futtatandó állomány. A CONFIG.TXT, FEJLEC.CSV és TETELEK.CSV fájlok alapján generálja le az adatszolgáltatást.

### CONFIG.TXT
Minta (ha elromolna ezzel felülírható):

	telephely_engedely:HU12345603001
	utolso_adat_osszehasonlitas_idoszaka:1701
	adatallomany_sorszama:00
	output_directory:not_set

telephely_engedely – a telephely engedély száma (13 hosszon)

utolso_adat_osszehasonlitas_idoszaka – automatikusan állítja az adatösszehasonlítás idejét. Ha más időpontra kell kiállítani mint az aktuális, nyugodtan át lehet írni az elkészült fájl nevében a 15.-18. karaktereket (ÉÉHH formátum)

adatallomany_sorszama – automatikusan állítja az adatösszehasonlítás sorszámát. Ha egy hónapban többször is generálna/feltöltene ez jelzi hogy különbözik az előzőtől. Hónap végén automatikusan 00-zódk. Ha más sorszámot adna mint a generáltban van, nyugodtan át lehet írni az elkészült fájl nevében a 19.-20. karaktereket (00-ZZ bármi lehet, csak mindig különbözőt kell feltölteni.)

output_directory – megadható bármely a felhasználó által írható/olvasható mappa. Ha marad a “not_set” érték, akkor a program mapáján belül létrejön egy “documents” mappa oda menti.

### FEJLEC.CSV
1 sorral kitöltendő táblázat. 

A Fejadatok 5-10. rovatát abban az esetben kötelező kitölteni, ha a 11. rovatban 1-es vagy 2-es érték szerepel és az üzemanyag értékesítése nem magánszemély részére történt.

A Fejadatok 6. rovatában az adószámot 8 karakter hosszon kell feltüntetni, ha az adott rovatba magyar adószámmal rendelkező vevő/címzett kerül rögzítésre. Harmadik országos vagy tagállami vevő/címzett esetén a rovatba „00000000”-át kell írni.

A Fejadatok 7. rovatában dohány kiskereskedelmi engedélyszámmal rendelkező vevő/címzett ”DKE”-vel kezdődő engedélyszámát 13 karakter hosszan kell rögzíteni. A rovat kitöltésére kizárólag akkor kerülhet sor, ha a 11. rovatban 1-es érték szerepel.

A Fejadatok 8. rovatában harmadik országos vagy tagállami vevő/címzett esetén az irányítószám helyett „0000”-t kell szerepeltetni.

A Fejadatok 11. rovat értéke az alábbi lehet:

1. Belföldre kiszállítás
2. Tagállamba kiszállítás
3. Exportra kiszállítás
4. Légiutas-ellátási tevékenységhez kiszállítás.

### TETELEK.CSV
Az adatszolgáltatás során a tételadatoknál kizárólag jövedéki termékek kerülhetnek rögzítésre.

A Tételadatok 5. rovatában a mennyiséget a 6. rovat szerinti mennyiségi egységben kell megadni.

A Tételadatok 6. rovatában mennyiségi egységként alkoholtermék, sör, csendes és habzóbor, köztes alkoholtermék, valamint egyéb csendes és habzó erjesztett ital esetében a „DB” rövidítést (darab) kell feltüntetni. Energiatermékek esetében a mennyiségi egység feltüntetésére az „L” (liter), a „KG” (kilogramm) vagy az „M3” (köbméter), dohánygyártmányok esetében pedig minden esetben a „DB” rövidítés alkalmazandó. A mennyiségi egység rovatban az előbbiektől eltérő rövidítések nem alkalmazhatóak.

A Tételadatok 7. rovatát nem kell kitölteni energiatermékek tekintetében. Egyébként a 7. rovatban a kiszerelés típusaként

a) alkoholtermék, sör, csendes és habzóbor, köztes alkoholtermék, valamint egyéb csendes és habzó erjesztett ital esetén az egy darabban (palack, doboz, stb.) lévő űrtartalmat literben, legfeljebb három tizedesjegy pontossággal,

b) dohánygyártmányok esetében a csomagban, dobozban található darabszámot,     illetve finomra vágott és egyéb fogyasztási dohány esetében az egy csomagban lévő tömeget kilogrammban, legfeljebb három tizedesjegy pontossággal kell megadni.

A Tételadatok 8. rovatát csak alkoholtermékek és sör esetében kötelező kitölteni, a termék alkoholfokának térfogatszázalékban való feltüntetésével.

A Tételadatok 5., 7. és 8. rovatában a tizedes törtek egész és tört részének elválasztására tizedesjelként kizárólag pont alkalmazható.

Sztornózott bizonylat esetén a Fejadatok 12. rovatában, valamint a Tételadatok 2. rovatában a sztornózásról kiállított bizonylat száma, míg a Tételadatok 5. rovatában negatív értékek kell, hogy szerepeljenek. A negatív előtag alkalmazása az utóbbi rovatoknál előírt maximális hossz kitöltését nem befolyásolja.

Termék visszaszállításával járó sztornózás esetében a Fejadatok 13. rovatában a visszaszállítás, egyéb esetben a sztornózásról kiállított bizonylat kiállításának dátumát kell szerepeltetni.
