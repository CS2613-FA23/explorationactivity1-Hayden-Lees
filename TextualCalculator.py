import re
import numpy as np

#global regex CONSTANTS 
INITIAL_REG = re.compile(r"""
                  ^\s*((?P<exit>exit|close|esc|escape|$)| #terminates program
                  (?P<help>help|cmds?|commands?)| #list how to use this textual calculator
                  (?P<eval>eval(uate)?|what\ (is|does))| #evaluates the given equation. Returns int or float
                  (?P<bool>truth|bool|(?<!what)(is|does))| #evaluates the truth of a boolean on two equations. Returns true or false
                  (?P<comp>compare))\s* #evaluates the whether the first is greater than, equal, or less than the second equation. Returns "greater than", "equal", "less than"
                  (?P<rest>.+)?$ #the rest of the given string""", re.X)
EVALUATE_REG = re.compile(r""" 
                        ^\s*
                        (?P<open>\(+)?\s* #for ordering operations
                        (?P<operand>(?P<func_name>[a-z_0-9]+)\((?P<func_value>.+?\)?)\)|(\d+(\.\d+)?|pi|e|ans))\s* #function of a value or just a value
                        (?P<close>\)+)?\s* #for ordering operations
                        (?P<sop_operators>[!])?\s* #some simple 1 operand operators
                        (?P<mop_operators>[+\-*/^%])?\s* #some simple 2 operand operators
                        (?P<rest>.+)?$ #the rest of the equation""", re.X)
TRUTH_REG = re.compile(r"""
                        ^\s*
                        (?P<first>.+?)\s* #the first equation to evaluate
                        (?P<comp><=?|>=?|!?=|greater\ than(\ or\ equal\ to)?|less\ than(\ or\ equal\ to)?|(not\ )?equal\ to)\s* #how to compare the results
                        (?P<second>.+)\s*$ #the second equation to evaluate""", re.X)
COMPARE_REG = re.compile(r"""
                        ^\s*
                        (?P<first>.+?)\s* #the first equation to evaluate
                        (and|\||&)\s* #when the first changes to the second
                        (?P<second>.+)\s*$ #the second equation to evaluate""", re.X)

#global non-regex CONSTANTS
HELPSTR = """
This is a text based calculator.

Currently it has three options:
    1. it can evaluate a single equation a return the answer (ex: 2^3/5 returns 1.6),
    2. it can evaluate a condition statement and return whether it is true or not 
    (ex: 2^3 > 3^2 returns false),
    3. and it can compare two equations and it will return whether the first is 
       greater, less, or equal to the second (ex: 4! and 7*3 returns 4! > 7*3)

An equation can currently consists of + - * / ^ % !, any trig, hypertrig, inverse trig, 
any float/int (ex: 5.0, 2), and values like pi, e, and even the answer of last evaluation (ans). You can use () to give
the equation order, and it follows PEDMAS otherwise. Uses radians.

To exit the calculator, you can type "exit", "close", "esc", "escape", or simply nothing
"""
ORDERDICT = {"+":1, "-":1,"*":2, "/":2, "%":2,"^":3,"!":4} #This is used to tell the program which operator goes when
DELTA = 1e-15 #This is used to fix the floating point error that happens with trig functions

#error messages
ERR_MISSING_REST = "ERROR: Needs something to evaluate"
ERR_UNKNOWN_CMD = "ERROR: Unknown question/cmd"
ERR_UNKNOWN_FN = "ERROR: Not a known function name"
ERR_FORMATTING = "ERROR: Invalid equation formatting"
ERR_UNBALANCED = "ERROR: Unbalanced ()"
ERR_COMPARE = "ERROR: Invalid compare statement"
ERR_TRUTH = "ERROR: Invalid truth statement"
WARN_FACTORIAL = "WARNING: The current factorial function (!) truncates the value given to it into a int"

#global non-regex variables
prev_ans = 0 #the answer of the last evaluate command

#functions
def factorial(x: int): #A simple factorial function
        out = 1
        for z in range(x): out *= x-z
        return out
