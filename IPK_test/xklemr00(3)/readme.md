# IPK projekt 1 - HTTP resolver doménových jmen
## Obecné informace
Autor: Richard Klem<br>
Login: xklemr00<br>
Email: xklemr00@stud.fit.vutbr.cz<br>
<br>
Jazyk: Python<br>
Verze jazyka: 3.6.9<br>

## Prerekvizity
Python 3.6.9<br>
GNU make<br>

## Spuštění
`make run PORT=XYZ`

kde `XYZ` značí celé číslo portu, který má skript server.py obsluhovat<br>
implicitní hodnota proměnné PORT je rovna 5353

## Podporované operace
### Upozornění
Část **_Podporované operace_** částečně opakuje zadání projektu, avšak <br>
původní text je parafrázován a hojně doplněn o popis mé vlastní implementace<br>
případů, stavů, možností apod., které nebyli v zadání specifikovány.<br>
Je tedy důležité, přečíst si popis mojí implementace, pro správné<br>
pochopení, jak konkrétně moje implementace serveru funguje a jaké jsou<br>
doplňující požadavky, rozšíření a omezení na práci se serverem.
### GET<br>
Přeloží právě jeden dotaz, který je specifikován jako parametr URL požadavku,<br>
například:
 
`GET /resolve?name=apple.com&type=A HTTP/1.1`

Povinně je nutné dodržet formát po částech následovně:<br>
`GET /resolve?name=`, `&type=` a `HTTP/1.1`<br>
Za `name=` a `type=` může následovat libovolná posloupnost znaků.

parametry jsou povinně právě tyto dva:<br>
`name` = doménové jméno anebo IPv4 adresa<br>
`type` = typ požadované odpovědi (_A_ nebo _PTR_)<br> 

Odpovědí je právě jeden řádek formátu:<br>
`DOTAZ:TYP=ODPOVED`

Například:<br>
`apple.com:A=17.142.160.59`

V případě nalezení odpovědi se vrací _status code_ `200 OK` a přeložená<br>
odpověď.<br>
Není-li odpověď nalezena, vrací se _status code_ `404 Not Found`.<br>
Je-li zadán některý parametr chybně nebo chybí, vrací se  _status code_<br>
`400 Bad Request`.

### POST<br>
Metoda **POST** obsahuje v těle požadavku seznam dotazů, každý musí být<br>
na samostatném řádku. Seznam nesmí být proložen žádnými prázdnými řádky<br>
ani jimi nesmí začínat. Na konci seznamu je povoleno jedno odřádkování.<br>
Tedy na konci řádku, na kterém se nachází poslední dotaz je povolen<br>
jeden bílý znak `\n`.<br>

Řádek požadavku je povinně:<br> 
`POST /dns-query HTTP/1.1`

Řádek v těle obsahující jeden dotaz má formát:<br>
`DOTAZ:TYP`

kde:<br>
`DOTAZ` - doménové jméno nebo IP adresa<br>
`TYP` - typ požadované odpovědi (_A_ nebo _PTR_)<br> 

Například:
```
www.fit.vutbr.cz:A
apple.com:A
147.229.14.131:PTR
seznam.cz:A
```

V případě, že pro alespoň jeden požadavek byla nalezena odpověď,<br>
je výsledkem _status code_ `200 OK` a seznam odpovědí. <br>

V případě, že pro konkrétní dotaz nebyla nalezena odpověď, je tento<br>
požadavek ignorován.

V případě, že z celého seznamu dotazů se nepodařilo přeložit ani jeden<br>
dotaz, je navrácen _status code_ `400 Bad Request` pokud alespoň jeden<br>
příkaz implikoval tento _status code_. V situaci, kdy se nepodařilo<br>
přeložit ani jeden dotaz, ale žádný neskončil se _status code_<br>
 `400 Bad Request`, je navrácen _status code_ `404 Not Found`.
 
V případě, že se prázdný řádek vyskytl na začátku nebo uprostřed<br>
seznamu dotazů nebo za posledním(mimo jeden povolený) dotazem v seznamu<br>
dotazů, je navrácen _status code_ `400 Bad Request` a to **bez seznamu<br>
odpovědí**!
 
 
 ## Popis průběhu programu
 Skript namapuje server na zadanou nebo implicitní hodnotu portu.<br>
 Na tomto portu bude server běžet dokud ho uživatel neukončí pomocí<br>
 signálu SIGINT napřílad pomocí "_Ctrl + C_".<br>
 Program sestává z jedné funkce, v které běží v nekonečné smyčce, kde<br>
 čeká na příchozí soket, který zpracuje se souladem s popisem v části<br>
 **_Podporované operace_** a následně je připraven na přijmutí dalšího<br>
 soketu.