# This file parses an input Racket string and converts it to an equivalent expression tree representation (called an AST)

import string # for string helper functions
from typeFile import * # import RacType for type hints
from ERobj import *  # for accessing pdict and ERObj declarations in applyRule

# SYMBOLS: perhaps in future allow square brackets and braces. 
WHITESPACE = ["\n","\t","\r"," "] # permits linebreak and indents for conditionals. all become \s in pre-processing step
ARITHMETIC = ["+","*","-","=",">","<"] # any other math uses ascii, such as expt, quotient, remainder. Note: "/" not permitted
OPEN_GROUP = ["(","[","{"] # needed to separate open from closed for more precision with error messaging
CLOSE_GROUP = [")","]","}"] # possibly cond might be implemented one day with square brackets. presently, all these replaced by parens in pre-processing
SPECIAL_CHARS = ["#","?","\u03BB","'"] # hashtag for bools,? for pred suffix, unicode is for λ (currently not in language), single quote for quoted lists
AllowedChars = list(string.ascii_letters) + list(string.digits) + WHITESPACE + ARITHMETIC + OPEN_GROUP + CLOSE_GROUP + SPECIAL_CHARS

# Node object used to compose the AST
class Node:
    def __init__(self, children=[], parent=None, data:str='', tokenType:RacType=RacType((None,None)), name=None, debug:bool=False, ins=None, outType=None, numArgs:int=None, length:int=None):
        self.children = children # by specification, children[0] is the "operator" for functions
        self.parent = parent # reference to the Node's parent (will be None for the root Node)
        self.data = data # this is the string name to be displayed (what used to be called "name" in the old PB)
        self.name = name # this is what used to be called "value" in the old PB
        self.type = tokenType # type of the node, (ex. boolean, int, function, etc.), specification described in typeFile
        self.debug = debug # False = standard execution, True = print info useful when debugging the pipeline
        #self.ins = ins # [OBSOLETE WITH NEW TYPE SPEC] for functions, it's the tuple of input types
        #self.outtype = outType # [OBSOLETE WITH NEW TYPE SPEC] for functions, it's the output type
        self.numArgs = numArgs # for functions, it's the number of inputs
        self.length = length # for lists, it's the length 

    # Node.type attribute getter
    @property
    def type(self):
        return self._type
    
    # Node.type attribute setter
    @type.setter
    def type(self, newType):
        self._type = newType

    # convert the Node into a representation that is printed to the console
    def __str__(self):

        # print any unassigned type info during debugging
        if self.type == None and self.debug:
            outStr = f'{self.children}, {self.data}'
            print(outStr)

        # print value and type of each Node object, and a whitespace character for readability
        if self.debug:
            ans = f'{self.name},{self.type} '
        else:
            ans = self.data # print standardized syntax
        
        # print the Node's children if there are any
        if len(self.children) > 0:
            for i in range(len(self.children)):
                if i == len(self.children)-1 or self.debug:
                    ans += str(self.children[i])
                else:
                    ans += str(self.children[i]) + ' '
            ans += ')'
        return ans
    
    # this sets every node in the tree to the same debug setting
    def fullDebug(self, setting:bool):  
        if self!=None:
            self.debug=setting
            for c in self.children:
                c.fullDebug(setting)
        return
    
    def setType(self, strg:str):
        if ">" not in strg:
            self.type=RacType((None,Type.__members__.get(strg)))
        else:
            # make a "token list"
            slist = strg.upper().replace("(", " ( ").replace(">", " > ").replace(",", " , ").replace(")", " ) ").strip().split()
            if (ind:=findArrow(slist)) == -1:
                self.type=RacType(Type.ERROR) # e.g. mismatched parens
            else:
                print(ind)
        return
     
    def applyRule(self, ruleID:str): #TODO: replace with dictionary
        if ruleID == "if":
            self.ruleIf()
        if ruleID == "cons":
            pass #self.ruleCons()
        if ruleID == "first":
            pass #self.ruleFirst()
        if ruleID == "rest":
            pass #self.ruleRest()

    def ruleIf(self, debug=False):
        if (len(self.children) != 0 and self.children[0].data != 'if') or len(self.children) != 4:
            print("Invalid if expression!")
            if debug:
                if len(self.children) != 0:
                    print("child[0] data:",self.children[0].data)
                print("length of children: ",len(self.children))
        else:
            condition = self.children[1]
            xNode = self.children[2]
            yNode = self.children[3]
            if condition.data == '#t':
                self.replaceNode(xNode)
            elif condition.data == '#f':
                self.replaceNode(yNode)
            elif isMatch(xNode, yNode): 
                self.replaceNode(xNode)

    def replaceNode(self, newNode): #is there a better way to do this?
        self.data = newNode.data
        self.name = newNode.name
        self.type = newNode.type
        self.numArgs = newNode.numArgs
        self.length = newNode.length
        self.children = newNode.children
        self.debug = newNode.debug 
        #do NOT change self.parent, to maintain place in tree


    
    #Old expression evaluation func, mistakenly called applyRule before - very incomplete
    #def evalExpression(self):
        # if (self.children[0].data in pdict): #for pre-defined functions
        #     operator = self.children[0].data
        #     erObj = pdict[operator]
        #     inputs = []
        #     for child in self.children[1:]: #converting to bools or ints so calculation can be done
        #         if child.data == '#t':
        #             inputs.append(True)
        #         elif child.data == '#f':
        #             inputs.append(False)
        #         elif child.type == Type.PARAM:
        #             inputs.append(child.data)
        #         else:
        #             inputs.append(int(child.data)) #any other type - any missing?
        #     if erObj.value: #if operation is defined in the ERobj, eg for arithmetic or boolean operations
        #         output = erObj.value(*inputs)
        #         return output
        #     else: #if, cons, first, rest, null, lambda
        #         if operator == 'first':
        #             return inputs[0]
        #         if operator == 'rest':
        #             return inputs[1:] #list of the remaining inputs
        #         if operator == 'if':
        #             if inputs[0]:
        #                 return inputs[1]
        #             else:
        #                 return inputs[2]

                
