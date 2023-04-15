#################################
#       Autor:   Tomáš Ebert    #
#       xlogin:  xebert00       #
#       Projekt: Interpret      #
#################################

import re
import sys
import argparse
import xml.etree.ElementTree as ET
import os

# Trida pro lokalni ramce
class Local_frame:
    # Vytvoreni prazdneho listu ramcu
    def __init__(self):
        self.local_frame = []

    # Ziskani celeho listu lokalnich ramcu
    def get_LF(self):
        return self.local_frame

    # Vytvoreni jednoho ramce v ramci celem listu ramcu
    def create_LF_dict(self):
        self.local_frame.append({})

    # Vlozi cely ramec do listu
    def push_new_LF(self, frame):
        self.local_frame[-1] = frame

    # Definuje promennou v ramci
    def def_LF(self, var):
        # Otestuje, zda uz promenna existuje
        try:
            self.local_frame[-1][var]
        except:
            self.local_frame[-1][var] = None, None
            return
        sys.stderr.write("ERROR: Variable is already defined.\n")
        exit(52)

    # Vlozi do lokalniho ramce na pozici var dvojici (typ, hodnota)
    def push_LF(self, var, arg_type, value):
        # Pokud pozice var v ramci neexistuje, tak vrati chybu
        try:
            self.local_frame[-1][var]
        except:
            sys.stderr.write("ERROR: Variable doesn't exists.\n")
            exit(54)
        self.local_frame[-1][var] = arg_type, value

    # Vrati cely ramec a zaroven ho vymaze z listu lokalnich ramcu
    def pop_LF(self):
        try:
            return self.local_frame.pop()
        except:
            sys.stderr.write("ERROR: Empty local frame.\n")
            exit(55)

    # Ziskani hodnoty z lokalniho ramce
    def get_item(self, var):
        try:
            return self.local_frame[-1][var][1]
        except:
            sys.stderr.write("ERROR: Empty local frame.\n")
            exit(55)

    # Ziskani typu hodnoty z lokalniho ramce
    def get_type(self, var):
        try:
            return self.local_frame[-1][var][0]
        except:
            sys.stderr.write("ERROR: Empty local frame.\n")
            exit(55)

# Trida pro instrukci
class Instruction:
    # Priradi nazev, poradi a zatim prazdny list argumentu pro instrukci
    def __init__(self, opcode, order):
        self.opcode = opcode
        self.order = order
        self.args = []

    # Prida novy argument k instrukci a zaroven je seradi
    def add_arguments(self, num, arg_type, value):
        self.args.append(Argument(num, arg_type, value))
        self.args.sort(key=lambda x: x.get_num())

    # Ziskani nazvu instrukce
    def get_opcode(self):
        return self.opcode

    # Ziskani order instrukce
    def get_order(self):
        return self.order

    # Porovna pocet zadanych a pocet ulozenych parametru
    def check_num_args(self, num_args):
        if not(len(self.args) == num_args):
            sys.stderr.write("ERROR: Bad number of arguments.\n")
            exit(32)

    # Zkontroluje, zda je spravne poradi argumentu
    def check_valid_num_args(self, num_args):
        arguments = ["arg1", "arg2", "arg3"]
        for i in range(0, num_args):
            if not(self.args[i].get_num() == arguments[i]):
                sys.stderr.write("ERROR: Bad number order of arguments.\n")
                exit(32)

    # Ziskani argumentu instrukce
    def get_args(self):
        return self.args

# Trida pro argument
class Argument:
    # Priradi cislo, typ a hodnotu argumentu
    def __init__(self, num, arg_type, value):
        self.num = num
        self.arg_type = arg_type
        self.value = value

    # Ziskani cisla argumentu
    def get_num(self):
        return self.num

    # Ziskani typu argumentu
    def get_arg_type(self):
        return self.arg_type

    # Ziskani hodnoty argumentu
    def get_value(self):
        return self.value
#################################################################


#################################################################
# Pomocna funkce pro vypis napovedy
def help_print():
    print(" Usage: python3 interpret.py [--help] [--source=<file_path>] [--input=<file_path>]")
    print("\tImportant: At least one of these arguments (source, input) must be given")
    print("\t1) --help: Show usage")
    print("\t\t   Can't be combined with any other argument")
    print("\t2) --source=<file_path>: XML file ")
    print("\t\t\t\t Optional -> getting from stdin")
    print("\t3) --input=<file_path>: File with inputs for interpretation")
    print("\t\t\t\tOptional -> getting from stdin")
#################################################################


#################################################################
# Pomocna funkce pro vypis napovedy pri erroru
def help_error_print():
    sys.stderr.write(" Usage: python3 interpret.py [--help] [--source=<file_path>] [--input=<file_path>]\n")
    sys.stderr.write("\tImportant: At least one of these arguments (source, input) must be given\n")
    sys.stderr.write("\t1) --help: Show usage\n")
    sys.stderr.write("\t\t   Can't be combined with any other argument\n")
    sys.stderr.write("\t2) --source=<file_path>: XML file\n")
    sys.stderr.write("\t\t\t\t Optional -> getting from stdin\n")
    sys.stderr.write("\t3) --input=<file_path>: File with inputs for interpretation\n")
    sys.stderr.write("\t\t\t\tOptional -> getting from stdin\n")
#################################################################


