<?php
#REGEX
    # <var> => [LF|TF|GF]@[a-zA-Z_-$&%*!?][a-zA-Z_-$&%*!?0-9]*
declare(strict_types=1);

ini_set('display_errors', 'stderr');

$header = false;

if ($argc == 2) {
    if ($argv[1] == "--help") {
        printf("Hello\n");
        return 0;
    }

}

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>";

while ($line = fgets(STDIN)) {
    $split = explode(" ", trim($line, "\n"));
    if ($header == false) {
        if ($split[0] == ".IPPcode23") {
            $header = true;
            echo("<program language=\"IPPcode23\">");
        }
    }

    switch(strtoupper($split[0])) {
        case "MOVE":
            break;
        case "CREATERFRAME":
            break;
        case "PUSHFRAME":
            break;
        case "POPFRAME":
            break;
        case "DEFVAR":
            break;
        case "CALL":
            break;
        case "RETURN":
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
        case "BREAK":
            break;
        default:
    }
}
?>