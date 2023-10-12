# Python's Regular Expressions Overview
## Table of Contents
1. [What is Regular Expressions](#what-is-regular-expressions) 
    1. [Why use Regular Expressions](#why-use-regular-expressions)
    2. [How I used Regular Expressions](#how-i-used-regular-expressions)
2. [What can Regular Expression do](#what-can-regular-expression-do)
3. [Other Questions](#other-questions)
    1. [When was Regular Expressions created](#when-was-regular-expressions-created)
    2. [Why I selected Regular Expressions](#why-i-selected-regular-expressions)
    3. [How it shaped how I learn python](#how-it-shaped-how-i-learn-python)
    4. [My overall experience with Regular Expressions](#my-overall-experience-with-regular-expressions)
***
### What is Regular Expressions

>A regular expression (or RE) specifies a set of strings that matches it [https://docs.python.org/3/library/re.html]

And in this library, it gives us all of the functions required to find out if any particular string matches the given RE, as well as many other useful functions. More on the functions [here](#what-can-regular-expressions-do)

#### Why use Regular Expressions

The purpose behind using regular expressions is in the properties of regular expression, and using them to matches their specific set of strings. This allows for a lot of control without resolving to a lot of if else statements.

#### How I used Regular Expressions

In my TextualCalculator I used specific regular expressions to match which mode the calculator is in such as evaluate, truth, or compare and other specific commands such as exit, and help. When using evaluate, truth, or compare it also helps with evaluating the given math equation(s) in a recursive manner as it is by far the easiest way to evaluate an equation of a variable amount of operators. 

##### The Regular Expressions I used

```py
INITIAL_REG = re.compile(r"""^\s*
    ((?P<exit>exit|close|esc|escape|$)|
    (?P<help>help|cmds?|commands?)| 
    (?P<eval>eval(uate)?|what\ (is|does))|
    (?P<bool>truth|bool|(?<!what)(is|does))|
    (?P<comp>compare))\s*
    (?P<rest>.+)?$""", re.X)
EVALUATE_REG = re.compile(r"""^\s*
    (?P<open>\(+)?\s*
    (?P<operand>
    (?P<func_name>[a-z_0-9]+)\((?P<func_value>.+?\)?)\)|
    (\d+(\.\d+)?|pi|e|ans))\s* 
    (?P<close>\)+)?\s* 
    (?P<sop_operators>[!])?\s*
    (?P<mop_operators>[+\-*/^%])?\s*
    (?P<rest>.+)?$""", re.X)
TRUTH_REG = re.compile(r"""^\s*
    (?P<first>.+?)\s*
    (?P<comp><=?|>=?|!?=|
    greater\ than(\ or\ equal\ to)?|
    less\ than(\ or\ equal\ to)?|
    (not\ )?equal\ to)\s*
    (?P<second>.+)\s*$""", re.X)
COMPARE_REG = re.compile(r"""^\s*
    (?P<first>.+?)\s*
    (and|\||&)\s*
    (?P<second>.+)\s*$""", re.X)
```
Starting with the ```INITIAL_REG```,  this regular expression Pattern object is used to see whether the users input matches one of the commands I have built in.

Similarly ```EVALUATE_REG``` is used to recursively comprehend mathematical equations.

Both `TRUTH_REG` and `COMPARE_REG` process their input into two mathematical equations which are further processed by `EVALUATE_REG` then returned and are compared or are checked with the give condition.

##### The functions I made with the regular expressions

Here is my `recursive_read(...)`

```py
def recursive_read(s: str, reg: re.Pattern, rec: str): 
    #recusively checks a string using the given regex and the recursive group string
    m = reg.search(s)   #checks the string (s) with the regex
    if m:   #if it matched anything
        m_list = [m]    #makes a list of the matches for later comprehension
        if m[rec] != None:  
            #checks if the match has more of the recursive pattern
            nex = recursive_read(m[rec], reg, rec)  #the recursive call
            if nex == None: return m_list   
            #if the rec pattern does not match anything
            for i in nex: m_list.append(i)
            #adds all of the recursive matches to this levels list
        return m_list
    return None
```

It takes a string, a Pattern object, and another string of the name of the recursive group name, it checks if there is any match from the full string and if it does we check if the recursive group is not `None` and calls this function on the string of the recursive group

***

### What can Regular Expression do

The regular expression library is a powerful tool. Here are some of the key functionalities of this library:

1. **Pattern Matching:** The regular expression library allows you to define patterns using regular expressions. These patterns can be used to search for specific substring within a text. 

2. **Search and Match:** You can use the regular expression library to search for patterns in a string or check if a string matches a particular pattern. The `search()` function finds the first occurrence of a pattern in a string, while the `match()` function checks if a string begins with a pattern.

    ```py
    >>> re.search("o", "frog")   # Match at index 2
    <re.Match object; span=(2, 3), match='o'>
    >>> re.match("o", "frog")    # No match; "frog" doesn't start with "o"
    ```

3. **Replacement:** The regular expression library allows you to replace matched patterns in a string with other text using the `sub()` function. This is useful for data cleaning and text manipulation tasks.

    ```py
    >>> def dashrepl(matchobj):
    ...     if matchobj.group(0) == '-': return ' '
    ...     else: return '-'
    ...
    >>> re.sub('-{1,2}', dashrepl, 'pro----gram-files')
    'pro--gram files'
    >>> re.sub(r'\sAND\s', ' & ', 'Baked Beans And Spam', flags=re.IGNORECASE)
    'Baked Beans & Spam'
    ```
    [https://docs.python.org/3/library/re.html#functions]

4. **Splitting:** The `split()` function can split a string into a list of substrings based on a specified regular expression pattern.

    ```py
    >>> re.split(r'\W+', 'Words, words, words.')
    ['Words', 'words', 'words', '']
    >>> re.split(r'(\W+)', 'Words, words, words.')
    ['Words', ', ', 'words', ', ', 'words', '.', '']
    >>> re.split(r'\W+', 'Words, words, words.', 1)
    ['Words', 'words, words.']
    >>> re.split('[a-f]+', '0a3B9', flags=re.IGNORECASE)
    ['0', '3', '9']
    ```
    [https://docs.python.org/3/library/re.html#functions]

5. **Grouping:** Regular expressions can be used to define groups within patterns. These groups allow you to extract specific parts of the matched text.

    ```py
    >>> m = re.search("(\d) and (\w)", "what about 3 and k")
    >>> m.groups()
    ('3', 'k')
    >>> m = re.search("(?P<number>\d) and (?P<letter>\w)", "what about 3 and k")
    >>> m.groupdict()
    {'number': '3', 'letter': 'k'}
    ```

6. **Flags:** The regular expression library supports various flags, such as case-insensitive matching, multiline matching, and more. The list of flags can be found here [https://docs.python.org/3/library/re.html#flags]

7. **Anchors:** Anchors like `^` and `$` are used to specify where in the text a pattern should appear.

8. **Character Classes:** The regular expression library provides predefined character classes like `\d` for digits, `\w` for word characters, and `\s` for whitespace.

    ```py
    >>> is4letters = re.compile("\s\w{4}\s")
    >>> is4letters.search("No Not Nothing Yeah Nope")
    <re.Match object; span=(14, 20), match=' Yeah '>
    ```

9. **Lookahead and Lookbehind:** Advanced features like lookahead and lookbehind assertions allow you to specify conditions for matching text that is not part of the actual match.

    ```py
    >>> itsMe = re.compile("Hayden (?=Lees)", re.I)
    >>> itsMe.search("Hayden Lastname is not me") # no match; "Hayden " is not followed "Lees"
    >>> itsMe.search("Hey it is me, hayden lees") # match at index 14
    <re.Match object; span=(14, 21), match='hayden '>
    ```

***
<div style="page-break-before:always">&nbsp;</div>
<p></p>

### Other Questions

#### When was Regular Expressions created

>"The concept of regular expressions began in the 1950s, when the American mathematician Stephen Cole Kleene formalized the concept of a regular language" [https://en.wikipedia.org/wiki/Regular_expression]

and the first version of python to include regular expressions was python 1.5 [https://python.readthedocs.io/en/v2.7.2/howto/regex.html] which was released January 3rd 1998. [http://python-history.blogspot.com/2009/01/brief-timeline-of-python.html]

#### Why I selected Regular Expressions

I selected regular expressions as I always wanted to learn how to use them to make a text interpreter that can evaluate a lot of things and be expandible.

#### How it shaped how I learn python

Throughout making this program I have learned a lot of interesting things from the flexiblity of python's match-case to using extensive recursion to simplify complex math equations and other problems of my own creation, rather the recursion questions given to me in classes before because I didn't know if it was easier to use recursion or not.

#### My overall experience with Regular Expressions

My overall experience with Regular Expressions is very good as I was able to make a program that I have been wanting to make for a long time.

I would recomend regular expressions to anyone who needs to validate user given input, to read throught data to find and replace something specific, and/or if they need to recursively read parts of a string for any reason.

I am planning on using this whenever it seems useful as it is very strong for being easy to understand.