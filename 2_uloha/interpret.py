import re
import sys
import argparse
import xml.etree.ElementTree as ET
import os

# TODO nacitani ze stdin

class Local_frame:
    def __init__(self):
        self.local_frame = None

    def push_LF(self, var, value):
        if self.local_frame is None:
            self.local_frame = {}
        self.local_frame[var] = value

    def pop_LF(self):
        if self.local_frame is None or self.local_frame == {}:
            sys.stderr.write("ERROR: Empty local frame.\n")
            exit(55)
        else:
            return self.local_frame.popitem()

class Instruction:
    instructions_list = []

    def __init__(self, opcode, order, num_args):
        self.opcode = opcode
        self.order = order
        self.num_args = num_args
        self.args = []
        self.instructions_list.append(self)
        self.instructions_list.sort(key=lambda x: x.get_order())

    # Prida novy argument k instrukci a zaroven je seradi
    def add_arguments(self, num, arg_type, value):
        self.args.append(Argument(num, arg_type, value))
        self.args.sort(key=lambda x: x.get_num())

    def get_opcode(self):
        return self.opcode

    def get_order(self):
        return self.order

    def check_num_args(self):
        if not(len(self.args) == self.num_args):
            sys.stderr.write("ERROR: Bad number of arguments.\n")
            exit(32)

    def check_valid_num_args(self):
        arguments = ["arg1", "arg2", "arg3"]
        for i in range(0, self.num_args):
            if not(self.args[i].get_num() == arguments[i]):
                sys.stderr.write("ERROR: Bad number order of arguments.\n")
                exit(32)

    def get_list(self):
        return self.instructions_list

    def get_args(self):
        return self.args


class Argument:
    def __init__(self, num, arg_type, value):
        self.num = num
        self.arg_type = arg_type
        self.value = value

    def get_num(self):
        return self.num

    def get_arg_type(self):
        return self.arg_type

    def get_value(self):
        return self.value


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
# Pomocna funkce pro vypis napovedy
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
# Zda je zadan soubor, existence souboru nebo pristupu k nemu
def args_check():
    # Vytvoreni argument parseru
    parser = argparse.ArgumentParser(add_help=False)

    # Pridani argumentu
    parser.add_argument('--help', action='store_true')
    parser.add_argument('--input', type=str)
    parser.add_argument('--source', type=str)

    # Predani argumentu
    args, unknown_args = parser.parse_known_args()

    # Overeni, zda je pouze --help parametr
    if unknown_args:
        sys.stderr.write("ERROR: Unknown argument.\n")
        help_error_print()
        exit(10)

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
    # Kontrola, zda byl parametr zadan jinak
    if args.input:
        # Kontrola, zda obsahuje soubor nebo ma k nemu pristup
        if os.path.isfile(args.input):
            input_file = args.input
        else:
            sys.stderr.write("ERROR: Missing file or missing permission to open this file.\n")
            exit(11)
    elif not args.input:
        input_file = sys.stdin

    if args.source:
        # Kontrola, zda obsahuje soubor nebo ma k nemu pristup
        if os.path.isfile(args.source):
            source_file = args.source
        else:
            sys.stderr.write("ERROR: Missing file or missing permission to open this file.\n")
            exit(11)
    elif not args.source:
        source_file = sys.stdin
    else:
        help_error_print()
        exit(10)
#################################################################



#################################################################
# Kontrola typu argumentu
def type_check(obj):
    args = obj.get_args()
    for i in args:
        for j in i.get_arg_type():
            if (re.match(r"int", j)):
                if not((re.match(r"^((?:(\+|\-){0,1}0$)|(?:(\+|\-){0,1}[1-9][0-9]*$))$", i.get_value()))):
                    sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                    exit(32)
            elif (re.match(r"label", j)):
                if not((re.match(r"^[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$", i.get_value()))):
                    sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                    exit(32)
            elif (re.match(r"var", j)):
                if not((re.match(r"^(LF|TF|GF)@[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$", i.get_value()))):
                    sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                    exit(32)
            elif (re.match(r"bool", j)):
                if not((re.match(r"^(true|false)$", i.get_value()))):
                    sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                    exit(32)
            elif (re.match(r"nil", j)):
                if not((re.match(r"^nil$", i.get_value()))):
                    sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                    exit(32)
            elif (re.match(r"type", j)):
                if not((re.match(r"^(int|string|bool)$", i.get_value()))):
                    sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                    exit(32)
            elif (re.match(r"string", j)):
                if not((re.match(r"^([^\\\s#]|\\\d{3})*$", i.get_value()))):
                    sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                    exit(32)


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

        # Kontrola zda order je jen kladne cislo
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
# Pridani argumentu k instrukci
def add_arg(child, obj):
    for subelem in child:
        obj.add_arguments(subelem.tag, subelem.attrib.values(), subelem.text)
