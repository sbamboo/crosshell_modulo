%parent% / {parent} in cmdlet .cfg files
way to iter over list, ex: "addOne *[0,1,2,3] -> [1,2,3,4]" or "set list [0,1,3,4]; addOne *| get list -> [1,2,3,4]"
fast var yield, ex: func $var -> $var (-> : yeild-operator,  -> $var : -> set var,   func $var -> $var : func | get var -> set var)
expand pipe, ex: <| or |> ([0,1,2,3] |> func1,func2,func3,func4 -> [x,y,z,a]


Yeild operator:
  ->
 Var:
  func $var -> $var       :        get var | func | set var
 Func:
  func $var -> func2      :        get var | func | func2

Indexing:
  [i]
 Var:
  $var[0]                 :         get var | atIndex 0
  $var[1] = <value>       :         setAtIndex var <value> 1
 Func:
  func[0]                 :         func | atIndex 0

Expand operator:
  *
 Var:
   $list                   :        get list | expand
   func *$list             :        func | get list | expand
   $list = *func           :        func | expand | set list
 Func:
   *func                   :        func | expand

Concat operator:
  <
 Var:
   <$list                  :        get list | concat
 Func:
   <func                   :        func | concat

Expand Pipe:
  *|
 Var:
  func *| $list            :        get list | expand | func
  *list | func
 Func:
  func *| func2            :        func2 | expand | func

Expand Pipe:
  <| / |>
 Var:
  func <| $list            : -      func $list[0] $list[1] (...Xlen(list))