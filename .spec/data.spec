list   : []
string : ""
int    : 0
json   : {"msg":"hi joseph"}


$list = ["string",0]         >> set list '["string",0]'
$string = "hi"               >> set string '"hi"'
$int = 0                     >> set int '0'
$json = {"msg":"hi joseph"}  >> set json '{"msg":"hi joseph"}'

$list   >> get list
$string >> get string
$int    >> get int
$json   >> get json

$list =| getColorList >> getColorList | set list 

$list =| getColor | convList >>  getColor | convList | set list

$list § getColor | convList   >> getColor | convList | set list