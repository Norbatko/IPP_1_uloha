# Implementační dokumentace k 2. úloze IPP 2023
* Jméno a příjmení: Tomáš Ebert
* Login: xebert00

Zadaním byla implementace skriptu v jazyce Python. Skript načítá XML soubor, zkontroluje jeho validitu a provede dané příkazy.

## Kostra skriptu
Skript nejdříve zkontroluje zadané parametry a případně vypíše nápovědu s ukázkou použití. Dále taky zkontroluje validitu souborů (zda k nim má přístup, existenci souboru). \
Následně už probíhá načtení samotného XML. Zkontroluje, zda je validní XML formát a pokud ano, pokračuje v načítaní a kontrole jednotlivých částí XML. \
Zavolá si funkci `tree_check`, která přijímá root daného XML a zkontroluje jeho parametry. Dále zkontroluje, zda order je číslo větší než 0 a zda neobsahuje duplicity. To stejné provede i s argumenty a každé instrukce. \
Při úspěšné kontrole skript pokračuje načtením všech instrukcí, které si postupně vkládá do listu a seřazuje podle jejich hodnoty ORDER. Po načtení si vkládá do zásobníku návěští hodnotu návěští, pokud se se jedná o instrukci LABEL, nebo hodnotu None, pokud to je jiná instrukce. Slouží to pro lehčí skákání na návěští, kdy dané návěští uložené v zásobníku odpovídá pozici LABEL instrukci v listu instrukcí.
Následně už celý děj probíhá v nekonečném cyklu, který je ukončen při projití celého listu instrukcí. Porovnává hodnotu opcode dané instrukce a v případě shody provede danou instrukci.
Zavolá si metodu pro kontrolu počtu argumentů, které je vložen očekávaný počet argumentů. Následně při úspěchu proběhne kontrola, zda argumenty jdou popořadě a nezačíná například až od argumentu 2. Proběhne také kontrola, zda argumenty odpovídají očekávaným typům.
Poté už proběhne provedení dané instrukce a kontrola určitých případů v rámci dané instrukce.
Mezi hlavní funkce skriptu patří `get_item_from_frame` a `push_item_to_frame`. První funkce očekává jako argumenty (první argument instrukce, pozici, očekávaný typ, globální rámec, lokální rámce, dočasný rámec). Získá hodnotu z argumentu a porovná s očekávaným typem. Vrací dvojici (typ, hodnota). Pokud je zadána pozice, tak vrací znak na pozici. Druhá funkce očekává jako argumenty (první argument instrukce, typ, hodnota, pozice, globální rámec, lokální rámce, dočasný rámec). Vloží do rámce proměnnou nebo do proměnné dvojici (typ, hodnota). Pokud je zadána pozice, tak vloží danou hodnotu na pozici.

## Třídy

### Local frame
Třída, která obsahuje všechny lokální rámce. Jsou uloženy v listu, kde každý lokální rámec je uložen jako slovník.
Obsahuje metody:

- init(self) = vytvoří prázdný list pro lokální rámce
- get_LF(self) = vrátí list lokálních rámů
- create_LF_dict(self) = vytvoří prázdný slovník, který vloží na konec listu
- push_new_LF(self, frame) = vloží rámec `frame` na konec listu
- def_LF(self, var) = zkontroluje, jestli už není proměnná `var` v lokálním rámci definovaná, jinak vrací chybu; definuje novou proměnnou `var` v lokálním rámci
- push_LF(self, var, arg_type, value) = zkontroluje, jestli proměnná `var` v lokálním rámci existuje, jinak vrací chybu; vloží proměnné `var` v lokálním rámci dvojici (arg_type, value)
- pop_LF(self) = zkontroluje, zda v listu existuje lokálním rámec, jinak vrací chybu; vrátí lokální rámec a odstraní ho z listu lokálních rámců
- get_item(self, var) = zkontroluje, jestli proměnná `var` v lokálním rámci existuje, jinak vrací chybu; vrátí hodnotu proměnné `var`
- get_type(self, var) = zkontroluje, jestli proměnná `var` v lokálním rámci existuje, jinak vrací chybu; vrátí typ proměnné `var`

### Instruction
Třída, pro danou instrukci.
Obsahuje metody:

- init(self, opcode, order) = přiřadí instrukci název `opcode`, pořadí `order` a list jejích argumentů (prázdný)
- add_arguments(self, num, arg_type, value) = přidá do listu argument, který je vytvořen pomocí konstruktoru třídy Argument; do argumentu je přirazeno jeho číslo `num`, typ `arg_type` a hodnota `value`; následně v listu jsou argumenty seřazeny podle čísla argumentů, které získáme pomocí metody z třídy Argument (`get_num()`)
- get_opcode(self) = vrací název instrukce
- get_order(self) = vrací pořadí instrukce
- check_num_args(self, num_args) = zkontroluje počet argumentů se zadaným "očekávaným" počtem argumentů `num_args`, jinak vrací chybu
- check_valid_num_args(self, num_args) = zkontroluje, zda je jsou argumenty číslovány od 1 až po `num_args`, jinak vrací chybu
- get_args(self) = vrací list argumentů instrukce

### Argument
Třída, pro daný argument.
Obsahuje metody:
- init(self, num, arg_type, value) = přiřadí instrukci číslo `num`, typ `arg_type` a jeho hodnotu `value`
- get_num(self) = vrací číslo argumentu
- get_arg_type(self) = vrací typ argumentu
- get_value(self) = vrací hodnotu argumentu

## UML diagram
<br>
![UML](https://user-images.githubusercontent.com/98109213/232227091-b19d0feb-ea1c-40c7-aa73-b598ab8d14f3.png)
<p style="text-align: center;"><b>Obrázek č. 1 - UML diagram</b></p>