#################################################################
# Kontrola argumentu a jejich parametru
# Kontrola, zda je zadan soubor, existence souboru nebo pristupu k nemu
def args_check():
    # Vytvoreni argument parseru
    parser = argparse.ArgumentParser(add_help=False)

    # Pridani argumentu
    parser.add_argument('--help', action='store_true')
    parser.add_argument('--input', type=str)
    parser.add_argument('--source', type=str)

    # Predani argumentu
    args, unknown_args = parser.parse_known_args()

    # Kontrola neznamych argumentu
    if unknown_args:
        sys.stderr.write("ERROR: Unknown argument.\n")
        help_error_print()
        exit(10)

    # Overeni, zda je pouze --help parametr
    if args.help:
        if len(sys.argv) == 2:
            help_print()
            exit(0)
        else:
            sys.stderr.write("ERROR: \"--help\" must be used without any other arguments.\n")
            help_error_print()
            exit(10)

    # Obsahuje pouze nazev souboru bez argumentu
    if len(sys.argv) < 2:
        sys.stderr.write("ERROR: One of --input or --source must be given.\n")
        help_error_print()
        exit(10)

    global input_file
    global source_file
    # Kontrola, zda byl parametr zadan nebo je potreba nacitat ze stdin
    if args.input:
        # Kontrola, zda obsahuje soubor nebo ma k nemu pristup
        if os.path.isfile(args.input):
            try:
                input_file = open(args.input, "r")
            except:
                sys.stderr.write("ERROR: Missing file or missing permission to open this file.\n")
                exit(11)
        else:
            sys.stderr.write("ERROR: Missing file or missing permission to open this file.\n")
            exit(11)
    # Pokud neobsahuje parametr, nacita ze stdin
    elif not args.input:
        input_file = sys.stdin

    # Kontrola, zda byl parametr zadan nebo je potreba nacitat ze stdin
    if args.source:
        # Kontrola, zda obsahuje soubor nebo ma k nemu pristup
        if os.path.isfile(args.source):
            source_file = args.source
        else:
            sys.stderr.write("ERROR: Missing file or missing permission to open this file.\n")
            exit(11)
    # Pokud neobsahuje parametr, nacita ze stdin
    elif not args.source:
        source_file = sys.stdin
    else:
        help_error_print()
        exit(10)
#################################################################


#################################################################
# Funkce pro ziskani o jaky frame se jedna, nebo None pokud to neni frame
def get_frame(frame):
    if frame is None:
        return None
    if re.match(r"^GF@", frame):
        return "GF"
    if re.match(r"^LF@", frame):
        return "LF"
    if re.match(r"^TF@", frame):
        return "TF"
    else:
        return None
#################################################################


#################################################################
# Ziskani dvojice (typ, hodnota) z argumentu (i kdyz je argument ramec)
# Pokud je zadan parametr expect_type, tak kontrolujeme, zda dany typ odpovida ocekavanemu expect_type
# Pokud je zadan parametr position, tak vracime znak na pozici position
def get_item_from_frame(arg, position, expect_type, global_frame, local_frame, temp_frame):
    # Ziskani, o ktery ramec se jedna
    frame = get_frame(arg.get_value())
    # Ziskani hodnoty ramce nebo hodnoty, pokud se nejedna o ramec
    var = arg.get_value()
    if position is None:
        if frame == "GF":
            # Zda existuje v ramci dana promenna
            try:
                global_frame[var[3:]]
            except:
                sys.stderr.write("ERROR: Variable doesn't exists.\n")
                exit(54)
            # Zda vyhovuje danemu typu a typ byl zadan
            if global_frame[var[3:]][0] != expect_type and not (expect_type is None):
                sys.stderr.write("ERROR: Invalid type of argument.\n")
                exit(53)
            else:
                return global_frame[var[3:]][0], global_frame[var[3:]][1]
        if frame == "LF":
            # Zda vyhovuje danemu typu a typ byl zadan
            if local_frame.get_type(var[3:]) != expect_type and not(expect_type is None):
                sys.stderr.write("ERROR: Invalid type of argument.\n")
                exit(53)
            else:
                return local_frame.get_type(var[3:]), local_frame.get_item(var[3:])
        if frame == "TF":
            # Kontrola, ze je docasny ramec vytvoren
            if temp_frame is not None:
                # Zda existuje v ramci dana promenna
                try:
                    temp_frame[var[3:]]
                except:
                    sys.stderr.write("ERROR: Variable doesn't exists.\n")
                    exit(54)
                # Zda vyhovuje danemu typu a typ byl zadan
                if temp_frame[var[3:]][0] != expect_type and not(expect_type is None):
                    sys.stderr.write("ERROR: Invalid type of argument.\n")
                    exit(53)
                else:
                    return temp_frame[var[3:]][0], temp_frame[var[3:]][1]
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)
        else:
            # Pokud jsme necetli z ramce, tak vracime rovnou (typ, hodnota)
            return list(arg.get_arg_type())[0], arg.get_value()
    # Pozice neni celociselna
    elif position[0] != "int":
        sys.stderr.write("ERROR: Position must be int and in the list.\n")
        exit(53)
    else:
        if frame == "GF":
            # Zda existuje v ramci dana promenna
            try:
                global_frame[var[3:]]
            except:
                sys.stderr.write("ERROR: Variable doesn't exists.\n")
                exit(54)
            if global_frame[var[3:]][0] != expect_type and not(expect_type is None):
                sys.stderr.write("ERROR: Invalid type of argument.\n")
                exit(53)
            # Pri setchar nemuzeme vlozit prazdny string, takze ho nechceme ani ziskat
            if global_frame[var[3:]][1] is None:
                sys.stderr.write("ERROR: SETCHAR can't use empty string.\n")
                exit(58)
            # Pozice neni mimo velikost pole
            if int(position[1]) < len(global_frame[var[3:]][1]):
                return global_frame[var[3:]][0], global_frame[var[3:]][1][int(position[1])]
            else:
                sys.stderr.write("ERROR: Index is outside of the string.\n")
                exit(58)

        if frame == "LF":
            if local_frame.get_type(var[3:]) != expect_type and not(expect_type is None):
                sys.stderr.write("ERROR: Invalid type of argument.\n")
                exit(53)
            # Pri setchar nemuzeme vlozit prazdny string, takze ho nechceme ani ziskat
            if local_frame.get_item(var[3:]) is None:
                sys.stderr.write("ERROR: SETCHAR can't use empty string.\n")
                exit(58)
            # Pozice neni mimo velikost pole
            if int(position[1]) < len(local_frame.get_item(var[3:])):
                return local_frame.get_type(var[3:]), local_frame.get_item(var[3:])[int(position[1])]
            else:
                sys.stderr.write("ERROR: Index is outside of the string.\n")
                exit(58)
        if frame == "TF":
            # Kontrola, ze je docasny ramec vytvoren
            if temp_frame is not None:
                # Zda existuje v ramci dana promenna
                try:
                    temp_frame[var[3:]]
                except:
                    sys.stderr.write("ERROR: Variable doesn't exists.\n")
                    exit(54)
                if temp_frame[var[3:]][0] != expect_type and not(expect_type is None):
                    sys.stderr.write("ERROR: Invalid type of argument.\n")
                    exit(53)
                # Pri setchar nemuzeme vlozit prazdny string, takze ho nechceme ani ziskat
                if temp_frame[var[3:]][1] is None:
                    sys.stderr.write("ERROR: SETCHAR can't use empty string.\n")
                    exit(58)
                # Pozice neni mimo velikost pole
                if int(position[1]) < len(temp_frame[var[3:]][1]):
                    return temp_frame[var[3:]][0], temp_frame[var[3:]][1][int(position[1])]
                else:
                    sys.stderr.write("ERROR: Index is outside of the string.\n")
                    exit(58)
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)
        else:
            # Pokud jsme necetli z ramce
            return list(arg.get_arg_type())[0], arg.get_value()[int(position[1])]