def fix_float_error(x): #fixes float error 
        if (type(x) == str): return x
        if (np.round(x)-x < DELTA): return np.round(x)
        return x
def recursive_read(s: str, reg: re.Pattern, rec: str): #recusively checks a string using the given regex and the recursive group string
    m = reg.search(s)                                  #checks the string (s) with the regex
    if m:                                              #if it matched anything
        m_list = [m]                                   #makes a list of the matches for later comprehension
        if m[rec] != None:                             #checks if the match has more of the recursive pattern
            nex = recursive_read(m[rec], reg, rec)     #the recursive call
            if nex == None: return m_list              #if the rec pattern does not match anything
            for i in nex: m_list.append(i)             #adds all of the recursive matches to this levels list
        return m_list
    return None
def recursive_eq_eval(ands: list, ors: list): #Uses the lists generated from reading the matches from the above function to get the answer
    for i in range(len(ands)):                                          #goes through all of the operands to find the ones that are in ()
        if (type(ands[i]) == list):                                     #if we find a ()
            ands[i] = recursive_eq_eval(ands[i], ors[i])                #the recursive call of the () values
            if (ands[i] == ERR_FORMATTING): return ERR_FORMATTING       #ends if error is occurred
            ors.pop(i)                                                  #removes the evaluated operator
    if (len(ors) == 1):                                                 #if there is only 1 operator left
        if (len(ands) == 1 and ors[0] != "!"): return ERR_FORMATTING    #if there aren't enough operands
        match ors[0]:                                                   #does the operation
            case "+": return float(ands[0]) + float(ands[1])            #
            case "-": return float(ands[0]) - float(ands[1])            #
            case "*": return float(ands[0]) * float(ands[1])            #
            case "/": return float(ands[0]) / float(ands[1])            #
            case "%": return float(ands[0]) % float(ands[1])            #
            case "^": return float(ands[0]) ** float(ands[1])           #
            case "!":                                                   #
                print(WARN_FACTORIAL)                                   #
                return factorial(int(ands[0]))                          #
    else:                                                               #figures out the order of the operators
        index = 0                                                       #
        maxord = 0                                                      #
        for i in range(len(ors)):                                       #
            if type(ors[i]) == list: continue                           #
            if (ORDERDICT[ors[i]] > maxord):                            #
                maxord = ORDERDICT[ors[i]]                              #
                index = i                                               #
        if (ors[index] == "!"): ands[index] = [ands[index]]             #effectively adds () to the operands and operator that need to go first
        else: ands[index:index+2] = [ands[index:index+2]]               #
        ors[index] = [ors[index]]                                       #
        return recursive_eq_eval(ands, ors)                             #
def fn_evaluate(fn_name: str, value): #Evaluates functions
    match fn_name:
        case "sin": return np.sin(value)
        case "sinh": return np.sinh(value)
        case "arcsin": return np.arcsin(value)
        case "arcsinh": return np.arcsinh(value)
        case "cos": return np.cos(value)
        case "cosh": return np.cosh(value)
        case "arccos": return np.arccos(value)
        case "arccosh": return np.arccosh(value)
        case "tan": return np.tan(value)
        case "tanh": return np.tanh(value)
        case "arctan": return np.arctan(value)
        case "arctanh": return np.arctanh(value)
        case "csc": return np.csc(value)
        case "csch": return np.csch(value)
        case "arccsc": return np.arccsc(value)
        case "arccsch": return np.arccsch(value)
        case "sec": return np.sec(value)
        case "sech": return np.sech(value)
        case "arcsec": return np.arcsec(value)
        case "arcsech": return np.arcsech(value)
        case "cot": return np.cot(value)
        case "coth": return np.coth(value)
        case "arccot": return np.arccot(value)
        case "arccoth": return np.arccoth(value)
        case _: return ERR_UNKNOWN_FN
