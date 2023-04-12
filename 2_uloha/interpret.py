import re
import sys
import argparse
import xml.etree.ElementTree as ET
import os

# TODO nacitani ze stdin

class Local_frame:
    def __init__(self):
        self.local_frame = []

    def get_LF(self):
        return self.local_frame

    def create_LF_dict(self):
        self.local_frame.append({})

    def push_new_LF(self, var, type, value):
        self.local_frame[-1][var] = type, value

    def def_LF(self, var):
        try:
            self.local_frame[-1][var]
        except:
            self.local_frame[-1][var] = None, None
            return
        sys.stderr.write("ERROR: Variable is already defined.\n")
        exit(52)

    def push_LF(self, var, type, value):
        try:
            self.local_frame[-1][var]
        except:
            sys.stderr.write("ERROR: Variable doesn't exists.\n")
            exit(54)

        if self.local_frame[-1][var] is None:
            self.local_frame[-1][var] = type, value
        else:
            sys.stderr.write("ERROR: Variable already exists.\n")
            exit(52)

    def copy_LF(self, var, type, value):
        self.local_frame[-1][var] = type, value

    def pop_LF(self):
        try:
            return self.local_frame.pop()
        except:
            sys.stderr.write("ERROR: Empty local frame.\n")
            exit(55)

    def get_item(self, var):
        try:
            return self.local_frame[-1][var][1]
        except:
            sys.stderr.write("ERROR: Empty local frame.\n")
            exit(55)

    def get_type(self, var):
        try:
            return self.local_frame[-1][var][0]
        except:
            sys.stderr.write("ERROR: Empty local frame.\n")
            exit(55)