#################################################################

#################################################################
# Zjisteni o jaky ramec se jedna
def move_to_frame(frame, global_frame, local_frame, temp_frame):
    # Ziskani promenne
    split_string = frame.split("@")
    var1 = split_string[-1]

    # Ziskani promenne
    split_string = frame.split("@")
    var2 = split_string[-1]



    if(re.match(r"^TF@", frame)):
        #if var1 in temp_frame:
        temp_frame[var1] = 5
        #else:
         #   sys.stderr.write("ERROR: Variable doesn't exists.\n")
          #  exit(54)
    if (re.match(r"^LF@", frame)):
        local_frame[var1] = 5
    if (re.match(r"^GF@", frame)):
        global_frame[var1] = 5
    else:
        return None
#################################################################

#################################################################
# Definovani promenne v ramci
def def_frame(frame , global_frame, local_frame, temp_frame):
    # Ziskani promenne
    split_string = frame.split("@")
    var = split_string[-1]

    if(re.match(r"^TF@", frame)):
        if temp_frame is None:
            print("AH")
            if var in temp_frame:
                sys.stderr.write("ERROR: Variable is already defined.\n")
                exit(54)
            else:
                temp_frame[var] = None
    if (re.match(r"^LF@", frame)):
        if var in local_frame:
            sys.stderr.write("ERROR: Variable is already defined.\n")
            exit(54)
        else:
            local_frame[var] = None
    if (re.match(r"^GF@", frame)):
        if var in global_frame:
            sys.stderr.write("ERROR: Variable is already defined.\n")
            exit(54)
        else:
            global_frame[var] = None

#################################################################