def fix_operands(lst: list): #This fixes any operands so that they are a float/int
    for x in range(len(lst)):                                       #goes through the operands to make sure they are correct 
        match lst[x]:                                               #
            case "(": return ERR_UNBALANCED                         #if at the end there is still a ( remaining it wasn't closed so it returns the unbalanced error
            case "pi": lst[x] = np.pi                               #turns the str "pi" into the value of pi
            case "e": lst[x] = np.e                                 #turns the str "e" into the value of e
            case "ans": lst[x] = prev_ans                           #turns the str "ans" into the previous answer
            case _ if type(lst[x]) != list: lst[x] = float(lst[x])  #turns any remaining str into its float equivalent
            case _:                                                 #
                fix = fix_operands(lst[x])                          #
                if type(fix) == str: return fix                     #
                lst[x] = fix                                        #
    return lst                                                      #
def eq_evaluate(s: str): #Uses the regs to parse the operands & operators from the matches returned from recursive_read for the recursive_eq_eval
    operands = []                                                                           #a list of the operands
    operators = []                                                                          #a list of the operators
    contents = recursive_read(s, EVALUATE_REG, "rest")                                      #gets a list of the matches
    if contents:                                                                            #if there are any matches at all
        for m in contents:                                                                  #goes through the matches in order
            if m:                                                                           #if the match is not empty
                if (m["open"] != None):                                                     #does the match have an open (
                    for c in m["open"]:                                                     #add the amount of ( to both lists
                        operands.append(c)                                                  #
                        operators.append(c)                                                 #
                if (m["func_value"] != None and m["func_name"] != None):                    #checks if the match has a function
                    val_of_func = eq_evaluate(m["func_value"])                              #simplyfies the function value to a float
                    if (type(val_of_func) == str): return val_of_func                       #ends if an error is returned from the function value
                    operand = fn_evaluate(m["func_name"], val_of_func)                      #evaluates the function
                    if (type(operand) == str): return operand                               #ends if an error is returned from the function
                    operands.append(fix_float_error(operand))                               #fixes and adds the value to the operand list
                else: operands.append(m["operand"])                                         #adds the value if it isn't a function
                if (m["close"] != None):                                                    #checks if the match has a closed )
                    for c in m["close"]:                                                    #for each ) locates the correct ( and turns everything inside into a list
                        indexands = 0                                                       #
                        indexors = 0                                                        #
                        try:                                                                #
                            operands.reverse()                                              #
                            operators.reverse()                                             #
                            indexands = len(operands) - operands.index('(') - 1             #
                            indexors = len(operators) - operators.index('(') - 1            #
                            operands.reverse()                                              #
                            operators.reverse()                                             #
                        except ValueError as e: return ERR_UNBALANCED                       #ends if there is no ( and return the unbalanced error
                        if (len(operands[indexands+1:]) > 1):                               #this if-else is to avoid a IndexOutOfBounds Error
                            operands = operands[:indexands] + [operands[indexands+1:]]      #
                            operators = operators[:indexors] + [operators[indexors+1:]]     #
                        else:                                                               #
                            operands = operands[:indexands] + operands[indexands+1:]        #
                            operators = operators[:indexors] + operators[indexors+1:]       #
                if (m["sop_operators"] != None): operators.append(m["sop_operators"])       #adds the single operand operator to the operator list
                if (m["mop_operators"] != None): operators.append(m["mop_operators"])       #adds the two operand operator to the operator list
    else: return ERR_FORMATTING                                                             #ends if there is no matches returning the formatting error
    operands = fix_operands(operands)                                                       #
    if (len(operators) == 0): return fix_float_error(operands[0])                           #if there is no operators return the only operand
    return fix_float_error(recursive_eq_eval(operands, operators))                          #otherwise recursively evaluate the operands and operators
