advwhile/advforeach (<PyCondition>) {
  <Input-Commands>
}

#advwhile/advforeach > pyCondition(Condition) > parse(<Input-Commands>)
# pyConditon executes/validates the pythonCondition and returns True/False/<int>/<thing>

while/foreach (<NativeCondition>) {
  <Input-Commands>
}

#while/foreach > condition(Condition) > parse(<Input-Commands>)
# condition executes the input and returns checks its return values and returns True/False/<int>/<thing>

foreach creates "curObj" which is the functions currentObject and is a Crosshell.Variable