#################################################################
# Nacteni z XML souboru, kdy se nejdriv i zavola funkce pro kontrolu
def tree_load(global_frame, local_frame, temp_frame):
    try:
        ET.parse(source_file)
    except:
        sys.stderr.write("ERROR: Bad XML format or XML file.\n")
        exit(31)

    tree = ET.parse(source_file)
    root = tree.getroot()
    tree_check(root)
    for child in root:
        instruct_keys = list(child.attrib.values())
        # Prvni pozice je order, na druhe je opcode
        if 'MOVE' in instruct_keys[1].upper():
            instr_move = Instruction("MOVE", instruct_keys[0], 2)
            add_arg(child, instr_move)
            instr_move.check_num_args()
            type_check(instr_move)
            move_to_frame(instr_move.get_args()[0].get_value(), global_frame, local_frame, temp_frame)
            continue

        if 'CREATEFRAME' in instruct_keys[1].upper():
            instr_createframe = Instruction("CREATEFRAME", instruct_keys[0], 0)
            add_arg(child, instr_createframe)
            instr_createframe.check_num_args()
            # Vytvori prazdny docasny ramec
            temp_frame = {}
            continue

        if 'PUSHFRAME' in instruct_keys[1].upper():
            instr_pushframe = Instruction("PUSHFRAME", instruct_keys[0], 0)
            add_arg(child, instr_pushframe)
            instr_pushframe.check_num_args()
            # Vytvori prazdny docasny ramec
            if temp_frame is None:
                sys.stderr.write("ERROR: Undefined temporary frame.\n")
                exit(55)
            # Pokud neni temporary frame prazdny, tak ho vloz na stack
            if temp_frame != {}:
                local_frame.push_LF(list(temp_frame.keys())[0], list(temp_frame.values())[0])
                temp_frame = None
            continue

        if 'POPFRAME' in instruct_keys[1].upper():
            instr_popframe = Instruction("POPFRAME", instruct_keys[0], 0)
            add_arg(child, instr_popframe)
            instr_popframe.check_num_args()
            # Pri pop mi vznikne list
            temp = list(local_frame.pop_LF())
            # Pomoci funkce zip udelam z listu zpatky dictionary
            temp_frame[temp[0]] = temp[1]
            continue

        if 'DEFVAR' in instruct_keys[1].upper():
            instr_defvar = Instruction("DEFVAR", instruct_keys[0], 1)
            add_arg(child, instr_defvar)
            instr_defvar.check_num_args()
            type_check(instr_defvar)
            def_frame(instr_defvar.get_args()[0].get_value() , global_frame, local_frame, temp_frame)
            continue

        if 'CALL' in instruct_keys[1].upper():
            instr_call = Instruction("CALL", instruct_keys[0], 1)
            add_arg(child, instr_call)
            instr_call.check_num_args()
            type_check(instr_call)
            continue

        if 'RETURN' in instruct_keys[1].upper():
            instr_return = Instruction("RETURN", instruct_keys[0], 0)
            add_arg(child, instr_return)
            instr_return.check_num_args()
            type_check(instr_return)
            continue

        if 'PUSHS' in instruct_keys[1].upper():
            instr_pushs = Instruction("PUSHS", instruct_keys[0], 1)
            add_arg(child, instr_pushs)
            instr_pushs.check_num_args()
            type_check(instr_pushs)
            continue

        if 'POPS' in instruct_keys[1].upper():
            instr_pops = Instruction("POPS", instruct_keys[0], 1)
            add_arg(child, instr_pops)
            instr_pops.check_num_args()
            type_check(instr_pops)
            continue

        if 'ADD' in instruct_keys[1].upper():
            instr_add = Instruction("ADD", instruct_keys[0], 3)
            add_arg(child, instr_add)
            instr_add.check_num_args()
            type_check(instr_add)
            continue

        if 'SUB' in instruct_keys[1].upper():
            instr_sub = Instruction("SUB", instruct_keys[0], 3)
            add_arg(child, instr_sub)
            instr_sub.check_num_args()
            type_check(instr_sub)
            continue

        if 'MUL' in instruct_keys[1].upper():
            instr_mul = Instruction("MUL", instruct_keys[0], 3)
            add_arg(child, instr_mul)
            instr_mul.check_num_args()
            type_check(instr_mul)
            continue

        if 'IDIV' in instruct_keys[1].upper():
            instr_idiv = Instruction("IDIV", instruct_keys[0], 3)
            add_arg(child, instr_idiv)
            instr_idiv.check_num_args()
            type_check(instr_idiv)
            continue

        if 'LT' in instruct_keys[1].upper():
            instr_lt = Instruction("LT", instruct_keys[0], 3)
            add_arg(child, instr_lt)
            instr_lt.check_num_args()
            type_check(instr_lt)
            continue

        if 'GT' in instruct_keys[1].upper():
            instr_gt = Instruction("GT", instruct_keys[0], 3)
            add_arg(child, instr_gt)
            instr_gt.check_num_args()
            type_check(instr_gt)
            continue

        if 'AND' in instruct_keys[1].upper():
            instr_and = Instruction("AND", instruct_keys[0], 3)
            add_arg(child, instr_and)
            instr_and.check_num_args()
            type_check(instr_and)
            continue

        if 'OR' in instruct_keys[1].upper():
            instr_or = Instruction("OR", instruct_keys[0], 3)
            add_arg(child, instr_or)
            instr_or.check_num_args()
            type_check(instr_or)
            continue

        if 'NOT' in instruct_keys[1].upper():
            instr_not = Instruction("NOT", instruct_keys[0], 2)
            add_arg(child, instr_not)
            instr_not.check_num_args()
            type_check(instr_not)
            continue

        if 'INT2CHAR' in instruct_keys[1].upper():
            instr_int2char = Instruction("INT2CHAR", instruct_keys[0], 2)
            add_arg(child, instr_int2char)
            instr_int2char.check_num_args()
            type_check(instr_int2char)
            continue

        if 'STRI2INT' in instruct_keys[1].upper():
            instr_stri2int = Instruction("STRI2INT", instruct_keys[0], 3)
            add_arg(child, instr_stri2int)
            instr_stri2int.check_num_args()
            type_check(instr_stri2int)
            continue

        if 'READ' in instruct_keys[1].upper():
            instr_read = Instruction("READ", instruct_keys[0], 2)
            add_arg(child, instr_read)
            instr_read.check_num_args()
            type_check(instr_read)
            continue

        if 'WRITE' in instruct_keys[1].upper():
            instr_write = Instruction("WRITE", instruct_keys[0], 1)
            add_arg(child, instr_write)
            instr_write.check_num_args()
            type_check(instr_write)
            instr_write.check_valid_num_args()
            continue

        if 'CONCAT' in instruct_keys[1].upper():
            instr_concat = Instruction("CONCAT", instruct_keys[0], 3)
            add_arg(child, instr_concat)
            instr_concat.check_num_args()
            type_check(instr_concat)
            continue

        if 'STRLEN' in instruct_keys[1].upper():
            instr_strlen = Instruction("STRLEN", instruct_keys[0], 2)
            add_arg(child, instr_strlen)
            instr_strlen.check_num_args()
            type_check(instr_strlen)
            continue

        if 'GETCHAR' in instruct_keys[1].upper():
            instr_getchar = Instruction("GETCHAR", instruct_keys[0], 3)
            add_arg(child, instr_getchar)
            instr_getchar.check_num_args()
            type_check(instr_getchar)
            continue

        if 'SETCHAR' in instruct_keys[1].upper():
            instr_setchar = Instruction("SETCHAR", instruct_keys[0], 3)
            add_arg(child, instr_setchar)
            instr_setchar.check_num_args()
            type_check(instr_setchar)
            continue

        if 'TYPE' in instruct_keys[1].upper():
            instr_type = Instruction("TYPE", instruct_keys[0], 2)
            add_arg(child, instr_type)
            instr_type.check_num_args()
            type_check(instr_type)
            continue

        if 'LABEL' in instruct_keys[1].upper():
            instr_label = Instruction("LABEL", instruct_keys[0], 1)
            add_arg(child, instr_label)
            instr_label.check_num_args()
            type_check(instr_label)
            continue

        if 'JUMPIFNEQ' in instruct_keys[1].upper():
            instr_jumpifneq = Instruction("JUMPIFNEQ", instruct_keys[0], 3)
            add_arg(child, instr_jumpifneq)
            instr_jumpifneq.check_num_args()
            type_check(instr_jumpifneq)
            continue

        if 'JUMPIFEQ' in instruct_keys[1].upper():
            instr_jumpifeq = Instruction("JUMPIFEQ", instruct_keys[0], 3)
            add_arg(child, instr_jumpifeq)
            instr_jumpifeq.check_num_args()
            type_check(instr_jumpifeq)
            continue

        if 'EQ' in instruct_keys[1].upper():
            instr_eq = Instruction("EQ", instruct_keys[0], 3)
            add_arg(child, instr_eq)
            instr_eq.check_num_args()
            type_check(instr_eq)
            continue

        if 'JUMP' in instruct_keys[1].upper():
            instr_jump = Instruction("JUMP", instruct_keys[0], 1)
            add_arg(child, instr_jump)
            instr_jump.check_num_args()
            type_check(instr_jump)
            continue

        if 'EXIT' in instruct_keys[1].upper():
            instr_exit = Instruction("EXIT", instruct_keys[0], 1)
            add_arg(child, instr_exit)
            instr_exit.check_num_args()
            type_check(instr_exit)
            continue

        if 'DPRINT' in instruct_keys[1].upper():
            instr_dprint = Instruction("DPRINT", instruct_keys[0], 1)
            add_arg(child, instr_dprint)
            instr_dprint.check_num_args()
            type_check(instr_dprint)
            continue

        if 'BREAK' in instruct_keys[1].upper():
            instr_break = Instruction("BREAK", instruct_keys[0], 0)
            add_arg(child, instr_break)
            instr_break.check_num_args()
            type_check(instr_break)
            continue

        else:
            sys.stderr.write("ERROR: Invalid opcode.\n")
            exit(32)



# __main__
args_check()
global_frame = {}
local_frame = Local_frame()
temp_frame = None
tree_load(global_frame, local_frame, temp_frame)

exit(0)