#################################################################


#################################################################
# Vlozeni dvojice (typ, hodnota) do ramce
# Pokud je zadan parametr position, tak vlozime zadanou hodnotu na pozici position v ramci
def push_item_to_frame(arg, type, value, position, global_frame, local_frame, temp_frame):
    # Ziskani, o ktery ramec se jedna
    frame = get_frame(arg.get_value())
    # Ziskani hodnoty ramce nebo hodnoty, pokud se nejedna o ramec
    var = arg.get_value()
    if position is None:
        if frame == "GF":
            # Zda existuje v ramci dana promenna
            try:
                global_frame[var[3:]]
            except:
                sys.stderr.write("ERROR: Variable doesn't exists.\n")
                exit(54)
            global_frame[var[3:]] = type, value
        if frame == "LF":
            local_frame.push_LF(var[3:], type, value)
        if frame == "TF":
            # Kontrola, ze je docasny ramec vytvoren
            if temp_frame is not None:
                # Zda existuje v ramci dana promenna
                try:
                    temp_frame[var[3:]]
                except:
                    sys.stderr.write("ERROR: Variable doesn't exists.\n")
                    exit(54)
                temp_frame[var[3:]] = type, value
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)
    else:
        if frame == "GF":
            # Zda existuje v ramci dana promenna
            try:
                global_frame[var[3:]]
            except:
                sys.stderr.write("ERROR: Variable doesn't exists.\n")
                exit(54)
            # Pozice neni mimo velikost pole
            if int(position[1]) < len(global_frame[var[3:]][1]):
                # Vlozi hodnotu na pozici position
                global_frame[var[3:]] = "string", global_frame[var[3:]][1][:int(position[1])] + value + \
                                                  global_frame[var[3:]][1][int(position[1])+1:]
            else:
                sys.stderr.write("ERROR: Index is outside of the string.\n")
                exit(58)
        if frame == "LF":
            # Pozice neni mimo velikost pole
            if int(position[1]) < len(local_frame.get_item(var[3:])):
                # Ziskam hodnotu z lokalniho ramce
                val = local_frame.get_item(var[3:])
                # Na pozici zmenim hodnotu
                val[position] = value
                # Vlozim do lokalniho ramce zmenenou hodnotu
                local_frame.push_LF(var[3:], "string", val)
            else:
                sys.stderr.write("ERROR: Index is outside of the string.\n")
                exit(58)
        if frame == "TF":
            # Kontrola, ze je docasny ramec vytvoren
            if temp_frame is not None:
                # Zda existuje v ramci dana promenna
                try:
                    temp_frame[var[3:]]
                except:
                    sys.stderr.write("ERROR: Variable doesn't exists.\n")
                    exit(54)
                # Pozice neni mimo velikost pole
                if int(position[1]) < len(temp_frame[var[3:]][1]):
                    # Vlozi hodnotu na pozici position
                    temp_frame[var[3:]] = "string", temp_frame[var[3:]][1][:int(position[1])] + value + \
                                                    temp_frame[var[3:]][1][int(position[1]) + 1:]
                else:
                    sys.stderr.write("ERROR: Index is outside of the string.\n")
                    exit(58)
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)
#################################################################


