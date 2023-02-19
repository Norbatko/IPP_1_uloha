<?php
#REGEX
    # <var> => [LF|TF|GF]@[a-zA-Z_-$&%*!?][a-zA-Z_-$&%*!?0-9]*
declare(strict_types=1);

ini_set('display_errors', 'stderr');

$header = false;
$arg_num = 1;
$order = 1;

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
        if ($this->type != NULL) {
            echo "\t\t<".$this->arg_num." type=\"".$this->type."\">".$this->arg."</".$this->arg_num.">\n";
        }
    }

    public function instruction_print_end() {
        echo "\t</instruction>\n";
    }
}



// $hello = new Instruction("WRITE", "1", "var", "GF@a", "arg1");



while ($line = fgets(STDIN)) {
    $split = explode(" ", trim($line, "\n"));
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
        
        case "CREATERFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            $instruction = new Instruction($split[0], $order, NULL, NULL, NULL);
            $instruction->instruction_print_start();
            $instruction->arg_print();
            $instruction->instruction_print_end();
            $order++;
            break;

        case "MOVE":
            break;
        case "DEFVAR":
            break;
        case "CALL":
            break;
        
        case "PUSHS":
            break;
        case "POPS":
            break;
        case "ADD":
            break;
        case "SUB":
            break;
        case "MUL":
            break;
        case "IDIV":
            break;
        case "LT":  //its the same as EQ => falling through on purpose
        case "GT":  //its the same as EQ => falling through on purpose
        case 'EQ':
            break;
        case "AND": //its the same as NOT => falling through on purpose
        case "OR":  //its the same as NOT => falling through on purpose
        case "NOT":
            break;
        case "INT2CHAR":
            break;
        case "STRI2INT":
            break;
        case "READ":
            break;
        case "WRITE":
            break;
        case "CONCAT":
            break;
        case "STRLEN":
            break;
        case "GETCHAR":
            break;
        case "SETCHAR":
            break;
        case "TYPE":
            break;
        case "LABEL":
            break;
        case "JUMP":
            break;
        case "JUMPIFEQ":
            break;
        case "JUMPIFNEQ":
            break;
        case "EXIT":
            break;
        case "DPRINT":
            break;
        
        default:
    }
}

echo "</program>"
?>