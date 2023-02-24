<?php
#REGEX
    # <var> => [LF|TF|GF]@[a-zA-Z_-$&%*!?][a-zA-Z_-$&%*!?0-9]*
    # bool => bool@(true|false)$
    # nil => nil@nil
    # int => (?:^0$)|(?"^\-{0,1}[1-9]+$)
    # string => 
declare(strict_types=1);


ini_set('display_errors', 'stderr');

$header = false;
$arg_num = 1;
$order = 1;


function instruction_set($opcode, $order, $type, $arg, $arg_num) {
    $instruction = new Instruction($opcode, $order, $type, $arg, $arg_num);
    $instruction->instruction_print_start();
    $instruction->arg_print();
    $instruction->instruction_print_end();
    global $order;
    $order++;
}

function is_type($type) {
    if($type == "bool@(true|false)") {
        
    }
}

function check_args($argv, $argc) {
    if($argc == 2) {
        if($argv[1] == "--help") {
            echo "parse.php";
            exit(0);
        }
    }
}

function check_param ($given, $correct) {
    if ($given == $correct) {
        return 0;
    } else {
        return 1;
    }
}


class Instruction {
    public $opcode;
    public $order;
    public $type;
    public $arg;
    public $arg_num;

    public function __construct($opcode, $order, $type, $arg, $arg_num) {
        $this->opcode = $opcode;
        $this->order = $order;
        $this->type = $type;
        $this->arg = $arg;
        $this->arg_num = $arg_num;
    }

    public function instruction_print_start() {
        echo "\t<instruction order=\"".$this->order."\" opcode=\"".$this->opcode."\">\n";
    }

    public function arg_print() {
        if ($this->arg != NULL) {
            echo "\t\t<arg".$this->arg_num." type=\"".$this->type."\">".$this->arg."</arg".$this->arg_num.">\n";
        }
    }

    public function instruction_print_end() {
        echo "\t</instruction>\n";
    }
}



// $hello = new Instruction("WRITE", "1", "var", "GF@a", "arg1");



while ($line = fgets(STDIN)) {
    $split = explode(" ", trim($line, "\n"));
    $len = count($split);
    if ($header == false) {
        if ($split[0] == ".IPPcode23") {
            $header = true;
            echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
            echo("<program language=\"IPPcode23\">\n");
        } else {
            exit(21);
        }
    }

    switch(strtoupper($split[0])) {
        // without argument
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            instruction_set(strtoupper($split[0]), $order, NULL, NULL, NULL);
            break;
        // 1 argument => var
        case "DEFVAR":
        case "POPS":
            
            break;

        // 1 argument => label
        case "CALL":
        case "LABEL":
        case "JUMP":
            if ($len == 1) {
                instruction_set(strtoupper($split[0]), $order, NULL, NULL, NULL);
            } else {
                instruction_set(strtoupper($split[0]), $order, "label", $split[1], 1);
            }
            
            break;

        // 1 argument => symb    
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            break;

        // 2 arguments => var, symb
        case "MOVE":
        case "INT2CHAR":
        case "STRLEN":
        case "TYPE":
            break;
        
        // 2 arguments => var, type
        case "READ":
            break;
        
        // 3 arguments => var, symb1, symb2
        case "ADD":
        case "SUB":
        case "MUL":
        case "IDIV":
        case "LT":  //its the same as EQ => falling through on purpose
        case "GT":  //its the same as EQ => falling through on purpose
        case 'EQ':
        case "AND": //its the same as NOT => falling through on purpose
        case "OR":  //its the same as NOT => falling through on purpose
        case "NOT":
        case "STRI2INT":
        case "CONCAT":
        case "GETCHAR":
        case "SETCHAR":
            break;
        
        // 3 arguments => label, symb1, symb2    
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            break;

        default:
    }
}

echo "</program>"
?>