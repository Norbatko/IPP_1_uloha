<?php
#REGEX
    # <var> => ^(LF|TF|GF)@[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$
    # bool => bool@(true|false)$
    # nil => ^nil@nil$
    # int => ^int@((?:0$)|(?:\-{0,1}[1-9][0-9]*$))
    # string => string@[^]
declare(strict_types=1);

use function PHPSTORM_META\type;

ini_set('display_errors', 'stderr');

$header = false;
$order = 1;


function instruction_set($opcode, $order, $type, $arg_num, ...$args) {
    $instruction = new Instruction($opcode, $order, $type, $arg_num, ...$args);
    $instruction->instruction_print_start();
    $instruction->arg_print();
    $instruction->instruction_print_end();
    global $order;
    $order++;
}

function type_check($type) {
    if(preg_match('/^bool@(true|false)$/m', $type)) {
        return "symb";
    } else if(preg_match('/^int@((?:0$)|(?:\-{0,1}[1-9][0-9]*$))/m', $type)) {
        return "symb";
    } else if(preg_match('/^nil@nil$/m', $type)) {
        return "symb";
    // } else if(preg_match('', $type)) {
    //     return "symb";
    } else if (preg_match('/^(LF|TF|GF)@[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$/m',$type)) {
        return "var";
    } else {
        exit(23);
    }
}

function symb_separ($type) {
    return $out = explode("@", $type);
}

// function var_check($type) {
//     // preg_match_all($re, $str, $matches, PREG_SET_ORDER, 0);
//     if(preg_match('/(LF|TF|GF)@[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$/m',$type)) {
//         return true;
//     } else {
//         exit(23);
//     }
// }

function var_split($type) {
    $tmp = strpos($type, '&');
    if($tmp != FALSE) {
        $split = explode('&', $type);
        return $out = $split[0]."&amp;".$split[1];
    }
    $tmp = strpos($type, '<');
    if($tmp != FALSE) {
        $split = explode('<', $type);
        return $out = $split[0]."&lt;".$split[1];
    }
    $tmp = strpos($type, '>');
    if($tmp != FALSE) {
        $split = explode('>', $type);
        return $out = $split[0]."&gt;".$split[1];
    }
    return $type;
}

function label_check($type) {
    
    if(preg_match('/^[a-zA-Z_\-$&%*!?][a-zA-Z_\-$&%*!?0-9]*$/m', $type)) {
        return true;
    } else {
        exit(23);
    }
}