#################################################################
# Kontrola typu argumentu, kdy pocet argumentu je promenlivy
def type_check(obj, *args):
    # Ziskani argumentu
    arguments = obj.get_args()
    # Counter pro posouvani v parametru argumentu
    cnt = 0
    # Prochazeni argumentu
    for i in arguments:
        # Ziskani typu argumentu
        for arg_type in i.get_arg_type():
            # Pokud nactu prazdny string, tak pokracuji a nekontroluji
            # Hazelo by to chybu pri porovnavani s regexem
            if i.get_value() is None:
                continue
            # Pokud se argument nachazi v zadanem typu argumentu, tak zkontroluji jeho hodnotu
            if arg_type in args[cnt]:
                if (re.match(r"int", arg_type)):
                    if not((re.match(r"^((?:(\+|\-){0,1}0$)|(?:(\+|\-){0,1}[1-9][0-9]*$))$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"label", arg_type)):
                    if not((re.match(r"^[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"var", arg_type)):
                    if not((re.match(r"^(LF|TF|GF)@[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"bool", arg_type)):
                    if not((re.match(r"^(true|false)$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"nil", arg_type)):
                    if not((re.match(r"^nil$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"type", arg_type)):
                    if not((re.match(r"^(int|string|bool)$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"string", arg_type)):
                    if not((re.match(r"^([^\\\s#]|\\\d{3})*$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                cnt += 1
            else:
                # Pokud nesedel typ argumentu s ocekavanym
                # U TYPE se jedna o chybu 32
                if args[cnt] == "type":
                    sys.stderr.write("ERROR: Invalid type of argument in instruction " + obj.get_opcode() + ".\n")
                    exit(32)
                # Pokud nesedel typ argumentu dane instrukce s ocekavanym argumentem
                else:
                    sys.stderr.write("ERROR: Invalid type of argument in instruction " + obj.get_opcode() + ".\n")
                    exit(53)
#################################################################


#################################################################
# Pridani argumentu k instrukci
def add_arg(child, obj):
    for subelem in child:
        obj.add_arguments(subelem.tag, subelem.attrib.values(), subelem.text)
#################################################################


#################################################################
# Definovani promenne v ramci
def def_frame(frame, global_frame, local_frame, temp_frame):
    if re.match(r"^TF@", frame[:3]):
        # Kontrola, ze je docasny ramec vytvoren
        if temp_frame is not None:
            # Kontrola, zda uz neni promenna v ramci definovana
            if frame[3:] in temp_frame:
                sys.stderr.write("ERROR: Variable is already defined.\n")
                exit(52)
            else:
                # Vlozeni dvojice (typ, hodnota), kdy oboji je nedefinovano
                temp_frame[frame[3:]] = None, None
        else:
            sys.stderr.write("ERROR: Frame doesn't exists.\n")
            exit(55)

    if re.match(r"^LF@", frame[:3]):
        # Pokud je list lokalnich ramcu prazdny, tak vytvori novy lokalni ramec
        if not local_frame.get_LF():
            local_frame.create_LF_dict()
        # Vlozeni dvojice (typ, hodnota), kdy oboji je nedefinovano
        local_frame.def_LF(frame[3:])
    if re.match(r"^GF@", frame[:3]):
        # Kontrola, zda uz neni promenna v ramci definovana
        if frame[3:] in global_frame:
            sys.stderr.write("ERROR: Variable is already defined.\n")
            exit(52)
        else:
            global_frame[frame[3:]] = None, None
#################################################################


#################################################################
# Prevedeni escape sekvenci na char a vraceni upraveneho stringus
def replace_esc_seq(string):
    # Abychom si zajistili, ze to bude string
    string = str(string)
    # Najdeme vsechny escape sekvence
    esc_seq = re.findall(r"\\\d{3}", string)
    # Pokud neni list escape sekvenci, tak menime
    if esc_seq != []:
        # Pro kazdou escape sekvenci ji prevedeme na char
        for i in esc_seq:
            rm_esc_seq = chr(int(i[1:]))
            string = string.replace(i, rm_esc_seq)
    return string
#################################################################


#################################################################
# Pomocna funkce pro ziskani hodnot pro aritmeticke operace
# Vraci list dvou dvojic (typ, hodnota)
def arithmetic_operation(obj, global_frame, local_frame, temp_frame):
    values = []
    arg1 = get_item_from_frame(obj.get_args()[1], None, "int", global_frame, local_frame, temp_frame)
    arg2 = get_item_from_frame(obj.get_args()[2], None, "int", global_frame, local_frame, temp_frame)
    values.append(arg1)
    values.append(arg2)
    return values
#################################################################


#################################################################
# Pomocna funkce pro ziskani hodnot pro logicke operace
# Vraci list dvou hodnot (True nebo False), nebo jedne hodnoty v pripade instrukce NOT
def logical_operation(obj, global_frame, local_frame, temp_frame):
    values = []
    arg1 = get_item_from_frame(obj.get_args()[1], None, "bool", global_frame, local_frame, temp_frame)
    if arg1[1] == "true":
        values.append(True)
    else:
        values.append(False)
    # Pokud si tuto funkci volala instrukce NOT, tak ma jen jeden argument
    if not(obj.get_opcode() == "NOT"):
        arg2 = get_item_from_frame(obj.get_args()[2], None, "bool", global_frame, local_frame, temp_frame)
        if arg2[1] == "true":
            values.append(True)
        else:
            values.append(False)
    return values
#################################################################


#################################################################
# Funkce pro kontrolu stejnych typu argumentu
# Pokud se jedna o instrukci EQ, tak je mozne porovnavat i s nil
def check_same_type(obj, equals, global_frame, local_frame, temp_frame):
    values = []
    arg1 = get_item_from_frame(obj.get_args()[1], None, None, global_frame, local_frame, temp_frame)
    arg2 = get_item_from_frame(obj.get_args()[2], None, None, global_frame, local_frame, temp_frame)
    if equals is None:
        if arg1[0] == "nil" or arg2[0] == "nil":
            sys.stderr.write("ERROR: Argument can't be nil.\n")
            exit(53)

    if arg1[0] == arg2[0] or arg1[0] == "nil" or arg2[0] == "nil":
        values.append(arg1)
        values.append(arg2)
        return values
    else:
        sys.stderr.write("ERROR: Different types of operands.\n")
        exit(53)
#################################################################


#################################################################
# Popuje hodnoty, dokud nenarazi na zadanou hodnotu
def pop_label_stack(list, value):
    while list and list[-1] != value:
        list.pop()
#################################################################


#################################################################
# Kontrola spravnosti XML souboru
def tree_check(root):
    if root.tag != 'program':
        exit(32)

    # Kontrola jazyka IPPcode23
    language = root.get('language', None)
    if language is not None:
        if not(re.match(r"^IPPcode23$", language)):
            sys.stderr.write("ERROR: Bad language attribute in the XML file.\n")
            exit(32)
    else:
        sys.stderr.write("ERROR: Language attribute not found in the XML file.\n")
        exit(32)

    # List pro kontrolu unikatnich opcodes
    unique_opcode = set()
    # Kontrola kazde instrukce
    for child in root:
        if child.tag != 'instruction':
            exit(32)
        # List pro order a opcode, ktere maji byt v instrukci
        instruct_keys = list(child.attrib.keys())
        instruct_values = list(child.attrib.values())

        # Kontrola zda instrukce obsahuje order a opcode
        if not('order' in instruct_keys) or not('opcode' in instruct_keys):
            exit(32)

        # Kontrola zda order je jen kladne cislo a vetsi nez 0
        if not(re.match(r"^[1-9][0-9]*$", instruct_values[0])):
            sys.stderr.write("ERROR: Bad number of opcode.\n")
            exit(32)

        # Kontrola duplicity opcode
        # Prohledavame jen opcodes, proto jen pozice 0
        if instruct_values[0] in unique_opcode:
            sys.stderr.write("ERROR: Duplicity of opcode.\n")
            exit(32)
        else:
            unique_opcode.add(instruct_values[0])

        # Kontrola zda instrukce ma max 3 argumenty a kazdy je jen jednou
        unique_args = set()
        for subelem in child:
            if not(re.match(r"arg[123]", subelem.tag)):
                exit(32)

            # Kontrola, ze se argument nevyskytuje vicekrat
            if subelem.tag in unique_args:
                sys.stderr.write("ERROR: Duplicity of arg.\n")
                exit(32)
            else:
                unique_args.add(subelem.tag)
#################################################################


#################################################################
# Nacteni z XML souboru
def tree_load(global_frame, local_frame, temp_frame, data_stack, label_stack, call_stack):
    # List pro instrukce
    instruction_list = []
    # Kontrola, zda jde nacist XML soubor
    try:
        ET.parse(source_file)
    except:
        sys.stderr.write("ERROR: Bad XML format or XML file.\n")
        exit(31)

    tree = ET.parse(source_file)
    root = tree.getroot()
    tree_check(root)
    # Counter pro posouvani v listu instrukci
    i = 0
    # Prvotni nacteni instrukci, aby byli serazene uz podle ORDER
    for child in root:
        instruct_keys = list(child.attrib.values())
        instruction_list.append(Instruction(instruct_keys[1].upper(), instruct_keys[0]))
        add_arg(child, instruction_list[i])
        i += 1
        # Serazeni instrukci podle ORDER
        instruction_list.sort(key=lambda x: int(x.get_order()))

    # Ziskani vsech navesti
    # Vytvori list, ktery odpovida listu instrukci, pro lehci skakani na navesti
    for instruction in instruction_list:
        if 'LABEL' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, "label")
            arg = get_item_from_frame(instruction.get_args()[0], None, "label", global_frame, local_frame, temp_frame)
            # Kontrola, zda navesti uz nebylo definovano
            if(arg[1] in label_stack):
                sys.stderr.write("ERROR: Label is already defined.\n")
                exit(52)
            else:
                label_stack.append(arg[1])
        else:
            # Pokud to nebylo navesti
            label_stack.append(None)
    j = 0
    while True:
        # Kontrola, zda neni projity cely list instrukci, slouzi pro ukonceni nekonecne smycky
        try:
            instruction_list[j]
        except:
            exit(0)
        instruction = instruction_list[j]
        # Kontrola nazvu OPCODE a provedeni instrukce

        # Presunuti hodnoty do ramce
        if 'MOVE' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"])
            arg = get_item_from_frame(instruction.get_args()[1], None, None, global_frame, local_frame, temp_frame)
            push_item_to_frame(instruction.get_args()[0], arg[0], arg[1], None, global_frame, local_frame, temp_frame)

        # Vytvoreni docasneho ramce
        elif 'CREATEFRAME' == instruction.get_opcode():
            instruction.check_num_args(0)
            # Vytvori prazdny docasny ramec
            temp_frame = {}

        # Presune docasny ramec do listu lokalnich ramcu
        elif 'PUSHFRAME' == instruction.get_opcode():
            instruction.check_num_args(0)
            # Kontrola, zda docasny ramec existuje
            if temp_frame is None:
                sys.stderr.write("ERROR: Undefined temporary frame.\n")
                exit(55)
            # Vytvorim novy lokalni ramec a vlozim tam docasny
            local_frame.create_LF_dict()
            local_frame.push_new_LF(temp_frame)
            # Vymazu docasny ramec
            temp_frame = None

        # Presune lokalni ramce do docasneho ramce
        elif 'POPFRAME' == instruction.get_opcode():
            instruction.check_num_args(0)
            # Vlozim lokalni ramec do docasneho ramce
            temp_frame = local_frame.pop_LF()

        # Definovani hodnoty v ramci
        elif 'DEFVAR' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, "var")
            def_frame(instruction.get_args()[0].get_value(), global_frame, local_frame, temp_frame)

        # Presunuti na navesti s moznosti vraceni
        elif 'CALL' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, "label")
            arg = get_item_from_frame(instruction.get_args()[0], None, "label", global_frame, local_frame, temp_frame)
            # Ulozeni pozice dalsi instrukce na zasobnik volani
            call_stack.append(j+1)
            # Pokud skace na navesti, ktere neexistuje
            if not (arg[1] in label_stack):
                sys.stderr.write("ERROR: Undefined label.\n")
                exit(52)
            else:
                # Skok na navesti
                label_copy = label_stack.copy()
                pop_label_stack(label_copy, arg[1])
                j = len(label_copy) - 1
            continue

        # Vraceni za CALL volani
        elif 'RETURN' == instruction.get_opcode():
            instruction.check_num_args(0)
            type_check(instruction)
            try:
                # Ziskani hodnotz ze zasobniku volani
                j = int(call_stack.pop())
            except:
                sys.stderr.write("ERROR: Empty call stack.\n")
                exit(56)
            continue

        # Vlozeni hodnoty na datovy zasovnik
        elif 'PUSHS' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, ["int", "string", "bool", "nil", "var"])
            tuple = get_item_from_frame(instruction.get_args()[0], None, None, global_frame, local_frame, temp_frame)
            # Vlozeni na zasobnik dvojice (typ, hodnota)
            data_stack.append(tuple)

        # Ziskani hodnoty z datoveho zasobniku
        elif 'POPS' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, "var")
            # Kontrola, zda neni zasobnik prazdny
            try:
                data_stack[-1]
            except:
                sys.stderr.write("ERROR: Data stack is empty.\n")
                exit(56)
            push_item_to_frame(instruction.get_args()[0], data_stack[-1][0], data_stack[-1][1], None, global_frame,
                               local_frame, temp_frame)
            # Odebrani z datoveho zasobniku
            data_stack.pop()

        # Scitani
        elif 'ADD' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "var"], ["int", "var"])
            values = arithmetic_operation(instruction, global_frame, local_frame, temp_frame)
            push_item_to_frame(instruction.get_args()[0], "int", str(int(values[0][1]) + int(values[1][1])), None, global_frame, local_frame,
                               temp_frame)

        # Odecitani
        elif 'SUB' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "var"], ["int", "var"])
            values = arithmetic_operation(instruction, global_frame, local_frame, temp_frame)
            push_item_to_frame(instruction.get_args()[0], "int", str(int(values[0][1]) - int(values[1][1])), None, global_frame, local_frame,
                               temp_frame)

        # Nasobeni
        elif 'MUL' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "var"], ["int", "var"])
            values = arithmetic_operation(instruction, global_frame, local_frame, temp_frame)
            push_item_to_frame(instruction.get_args()[0], "int", str(int(values[0][1]) * int(values[1][1])), None, global_frame, local_frame,
                               temp_frame)

        # Celociselne deleni
        elif 'IDIV' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "var"], ["int", "var"])
            values = arithmetic_operation(instruction, global_frame, local_frame, temp_frame)
            if int(values[1][1]) == 0:
                sys.stderr.write("ERROR: Can't divide by 0.\n")
                exit(57)
            # Diky // ziskame cele cislo po deleni
            push_item_to_frame(instruction.get_args()[0], "int", str(int(values[0][1]) // int(values[1][1])), None, global_frame,
                               local_frame, temp_frame)

        # Porovna, zda je prvni hodnota mensi nez druha
        elif 'LT' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "string", "bool", "var"], ["int", "string", "bool", "var"])
            values = check_same_type(instruction, None, global_frame, local_frame, temp_frame)
            # Pri cislech musime pretypovat hodnotu ulozenou jako string na int, aby fungovalo porovnavani
            if values[0][0] == "int":
                push_item_to_frame(instruction.get_args()[0], "bool",
                                   (str(int(values[0][1]) < int(values[1][1]))).lower(), None, global_frame,
                                   local_frame, temp_frame)
            else:
                push_item_to_frame(instruction.get_args()[0], "bool", (str(values[0][1] < values[1][1])).lower(), None,
                                   global_frame, local_frame, temp_frame)

        # Porovna, zda je prvni hodnota vetsi nez druha
        elif 'GT' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "string", "bool", "var"], ["int", "string", "bool", "var"])
            values = check_same_type(instruction, None, global_frame, local_frame, temp_frame)
            # Pri cislech musime pretypovat hodnotu ulozenou jako string na int, aby fungovalo porovnavani
            if values[0][0] == "int":
                push_item_to_frame(instruction.get_args()[0], "bool",
                                   (str(int(values[0][1]) > int(values[1][1]))).lower(), None, global_frame,
                                   local_frame, temp_frame)
            else:
                push_item_to_frame(instruction.get_args()[0], "bool", (str(values[0][1] > values[1][1])).lower(), None,
                                   global_frame, local_frame, temp_frame)

        # AND hodnot
        elif 'AND' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["bool", "var"], ["bool", "var"])
            values = logical_operation(instruction, global_frame, local_frame, temp_frame)
            push_item_to_frame(instruction.get_args()[0], "bool", (str(values[0] and values[1])).lower(), None,
                               global_frame, local_frame, temp_frame)

        # OR hodnot
        elif 'OR' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["bool", "var"], ["bool", "var"])
            values = logical_operation(instruction, global_frame, local_frame, temp_frame)
            push_item_to_frame(instruction.get_args()[0], "bool", (str(values[0] or values[1])).lower(), None,
                               global_frame, local_frame, temp_frame)

        # Negace hodnoty
        elif 'NOT' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["bool", "var"])
            values = logical_operation(instruction, global_frame, local_frame, temp_frame)
            push_item_to_frame(instruction.get_args()[0], "bool", (str(not(values[0]))).lower(), None, global_frame,
                               local_frame, temp_frame)

        # Prevedeni cisla na retezec
        elif 'INT2CHAR' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["int", "var"])
            arg = get_item_from_frame(instruction.get_args()[1], None, "int", global_frame, local_frame, temp_frame)
            # Kontrola, zda je hodnota v UNICODE
            try:
                chr(int(arg[1]))
            except:
                sys.stderr.write("ERROR: Value is not valid in UNICODE.\n")
                exit(58)
            push_item_to_frame(instruction.get_args()[0], "string", chr(int(arg[1])), None, global_frame, local_frame,
                               temp_frame)

        # Prevedeni retezce na cislo
        elif 'STRI2INT' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["string", "var"], ["int", "var"])
            arg = get_item_from_frame(instruction.get_args()[1], None, "string", global_frame, local_frame, temp_frame)
            position = get_item_from_frame(instruction.get_args()[2], None, "int", global_frame, local_frame,
                                           temp_frame)
            if arg[0] != "string" or position[0] != "int":
                sys.stderr.write("ERROR: STRI2INT expected string and on position int.\n")
                exit(53)
            else:
                try:
                    ord(arg[1][int(position[1])])
                except:
                    sys.stderr.write("ERROR: Value is not valid in UNICODE.\n")
                    exit(58)
                push_item_to_frame(instruction.get_args()[0], "string", ord(arg[1][int(position[1])]), None,
                                   global_frame, local_frame, temp_frame)

        # Cte ze souboru, nebo pripadne ze STDIN
        elif 'READ' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", "type")
            read_value = input_file.readline()
            read_value = read_value.strip()
            arg_type = instruction.get_args()[1].get_value()
            if arg_type == "bool":
                if re.match(r"true", read_value, flags=re.IGNORECASE):
                    read_value = "true"
                elif re.match(r"false", read_value, flags=re.IGNORECASE):
                    read_value = "false"
                else:
                    read_value = "nil"
                    arg_type = "nil"

            if not read_value:
                read_value = "nil"
                arg_type = "nil"

            if (not(re.match(r"^((?:(\+|\-){0,1}0$)|(?:(\+|\-){0,1}[1-9][0-9]*$))$", read_value))
                    and arg_type == "int"):
                arg_type = "nil"
                read_value = "nil"
            elif (not(re.match(r"^([^\\#]|\\\d{3})*$", read_value)) and arg_type == "string"):
                arg_type = "nil"
                read_value = "nil"
            push_item_to_frame(instruction.get_args()[0], arg_type, read_value, None, global_frame, local_frame,
                               temp_frame)

        # Vypise zadanou hodnotu
        elif 'WRITE' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, ["int", "string", "bool", "nil", "var"])
            arg = get_item_from_frame(instruction.get_args()[0], None, None, global_frame, local_frame, temp_frame)
            if arg[0] == "nil" or arg[1] is None:
                print("", end='')
            elif arg[0] == "bool":
                print(arg[1], end='')
            else:
                print(replace_esc_seq(arg[1]), end='')

        # Spoji 2 retezce
        elif 'CONCAT' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["string", "var"], ["string", "var"])
            arg1 = get_item_from_frame(instruction.get_args()[1], None, "string", global_frame, local_frame, temp_frame)
            arg2 = get_item_from_frame(instruction.get_args()[2], None, "string", global_frame, local_frame, temp_frame)
            if arg1[0] != "string" or arg2[0] != "string":
                sys.stderr.write("ERROR: CONCAT expected string.\n")
                exit(53)
            else:
                push_item_to_frame(instruction.get_args()[0], "string", arg1[1] + arg2[1], None, global_frame,
                                   local_frame, temp_frame)

        # Vypocita delku zadaneho retezce
        elif 'STRLEN' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["string", "var"])
            arg = get_item_from_frame(instruction.get_args()[1], None, "string", global_frame, local_frame, temp_frame)
            if arg[0] != "string":
                sys.stderr.write("ERROR: STRLEN expected string.\n")
                exit(53)
            else:
                push_item_to_frame(instruction.get_args()[0], "int", str(len(arg[1])), None, global_frame, local_frame,
                                   temp_frame)

        # Ziska znak z pozice
        elif 'GETCHAR' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["string", "var"], ["int", "var"])
            position = get_item_from_frame(instruction.get_args()[2], None, "int", global_frame, local_frame,
                                           temp_frame)
            arg = get_item_from_frame(instruction.get_args()[1], position, "string", global_frame, local_frame,
                                      temp_frame)
            push_item_to_frame(instruction.get_args()[0], "string", arg[1], None, global_frame, local_frame,
                               temp_frame)

        # Vlozi zadany znak na pozici
        elif 'SETCHAR' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "var"], ["int", "string", "bool", "nil", "var"])
            position = get_item_from_frame(instruction.get_args()[1], None, "int", global_frame, local_frame,
                                           temp_frame)
            arg = get_item_from_frame(instruction.get_args()[2], ("int", 0), "string", global_frame, local_frame,
                                      temp_frame)
            push_item_to_frame(instruction.get_args()[0], "string", arg[1], position, global_frame, local_frame,
                               temp_frame)

        # Ziskani typu hodnoty
        elif 'TYPE' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"])
            arg = get_item_from_frame(instruction.get_args()[1], None, None, global_frame, local_frame, temp_frame)
            push_item_to_frame(instruction.get_args()[0], "string", arg[0], None, global_frame, local_frame, temp_frame)

        # Label uz je zpracovany z drive, takze jen posunuti na dalsi instrukci
        elif 'LABEL' == instruction.get_opcode():
            j += 1
            continue

        # Skoci na navesti, pokud se hodnoty stejneho typu nerovnaji nebo je jedna z nich nil
        elif 'JUMPIFNEQ' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "label", ["int", "string", "bool", "nil", "var"],
                       ["int", "string", "bool", "nil", "var"])
            arg = get_item_from_frame(instruction.get_args()[0], None, "label", global_frame, local_frame, temp_frame)
            values = check_same_type(instruction, "EQ", global_frame, local_frame, temp_frame)
            if values[0][1] != values[1][1]:
                # Pokud je navesti definovane
                if not(arg[1] in label_stack):
                    sys.stderr.write("ERROR: Undefined label.\n")
                    exit(52)
                else:
                    # Posunuti na navesti a ziskani instrukce
                    label_copy = label_stack.copy()
                    pop_label_stack(label_copy, arg[1])
                    j = len(label_copy) - 1
            else:
                # Pokud neplati podminka, posunuti na dalsi instrukci
                j += 1
            # Slouzi k tomu, aby se nezvysil counter pro posun v instrukcich, pokud skocime na navesti
            continue

        # Skoci na navesti, pokud se hodnoty stejneho typu rovnaji nebo je jedna z nich nil
        elif 'JUMPIFEQ' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "label", ["int", "string", "bool", "nil", "var"],
                       ["int", "string", "bool", "nil", "var"])
            arg = get_item_from_frame(instruction.get_args()[0], None, "label", global_frame, local_frame, temp_frame)
            values = check_same_type(instruction, "EQ", global_frame, local_frame, temp_frame)
            if values[0][1] == values[1][1]:
                # Pokud je navesti definovane
                if not (arg[1] in label_stack):
                    sys.stderr.write("ERROR: Undefined label.\n")
                    exit(52)
                else:
                    # Posunuti na navesti a ziskani instrukce
                    label_copy = label_stack.copy()
                    pop_label_stack(label_copy, arg[1])
                    j = len(label_copy) - 1
            else:
                # Pokud neplati podminka, posunuti na dalsi instrukci
                j += 1
            # Slouzi k tomu, aby se nezvysil counter pro posun v instrukcich, pokud skocime na navesti
            continue

        # Kontrola, zda se 2 hodnoty rovnaji a jsou stejnho typu, nebo je jedna z nich nil
        elif 'EQ' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"],
                       ["int", "string", "bool", "nil", "var"])
            values = check_same_type(instruction, "EQ", global_frame, local_frame, temp_frame)
            push_item_to_frame(instruction.get_args()[0], "bool", (str(values[0] == values[1])).lower(), None,
                               global_frame, local_frame, temp_frame)

        # Skoci na navesti
        elif 'JUMP' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, "label")
            arg = get_item_from_frame(instruction.get_args()[0], None, "label", global_frame, local_frame, temp_frame)
            # Pokud je navesti definovane
            if not (arg[1] in label_stack):
                sys.stderr.write("ERROR: Undefined label.\n")
                exit(52)
            else:
                # Posunuti na navesti a ziskani instrukce
                label_copy = label_stack.copy()
                pop_label_stack(label_copy, arg[1])
                j = len(label_copy) - 1
            # Slouzi k tomu, aby se nezvysil counter pro posun v instrukcich, pokud skocime na navesti
            continue

        # Ukonceni interpretu s navratovym kodem
        elif 'EXIT' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, ["int", "var"])
            arg = get_item_from_frame(instruction.get_args()[0], None, "int", global_frame, local_frame, temp_frame)
            if 0 <= int(arg[1]) <= 49:
                exit(int(instruction.get_args()[0].get_value()))
            else:
                sys.stderr.write("ERROR: Invalid exit code.\n")
                exit(57)

        # Vypsani hodnoty na chybovy vystup
        elif 'DPRINT' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, ["int", "string", "bool", "nil", "var"])
            arg = get_item_from_frame(instruction.get_args()[0], None, None, global_frame, local_frame, temp_frame)
            if arg[0] == "nil" or arg[1] is None:
                sys.stderr.write("")
            elif arg[0] == "bool":
                sys.stderr.write(arg[1])
            else:
                sys.stderr.write(replace_esc_seq(arg[1]))

        # Vypsani stavu interpretu na chybovy vystup
        elif 'BREAK' == instruction.get_opcode():
            instruction.check_num_args(0)

        else:
            sys.stderr.write("ERROR: Invalid opcode.\n")
            exit(32)
        # Posunuti na dalsi instrukci
        j += 1

# __main__ #
args_check()
global_frame = {}
local_frame = Local_frame()
temp_frame = None
data_stack = []
label_stack = []
call_stack = []
tree_load(global_frame, local_frame, temp_frame, data_stack, label_stack, call_stack)
exit(0)