class Instruction:
    instructions_list = []
    def __init__(self, opcode, order):
        self.opcode = opcode
        self.order = order
        self.args = []
        self.instructions_list.append(self)

    # Prida novy argument k instrukci a zaroven je seradi
    def add_arguments(self, num, arg_type, value):
        self.args.append(Argument(num, arg_type, value))
        self.args.sort(key=lambda x: x.get_num())

    def get_opcode(self):
        return self.opcode

    def get_order(self):
        return self.order

    def check_num_args(self, num_args):
        if not(len(self.args) == num_args):
            sys.stderr.write("ERROR: Bad number of arguments.\n")
            exit(32)

    def check_valid_num_args(self, num_args):
        arguments = ["arg1", "arg2", "arg3"]
        for i in range(0, num_args):
            if not(self.args[i].get_num() == arguments[i]):
                sys.stderr.write("ERROR: Bad number order of arguments.\n")
                exit(32)

    def get_list(self):
        return self.instructions_list

    def get_args(self):
        return self.args

    def get_len(self):
        return len(self.instructions_list)

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
def type_check(obj, *args):
    arguments = obj.get_args()
    cnt = 0
    for i in arguments:
        for type in i.get_arg_type():
            if type in args[cnt]:
                if (re.match(r"int", type)):
                    if not((re.match(r"^((?:(\+|\-){0,1}0$)|(?:(\+|\-){0,1}[1-9][0-9]*$))$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"label", type)):
                    if not((re.match(r"^[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"var", type)):
                    if not((re.match(r"^(LF|TF|GF)@[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"bool", type)):
                    if not((re.match(r"^(true|false)$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"nil", type)):
                    if not((re.match(r"^nil$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"type", type)):
                    if not((re.match(r"^(int|string|bool)$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                elif (re.match(r"string", type)):
                    if not((re.match(r"^([^\\\s#]|\\\d{3})*$", i.get_value()))):
                        sys.stderr.write("ERROR: Type of value doesn't match the expected type.\n")
                        exit(32)
                cnt += 1
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
# Funkce pro ziskani o jaky frame se jedna, nebo None pokud to neni frame
def get_frame(frame):
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
# Provedeni instrukce MOVE
def instr_move(arg1, arg2, global_frame, local_frame, temp_frame):
    # Pokud kopirujeme z jineho ramce
    frame_to = arg1.get_value()
    frame_from = arg2.get_value()
    frame_to_name = get_frame(arg1.get_value())
    frame_from_name = get_frame(arg2.get_value())

    if frame_from_name == "GF":
        if frame_to_name == "GF":
            global_frame[frame_to[3:]] = global_frame[frame_from[3:]]
        if frame_to_name == "LF":
            local_frame.copy_LF(frame_to[3:], global_frame[frame_from[3:]])
        if frame_to_name == "TF":
            temp_frame[frame_to[3:]] = global_frame[frame_from[3:]]

    elif frame_from_name == "LF":
        if frame_to_name == "GF":
            global_frame[frame_to[3:]] = local_frame.get_item(frame_from[3:])
        if frame_to_name == "LF":
            local_frame.copy_LF(frame_to[3:], local_frame.get_item(frame_from[3:]))
        if frame_to_name == "TF":
            temp_frame[frame_to[3:]] = local_frame.get_item(frame_from[3:])

    elif frame_from_name == "TF":
        if frame_to_name == "GF":
            global_frame[frame_to[3:]] = temp_frame[frame_from[3:]]
        if frame_to_name == "LF":
            local_frame.copy_LF(frame_to[3:], temp_frame[frame_from[3:]])

    else:
        if frame_to_name == "GF":
            global_frame[frame_to[3:]] = list(arg2.get_arg_type())[0], frame_from
        if frame_to_name == "LF":
            local_frame.copy_LF(frame_to[3:], list(arg2.get_arg_type())[0], frame_from)
        if frame_to_name == "TF":
            temp_frame[frame_to[3:]] = list(arg2.get_arg_type())[0], frame_from
#################################################################



#################################################################
# Definovani promenne v ramci
def def_frame(frame, global_frame, local_frame, temp_frame):
    if re.match(r"^TF@", frame[:3]):
        if temp_frame is not None:
            if frame[3:] in temp_frame:
                sys.stderr.write("ERROR: Variable is already defined.\n")
                exit(52)
            else:
                temp_frame[frame[3:]] = None, None
        else:
            sys.stderr.write("ERROR: Frame doesn't exists.\n")
            exit(55)

    if re.match(r"^LF@", frame[:3]):
        if not local_frame.get_LF():
            local_frame.create_LF_dict()
        local_frame.def_LF(frame[3:])
    if re.match(r"^GF@", frame[:3]):
        if frame[3:] in global_frame:
            sys.stderr.write("ERROR: Variable is already defined.\n")
            exit(52)
        else:
            global_frame[frame[3:]] = None, None
#################################################################

#################################################################
# Vypise na stdout
def write(obj, global_frame, local_frame, temp_frame):
    value = obj.get_args()[0].get_value()
    if("var" in obj.get_args()[0].get_arg_type()):
        frame = get_frame(value)
        if frame == "GF":
            if global_frame[value[3:]][1] is None:
                print("", end='')
            else:
                print(global_frame[value[3:]][1], end='')
        elif frame == "LF":
            print(local_frame.get_item(value[3:]), end='')
        elif frame == "TF":
            if temp_frame is not None:
                print(temp_frame[value[3:]][1], end='')
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)
    elif("bool" in obj.get_args()[0].get_arg_type()):
        print(value, end='')
    elif("nil" in obj.get_args()[0].get_arg_type()):
        print('', end='')
    else:
        print(value, end='')
#################################################################

#################################################################
def arithmetic_operation(obj, global_frame, local_frame, temp_frame):
    values = []
    first_frame = get_frame(obj.get_args()[1].get_value())
    first_operand = obj.get_args()[1].get_value()
    second_frame = get_frame(obj.get_args()[2].get_value())
    second_operand = obj.get_args()[2].get_value()

    if first_frame is None:
        values.append(first_operand)
    else:
        if first_frame == "GF":
            if global_frame[first_operand[3:]][0] == "int":
                values.append(global_frame[first_operand[3:]][1])
            else:
                sys.stderr.write("ERROR: Invalid type of argument.\n")
                exit(53)
        elif first_frame == "LF":
            if local_frame[first_operand[3:]][0] == "int":
                values.append(local_frame.get_item(first_operand[3:]))
            else:
                sys.stderr.write("ERROR: Invalid type of argument.\n")
                exit(53)
        elif first_frame == "TF":
            if temp_frame is not None:
                if temp_frame[first_operand[3:]][0] == "int":
                    values.append(temp_frame[first_operand[3:]][1])
                else:
                    sys.stderr.write("ERROR: Invalid type of argument.\n")
                    exit(53)
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)

    if second_frame is None:
        values.append(second_operand)
    else:
        if second_frame == "GF":
            if global_frame[second_operand[3:]][0] == "int":
                values.append(global_frame[second_operand[3:]][1])
            else:
                sys.stderr.write("ERROR: Invalid type of argument.\n")
                exit(53)
        elif second_frame == "LF":
            if local_frame[second_operand[3:]][0] == "int":
                values.append(local_frame.get_item(second_operand[3:]))
            else:
                sys.stderr.write("ERROR: Invalid type of argument.\n")
                exit(53)
        elif second_frame == "TF":
            if temp_frame is not None:
                if temp_frame[second_operand[3:]][0] == "int":
                    values.append(temp_frame[second_operand[3:]][1])
                else:
                    sys.stderr.write("ERROR: Invalid type of argument.\n")
                    exit(53)
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)

    # Pretypuji ciselne stringy na int
    return [int(string) for string in values]

#################################################################

#################################################################
def check_same_type(obj, global_frame, local_frame, temp_frame):
    values = []
    first_frame = get_frame(obj.get_args()[1].get_value())
    first_operand_list = list(obj.get_args()[1].get_arg_type())
    first_operand = first_operand_list[0]
    first_type = None

    if first_frame is None:
        first_type = first_operand
        values.append(obj.get_args()[1].get_value())
    else:
        if first_frame == "GF":
            first_type = type(global_frame[first_operand])
            values.append(global_frame[first_operand])
        elif first_frame == "LF":
            first_type = type(local_frame.get_item(first_operand))
            values.append(local_frame.get_item(first_operand))
        elif first_frame == "TF":
            if temp_frame is not None:
                first_type = type(temp_frame[first_operand])
                values.append(temp_frame[first_operand])
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)

    second_frame = get_frame(obj.get_args()[2].get_value())
    second_operand_list = list(obj.get_args()[2].get_arg_type())
    second_operand = second_operand_list[0]
    second_type = None

    if second_frame is None:
        second_type = second_operand
        values.append(obj.get_args()[2].get_value())
    else:
        if second_frame == "GF":
            second_type = type(global_frame[second_operand])
            values.append(global_frame[second_operand])
        elif second_frame == "LF":
            second_type = type(local_frame.get_item(second_operand))
            values.append(local_frame.get_item(second_operand))
        elif second_frame == "TF":
            if temp_frame is not None:
                second_type = type(temp_frame[second_operand])
                values.append(temp_frame[second_operand])
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)
    if first_type == second_type:
        return values
    else:
        sys.stderr.write("ERROR: Different types of operands.\n")
        exit(53)
#################################################################
def get_type(obj, global_frame, local_frame, temp_frame):
    values = []
    frame = get_frame(obj.get_args()[1].get_value())
    var = obj.get_args()[1].get_value()
    operand_list = list(obj.get_args()[1].get_arg_type())
    operand = operand_list[0]

    if frame is None:
        values.append(operand)
    else:
        if frame == "GF":
            values.append(global_frame[var[3:]][0])
        elif frame == "LF":
            values.append(local_frame.get_type(var[3:]))
        elif frame == "TF":
            if temp_frame is not None:
                values.append(temp_frame[var[3:]][0])
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)
    return values
#################################################################

#################################################################
def is_bool(value):
    return re.match(r"^(true|false)$", str(value))

#################################################################
def logical_operation(obj, global_frame, local_frame, temp_frame):
    values = []
    first_frame = get_frame(obj.get_args()[1].get_value())
    first_operand = obj.get_args()[1].get_value()

    if not(obj.get_opcode() == "NOT"):
        second_frame = get_frame(obj.get_args()[2].get_value())
        second_operand = obj.get_args()[2].get_value()

    if first_frame is None:
        if first_operand == "true":
            values.append(True)
        else:
            values.append(False)
    else:
        if first_frame == "GF":
            if is_bool(global_frame[first_operand[3:]]):
                if global_frame[first_operand[3:]] == "true":
                    values.append(True)
                else:
                    values.append(False)
            else:
                sys.stderr.write("ERROR: Invalid type of argument.\n")
                exit(53)
        elif first_frame == "LF":
            if is_bool(local_frame[first_operand[3:]]):
                if local_frame.get_item(first_operand[3:]) == "true":
                    values.append(True)
                else:
                    values.append(False)
            else:
                sys.stderr.write("ERROR: Invalid type of argument.\n")
                exit(53)
        elif first_frame == "TF":
            if temp_frame is not None:
                if is_bool(temp_frame[first_operand[3:]]):
                    if temp_frame[first_operand[3:]] == "true":
                        values.append(True)
                    else:
                        values.append(False)
                else:
                    sys.stderr.write("ERROR: Invalid type of argument.\n")
                    exit(53)
            else:
                sys.stderr.write("ERROR: Frame doesn't exists.\n")
                exit(55)

    if not(obj.get_opcode() == "NOT"):
        if second_frame is None:
            if second_operand == "true":
                values.append(True)
            else:
                values.append(False)
        else:
            if second_frame == "GF":
                if is_bool(global_frame[second_operand[3:]]):
                    if global_frame[second_operand[3:]] == "true":
                        values.append(True)
                    else:
                        values.append(False)
                else:
                    sys.stderr.write("ERROR: Invalid type of argument.\n")
                    exit(53)
            elif second_frame == "LF":
                if is_bool(local_frame[second_operand[3:]]):
                    if local_frame.get_item(second_operand[3:]) == "true":
                        values.append(True)
                    else:
                        values.append(False)
                else:
                    sys.stderr.write("ERROR: Invalid type of argument.\n")
                    exit(53)
            elif second_frame == "TF":
                if temp_frame is not None:
                    if is_bool(temp_frame[second_operand[3:]]):
                        if temp_frame[second_operand[3:]] == "true":
                            values.append(True)
                        else:
                            values.append(False)
                    else:
                        sys.stderr.write("ERROR: Invalid type of argument.\n")
                        exit(53)
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
    return values
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
# Nacteni z XML souboru, kdy se nejdriv i zavola funkce pro kontrolu
def tree_load(global_frame, local_frame, temp_frame):
    instruction_list = []
    try:
        ET.parse(source_file)
    except:
        sys.stderr.write("ERROR: Bad XML format or XML file.\n")
        exit(31)

    tree = ET.parse(source_file)
    root = tree.getroot()
    tree_check(root)
    i = 0
    for child in root:
        instruct_keys = list(child.attrib.values())
        instruction_list.append(Instruction(instruct_keys[1].upper(), instruct_keys[0]))
        add_arg(child, instruction_list[i])
        i += 1
        instruction_list.sort(key=lambda x: int(x.get_order()))

    for instruction in instruction_list:
        # Prvni pozice je order, na druhe je opcode
        if 'MOVE' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"])
            instr_move(instruction.get_args()[0], instruction.get_args()[1], global_frame, local_frame, temp_frame)
            continue

        if 'CREATEFRAME' == instruction.get_opcode():
            instruction.check_num_args(0)
            # Vytvori prazdny docasny ramec
            temp_frame = {}
            continue

        if 'PUSHFRAME' == instruction.get_opcode():
            instruction.check_num_args(0)
            # Vytvori prazdny docasny ramec
            if temp_frame is None:
                sys.stderr.write("ERROR: Undefined temporary frame.\n")
                exit(55)
            # Pokud neni temporary frame prazdny, tak ho vloz na stack
            if temp_frame != {}:
                local_frame.create_LF_dict()
                if list(temp_frame.values())[0] is None:
                    local_frame.push_new_LF(list(temp_frame.keys())[0], None, None)
                    temp_frame = None
                else:
                    local_frame.push_new_LF(list(temp_frame.keys())[0], list(temp_frame.values())[0][0], list(temp_frame.values())[0][1])
                    temp_frame = None
            else:
                sys.stderr.write("ERROR: Empty temporary frame.\n")
                exit(55)
            continue

        if 'POPFRAME' == instruction.get_opcode():
            instruction.check_num_args(0)
            # Vlozim frame do temporary framu
            temp_frame = local_frame.pop_LF()
            continue

        if 'DEFVAR' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, "var")
            def_frame(instruction.get_args()[0].get_value(), global_frame, local_frame, temp_frame)
            continue

        if 'CALL' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, "label")
            continue

        if 'RETURN' == instruction.get_opcode():
            instruction.check_num_args(0)
            type_check(instruction)
            continue

        if 'PUSHS' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, ["int", "string", "bool", "nil", "var"])
            continue

        if 'POPS' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, "var")
            continue

        if 'ADD' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "var"], ["int", "var"])
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            values = arithmetic_operation(instruction, global_frame, local_frame, temp_frame)
            result = values[0] + values[1]
            if frame == "GF":
                global_frame[var[3:]] = "int", result
            if frame == "LF":
                local_frame.push_LF(var[3:], "int", result)
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = "int", result
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'SUB' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "var"], ["int", "var"])
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            values = arithmetic_operation(instruction, global_frame, local_frame, temp_frame)
            result = values[0] - values[1]
            if frame == "GF":
                global_frame[var[3:]] = "int", result
            if frame == "LF":
                local_frame.push_LF(var[3:], "int", result)
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = "int", result
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'MUL' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "var"], ["int", "var"])
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            values = arithmetic_operation(instruction, global_frame, local_frame, temp_frame)
            result = values[0] * values[1]
            if frame == "GF":
                global_frame[var[3:]] = "int", result
            if frame == "LF":
                local_frame.push_LF(var[3:], "int", result)
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = "int", result
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'IDIV' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "var"], ["int", "var"])
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            values = arithmetic_operation(instruction, global_frame, local_frame, temp_frame)
            if values[1] == 0:
                sys.stderr.write("ERROR: Can't divide by 0.\n")
                exit(57)
            # Diky // bude vysledek zase int
            result = values[0] // values[1]
            if frame == "GF":
                global_frame[var[3:]] = "int", result
            if frame == "LF":
                local_frame.push_LF(var[3:], "int", result)
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = "int", result
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'LT' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "string", "bool", "var"], ["int", "string", "bool", "var"])
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            values = check_same_type(instruction, global_frame, local_frame, temp_frame)
            if frame == "GF":
                global_frame[var[3:]] = "bool", values[0] < values[1]
            if frame == "LF":
                local_frame.push_LF(var[3:], "bool", values[0] < values[1])
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = "bool", values[0] < values[1]
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'GT' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "string", "bool", "var"], ["int", "string", "bool", "var"])
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            values = check_same_type(instruction, global_frame, local_frame, temp_frame)
            if frame == "GF":
                global_frame[var[3:]] = "bool", values[0] > values[1]
            if frame == "LF":
                local_frame.push_LF(var[3:], "bool", values[0] > values[1])
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = "bool", values[0] > values[1]
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'AND' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["bool", "var"], ["bool", "var"])
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            values = logical_operation(instruction, global_frame, local_frame, temp_frame)
            if frame == "GF":
                global_frame[var[3:]] = "bool", values[0] and values[1]
            if frame == "LF":
                local_frame.push_LF(var[3:], "bool", values[0] and values[1])
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = "bool", values[0] and values[1]
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'OR' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["bool", "var"], ["bool", "var"])
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            values = logical_operation(instruction, global_frame, local_frame, temp_frame)
            if frame == "GF":
                global_frame[var[3:]] = "bool", values[0] or values[1]
            if frame == "LF":
                local_frame.push_LF(var[3:], "bool", values[0] or values[1])
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = "bool", values[0] or values[1]
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'NOT' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["bool", "var"])
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            values = logical_operation(instruction, global_frame, local_frame, temp_frame)
            if frame == "GF":
                global_frame[var[3:]] = "bool", not(values[0])
            if frame == "LF":
                local_frame.push_LF(var[3:], "bool", not(values[0]))
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = "bool", not(values[0])
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'INT2CHAR' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"])
            continue

        if 'STRI2INT' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, ["int", "string", "bool", "nil", "var"], ["int", "string", "bool", "nil", "var"])
            continue

        if 'READ' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", "type")
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            read_value = input()
            type = instruction.get_args()[1].get_value()

            if type == "bool":
                if re.match(r"true", read_value, flags=re.IGNORECASE):
                    read_value = "true"
                else:
                    read_value = "false"

            if not read_value:
                read_value = "nil"
                type = "nil"

            if frame == "GF":
                global_frame[var[3:]] = type, read_value
            if frame == "LF":
                local_frame.push_LF(var[3:], type, read_value)
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = type, read_value
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'WRITE' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, ["int", "string", "bool", "nil", "var"])
            write(instruction, global_frame, local_frame, temp_frame)
            continue

        if 'CONCAT' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"], ["int", "string", "bool", "nil", "var"])
            continue

        if 'STRLEN' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"])
            continue

        if 'GETCHAR' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"], ["int", "string", "bool", "nil", "var"])
            continue

        if 'SETCHAR' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"], ["int", "string", "bool", "nil", "var"])
            continue

        if 'TYPE' == instruction.get_opcode():
            instruction.check_num_args(2)
            instruction.check_valid_num_args(2)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"])
            var = instruction.get_args()[0].get_value()
            frame = get_frame(instruction.get_args()[0].get_value())
            values = get_type(instruction, global_frame, local_frame, temp_frame)
            if frame == "GF":
                global_frame[var[3:]] = values[0], values[0]
            if frame == "LF":
                local_frame.push_LF(var[3:], values[0], values[0])
            if frame == "TF":
                if temp_frame is not None:
                    temp_frame[var[3:]] = values[0], values[0]
                else:
                    sys.stderr.write("ERROR: Frame doesn't exists.\n")
                    exit(55)
            continue

        if 'LABEL' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, "label")
            continue

        if 'JUMPIFNEQ' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "label", ["int", "string", "bool", "nil", "var"], ["int", "string", "bool", "nil", "var"])
            continue

        if 'JUMPIFEQ' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "label", ["int", "string", "bool", "nil", "var"], ["int", "string", "bool", "nil", "var"])
            continue

        if 'EQ' == instruction.get_opcode():
            instruction.check_num_args(3)
            instruction.check_valid_num_args(3)
            type_check(instruction, "var", ["int", "string", "bool", "nil", "var"], ["int", "string", "bool", "nil", "var"])
            continue

        if 'JUMP' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, "label")
            continue

        if 'EXIT' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, ["int", "string", "bool", "nil", "var"])
            if 0 <= int(instruction.get_args()[0].get_value()) <= 49:
                exit(int(instruction.get_args()[0].get_value()))
            else:
                sys.stderr.write("ERROR: Invalid exit code.\n")
                exit(57)
            continue

        if 'DPRINT' == instruction.get_opcode():
            instruction.check_num_args(1)
            instruction.check_valid_num_args(1)
            type_check(instruction, ["int", "string", "bool", "nil", "var"])
            continue

        if 'BREAK' == instruction.get_opcode():
            instruction.check_num_args(0)
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