# a helper function for setType that returns the position in the list of the root >
def findArrow(tlist:list)->int:
    if tlist[0]!="(": #it was just a single parameter function and so user didn't use parens
        return 1
    counter=0 #checking for when parens first become balanced
    for i in range(len(tlist)): #must use range since index matters
        counter += 1 if tlist[i]=="(" else -1 if tlist[i]==")" else 0
        if counter == 0:
            return i+1
    return -1 # this should never happen unless the string had unbalanced parens
        
# errLog is a list of strings of error messages that will be passed at each step of the tree-building process
def preProcess(inputString:str, errLog:list[str]=None, debug=False) -> tuple[list[str],list[str]]: # None will generate a warning since it's not a list of strings
    if errLog == None: # values assigned at func def, not each call, so need None vs []
        errLog = []

    #orig=inputString #saving original to refer to later, but might not be needed
    #inputString = inputString.lower()  #decided to permit uppercase letters and make it case sensitive to allow M vs m. caution: now  "If" is not "if"
    
    # standardize open/close grouping characters and whitespace
    inputString=inputString.replace("]",")").replace("[","(").replace("{","(").replace("}",")").replace("\t"," ").replace("\r"," ").replace("\n"," ").replace("("," ( ").replace(")"," ) ")
    inputString = " ".join(inputString.split()) # remove consecutive spaces, strip whitespace from front & back of inputString
    
    if inputString == "": # needed to avoid an issue in checking first character as (
        errLog.append("no input detected") # can't return the append directly since append changes in place and doesn't return a value!!
        return [], errLog
    # note that final replacement at end of next line attaches a \s to parens for list-splitting purposes
    
    # parentheses pairing check
    parenPairing = 0
    for ind in range(len(inputString)): # needed to loop over index values rather than char to know if not at end
        char = inputString[ind]

        # check if char is an allowed character
        if char not in AllowedChars:
            errLog.append(f"{char} not an allowed character")

        # parenPairing should only return to 0 at the very end of the input string
        if char == '(':
            parenPairing += 1
        elif char == ')':
            parenPairing -= 1

        # the following conditionals refer to the general lists of chars in case later developers decide not to the the replacements:
        # parentheses balanced in the interior of the string    
        if char in OPEN_GROUP and parenPairing==1 and 0<ind<len(inputString)-1:
            errLog.append("contains multiple independent subexpressions") #"(stuff)(stuff)".  need )( check to insure "34" doesn't trigger an error
        
        # separate values not wrapped in a list
        if char in WHITESPACE and inputString[0] not in OPEN_GROUP:
            errLog.append("multiple elements should be contained within a list") # "n n" will trigger an error
    
    # parentheses are not balanced in the input string 
    if parenPairing < 0:
        errLog.append("too many )")
    elif parenPairing > 0:
        errLog.append("too many (")
    
    # attaches single quote to left paren for quoted lists 
    inputString = inputString.replace("' (","'(")

    # return the list of standardized tokens, and the error log
    return inputString.split(),errLog