def eq_booled(s: str): #Uses the regs to parse the equations and the condition
    booled = TRUTH_REG.search(s)                                                            #turns the statement into the truth match
    if booled:                                                                              #if the match exist we can work on it
        first = eq_evaluate(booled["first"])                                                #gets the value of the first equation
        second = eq_evaluate(booled["second"])                                              #gets the value of the second equation
        truestr = f"Yes, {booled['first']} {booled['comp']} {booled['second']} is true"     #creates the true str
        falsestr = f"No, {booled['first']} {booled['comp']} {booled['second']} is false"    #creates the false str
        try:                                                                                #checks if they returned an error
            first = float(first)                                                            #
            try: second = float(second)                                                     #
            except ValueError as e: return second                                           #
        except ValueError as e:                                                             #
            try: second = float(second)                                                     #
            except ValueError as e: return first + "\n" + second                            #
            return first                                                                    #
        match booled["comp"]:                                                               #using the conditional symbols checks if they match that condition or not
            case "<"|"less than":                                                           #
                if (first < second): return truestr                                         #
                else: return falsestr                                                       #
            case ">"|"greater than":                                                        #
                if (first > second): return truestr                                         #
                else: return falsestr                                                       #
            case "="|"equal to":                                                            #
                if (first == second): return truestr                                        #
                else: return falsestr                                                       #
            case "<="|"less than or equal to":                                              #
                if (first <= second): return truestr                                        #
                else: return falsestr                                                       #
            case ">="|"greater than or equal to":                                           #
                if (first >= second): return truestr                                        #
                else: return falsestr                                                       #
            case "!="|"not equal to":                                                       #
                if (first != second): return truestr                                        #
                else: return falsestr                                                       #
    else: return ERR_TRUTH                                                                  #if there is no match return truth error
def eq_comped(s: str): #Uses the regs to parse the equations and compares their values
    comped = COMPARE_REG.search(s)                                                  #checks if it matches the pattern for a compare
    if comped:                                                                      #if the match exists
        first = eq_evaluate(comped["first"])                                        #gets the value of the first equation
        second = eq_evaluate(comped["second"])                                      #gets the value of the second equation
        try:                                                                        #checks if either of the above returned an error
            first = float(first)                                                    #
            try: second = float(second)                                             #
            except ValueError as e: return second                                   #
        except ValueError as e:                                                     #
            try: second = float(second)                                             #
            except ValueError as e: return first + "\n" + second                    #
            return first                                                            #
        if (first > second): return f'{comped["first"]} > {comped["second"]}'       #compares the values
        elif (first == second): return f'{comped["first"]} = {comped["second"]}'    #
        else: return f'{comped["first"]} < {comped["second"]}'                      #
    else: return ERR_COMPARE                                                        #returns the compare error if there is no match

#the main portion of the Textual Calculator
while True:                                                     #loops until the exit command is called
    print("Please input a question/cmd below: ")                #prints the prompt for the user
    cmd = input("").lower()                                     #gets the input and makes it all lowercase
    results = INITIAL_REG.search(cmd)                           #checks if it matches any commands
    if results:                                                 #if it does match
        has_rest = (results["rest"] != None)                    #checks if it has a statement
        rest = ""                                               #
        if has_rest: rest = results["rest"]                     #if it does then make it a variable
        if results["exit"] != None: break                       #if the command is exit then end the loop and program
        if results["help"] != None: print(HELPSTR)              #if the command is help then prints the helpstr
        if results["eval"] != None:                             #if the command is eval then evaluates the rest of the command
            if has_rest:                                        #
                output = eq_evaluate(rest)                      #
                if type(output) == str: print(output)           #
                else:                                           #
                    prev_ans = output                           #
                    print(f"ANSWER: {output}")                  #
            else: print(ERR_MISSING_REST)                       #
        if results["bool"] != None:                             #if the command is bool then it checks the truth of the rest of it
            if has_rest: print(f"ANSWER: {eq_booled(rest)}")    #
            else: print(ERR_MISSING_REST)                       #
        if results["comp"] != None:                             #if the command is comp then it compares the rest of it
            if has_rest: print(f"ANSWER: {eq_comped(rest)}")    #
            else: print(ERR_MISSING_REST)                       #
    else: print(ERR_UNKNOWN_CMD)                                #if the command is unknown then prints the error