function check_args($argv, $argc) {
    if($argc == 2) {
        if($argv[1] == "--help") {
            echo "parse.php";
            exit(0);
        }
    } else {
        exit(10);
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
    public $args;
    public $arg_num;

    public function __construct($opcode, $order, $type, $arg_num, ...$args) {
        $this->opcode = $opcode;
        $this->order = $order;
        $this->type = $type;
        $this->arg_num = $arg_num;
        $this->args = array();
        foreach($args as $i) {
            $this->args[] = $i;
        }
    }

    public function instruction_print_start() {
        echo "\t<instruction order=\"".$this->order."\" opcode=\"".$this->opcode."\">\n";
    }

    public function arg_print() {
        for($i = 0; $i < $this->arg_num; $i++) {
            if ($this->args[$i] != NULL) {
                
                echo "\t\t<arg".($i+1)." type=\"".$this->type."\">".$this->args[$i]."</arg".($i+1).">\n";
            }
        }
    }

    public function instruction_print_end() {
        echo "\t</instruction>\n";
    }
}



// $hello = new Instruction("WRITE", "1", "var", "GF@a", "arg1");



while ($line = fgets(STDIN)) {
    $line = preg_replace('/\s*#.*/m','',$line); //removing comments from line
    $split = explode(" ", trim($line, "\n"));
    $len = count($split);
    for($i = 0; $i < $len; $i++) {
        if($split[$i] === '') {
            unset($split[$i]);
        }
    }
    $split = array_values($split);
    $len = count($split);
    
    if($split == NULL) {    //there was only blank line or comment
        continue;
    }

    if ($header == false) {
        // for($i = 0; $i < $len; $i++) {  //going though the all splits (even '')
            if ($split[0] == ".IPPcode23") {
                $header = true;
                echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n";
                echo("<program language=\"IPPcode23\">\n");
                continue;
            // } else if($split[$i] == '') {
            //     continue;
            } else {
                exit(21);
            }
        // }
        continue;
    }

    switch(strtoupper($split[0])) {
        
        // without argument
        case "CREATEFRAME":
        case "PUSHFRAME":
        case "POPFRAME":
        case "RETURN":
        case "BREAK":
            if ($len == 1) {
                instruction_set(strtoupper($split[0]), $order, NULL, NULL, NULL);
            } else {
                exit(23);
            }
            break;
        
        // 1 argument => var
        case "DEFVAR":
        case "POPS":
            if($len == 2) {
                if(type_check($split[1]) == "var") {
                    $split[1] = var_split($split[1]);
                    instruction_set(strtoupper($split[0]), $order, "var", 1, $split[1]);
                } else {
                    exit(23);
                }
            } else {
                exit(23);
            }
            break;

        // 1 argument => label
        case "CALL":
        case "LABEL":
        case "JUMP":
            // if ($len == 1) {
            //     instruction_set(strtoupper($split[0]), $order, NULL, NULL, NULL);
            // } else 
            if ($len == 2){
                if (label_check($split[1])) {
                    instruction_set(strtoupper($split[0]), $order, "label", 1, $split[1]);
                }
            } else {
                exit(23);
            }
            break;

        // 1 argument => symb    
        case "PUSHS":
        case "WRITE":
        case "EXIT":
        case "DPRINT":
            if($len == 2) {
                if(type_check($split[1]) == "symb") {
                    $out = symb_separ($split[1]);
                    instruction_set(strtoupper($split[0]), $order, $out[0], 1, $out[1]);
                } else if (type_check($split[1]) == "var") {
                    instruction_set(strtoupper($split[0]), $order, "var", 1, $split[1]);
                }
            } else {
                exit(23);
            }
            break;

        // 2 arguments => var, symb
        case "MOVE":
        case "INT2CHAR":
        case "STRLEN":
        case "TYPE":
            if ($len == 3) {
                if(type_check($split[1]) == "var") {
                    $split[1] = var_split($split[1]);
                    if (type_check($split[2]) == "symb") {
                        instruction_set(strtoupper($split[0]), $order, "var", 1, $split[1]);
                        $out = symb_separ($split[2]);
                        instruction_set(strtoupper($split[0]), $order, $out[0], 2, $out[1]);
                    } else if (type_check($split[2]) == "var") {
                        $split[2] = var_split($split[2]);
                        instruction_set(strtoupper($split[0]), $order, "var", 2, $split[1], $split[2]);
                        //instruction_set(strtoupper($split[0]), $order, "var", $split[2], 2);
                    }
                }
            } else {
                exit(23);
            }
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
            if ($len == 4) {
                if(type_check($split[1]) == "var") {
                    $split[1] = var_split($split[1]);
                    if (type_check($split[2]) == "symb") {
                        if(type_check($split[3]) == "symb") {
                            instruction_set(strtoupper($split[0]), $order, "var", 3, $split[1]);
                            $out = symb_separ($split[2]);
                            instruction_set(strtoupper($split[0]), $order, $out[0], 2, $out[1]);
                            $out = symb_separ($split[3]);
                            instruction_set(strtoupper($split[0]), $order, $out[0], 3, $out[1]);
                        }
                    }
                }
            } else {
                exit(23);
            }
            break;
        
        // 3 arguments => label, symb1, symb2    
        case "JUMPIFEQ":
        case "JUMPIFNEQ":
            break;

        default:
            exit(22);
    }
}

echo "</program>"
?>