# helper function to find the index of the matching close parenthesis given the index of the open parenthesis    
def findMatchingParenthesis(tokenList, index) -> int:
    count = 1
    for i in range(index+1, len(tokenList)):
        if tokenList[i] == '(':
            count += 1
        elif tokenList[i] == ')':
            count -= 1     
        if count == 0:
            return i
        
# algorithm to build the AST, composed of Node objects
def buildTree(inputList:list[str], debug=False) -> list:
    # if inputList == [], return the empty list
    if len(inputList) == 0:
        return [] 
    
    # we have something in inputList, create a Node
    node = Node([], debug=debug) # need [] inside Node init to ensure no children on instantiation
    node.data = inputList[0] # fill out the data with the symbol

    # if the first token is not '(', it is a single literal (ex. boolean, int, parameter)
    if inputList[0] != '(':

        # create Node where Node.data is the literal and continue processing the rest of input
        return [node] + buildTree(inputList[1:len(inputList)], debug)
    
    # special case for the empty list '()', just modify Node.data == '()'
    if inputList[0] == '(' and inputList[1] == ')':
        node.data = 'null'

        # continue processing the rest of input
        return [node] + buildTree(inputList[2:len(inputList)], debug)

    # we have '(' as the first token, find the index of its matching ')'
    matchIndex = findMatchingParenthesis(inputList,0)

    # if everything else is contained within our parenthesis pair, they will be contained in Node.children
    if matchIndex + 1 == len(inputList):
        node.children = buildTree(inputList[1:-1], debug)

        # set the parent of each child node to be the (root) node
        for child in node.children:
            child.parent = node
        
        # return the (root) node
        return [node]
    
    # there are multiple elements in our list, create a Node/subtree for things in that list, append all to Node.children
    node.children += buildTree(inputList[1:matchIndex], debug)

    # set the parent of each child node to be the (root) node
    for child in node.children:
        child.parent = node

    # continue processing the rest of input
    return [node] + buildTree(inputList[matchIndex+1:len(inputList)], debug)

def isMatch(xNode:Node, yNode:Node)->bool: #recursively check if two nodes are identical #TODO: replace elif chain with something prettier
    if xNode.data != yNode.data:
        return False
    elif xNode.name != yNode.name:
        return False
    elif xNode.numArgs != yNode.numArgs:
        return False
    elif xNode.length != yNode.length:
        return False
    elif xNode.type != yNode.type:
        return False
    elif len(xNode.children) != len(yNode.children):
        return False
    elif len(xNode.children) != 0:
        for i in range(len(xNode.children)):
            return isMatch(xNode.children[i], yNode.children[i])
    else:
        return True #if everything else passed