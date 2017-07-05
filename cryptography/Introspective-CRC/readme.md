# Introspective CRC

The challenge provide a .gif file that display a md5 hash code. Of course, that not the solution :)

My first try is to compute the md5 checksum of the .gif file, I run:
```bash
$ md5sum md5.gif
f5ca4f935d44b85c431a8bf788c0eaca  md5.gif
```

it returns the same md5 hash. 

As you see, the challenge provide also an URL:
selfhash.ctfcompetition.com:1337, let's connect to that URL:
```bash
mayar@mayarLinux:~$ nc selfhash.ctfcompetition.com 1337
Give me some data: hello

Check failed.
Expected:
    len(data) == 82
Was:
    5
```

The server ask for some data. Of course, we don't know the data to give. We must find it.
When, we provided "hello", it displayed the length of "hello".

Let's give 10 characters:
```bash
mayar@mayarLinux:Introspective-CRC$ printf "%0.sa" {1..10} | nc selfhash.ctfcompetition.com 1337
Give me some data: 
Check failed.
Expected:
    len(data) == 82
Was:
    10
```
And when provided "a"*10, it displayed 10.

_**`At this point, we understant that the data must contain 82 characters.`**_


Let's send a string with "a"*82 characters:
```bash
mayar@mayarLinux:Introspective-CRC$ printf "%0.sa" {1..82} | nc selfhash.ctfcompetition.com 1337
Give me some data: 
Check failed.
Expected: 
    set(data) <= set("01")
Was:
    set(['a'])
```
_**`Hum, the server wait a string that contains only "0"s and "1"s.`**_


When we send "0"*82:
```bash
mayar@mayarLinux:Introspective-CRC$ printf "%0.s0" {1..82} | nc selfhash.ctfcompetition.com 1337
Give me some data: 
Check failed.
Expected: 
    crc_82_darc(data) == int(data, 2)
Was:
    1021102219365466010738322L
    0
```

and "1"*82:
```bash
mayar@mayarLinux:Introspective-CRC$ printf "%0.s1" {1..82} | nc selfhash.ctfcompetition.com 1337
Give me some data: 
Check failed.
Expected: 
    crc_82_darc(data) == int(data, 2)
Was:
    4100702145019332376236782L
    4835703278458516698824703L
```
_**`a CRC error`**_


### This leads as to that:
* The _**`data`**_ is a 82-binary string.
* The _**`crc_82_darc(data)`**_ is equal to _**`int(data, 2)`**_: That means, the _**`crc_82_darc(data in binary)`**_ is equal to the _**`data`**_ converted to an integer. ==> We are looking for an integer _**`x`**_, that: _**`crc_82_darc(toBinary(x)) == x`**_

* _**`x`**_ is coded on 82 bits, so _**`MAX_X = 2^82-1 = 4835703278458516698824703`**_. If you think to bruteforce that, then see you after one thousand year :) Because you have to write a script to check, for every _**`x in [1000000000000000000000000, 4835703278458516698824703]`**_, if _**`crc_82_darc(toBinary(x)) == x`**_

If you're not convinced, try yourself:
```python
import sys
import numpy
try:
    from pwn import *
except ImportError:
    print ("Sorry, you have to install the pwntools libarary.")
    print ("for python2: http://docs.pwntools.com/en/stable/install.html")
    print("for python3: http://python3-pwntools.readthedocs.io/en/latest/install.html")
    sys.exit()

start = 1000000000000000000000000
end = 4835703278458516698824703
for x in range(start, end+1):
    xInBin = '{0:082b}'.format(x)
    xCRC = crc.crc_82_darc(xInBin)
    if x == xCRC:
        print ("BINGO data found: "+xInBin)
        sys.exit()
    else:
        print ("crc_82_darc("+xInBin+") == "+str(xCRC))
```

### _**`The solution is to find a fast way to resolve this equation: crc_82_darc(toBinary(x)) == x`**_

To resolve this challenge, we have to do some linear Algebra ;)

# Linear Algebra: Linearity of the CRC function
Let's denote that: **_`crc_82_darc(x) = f(x)`**_
After a long time of research, I found that in general the the CRC function is linear.

### The formula
![formula1](/cryptography/Introspective-CRC/images/f1.png)
![formula1](/cryptography/Introspective-CRC/images/f2.png)

We have: _**`(V-I) X = Z`**_.
To resolve it, we have multiple approches. Like the [Gaussian elimination](https://en.wikipedia.org/wiki/Gaussian_elimination).
For me, I used the [sageMath](http://www.sagemath.org/) tool + python script to resolve (V-I) X = Z.

### Steps
1. Compute the 82-vector _**`Z`**_: toBinary(crc_82_darc('0' * 82))
1. Compute the 82x82-matrix _**`V`**_
1. Compute the 82x82-matrix _**`(V-I)`**_
(We can do step #2 and #3 in one step)
1. Resolve the system: _**`(V-I) X = Z`**_
1. Send the solution to _**`selfhash.ctfcompetition.com:1337`**_

### The python script
```python
########################Needs Libararies########################################
import sys
from subprocess import call
import re

try:
    from sage.all import *
except ImportError:
    print  "Sorry, you have to install the sage module."
    print ("http://www.sagemath.org/")
    print "$ sudo cp sage /usr/local/bin/"
    print "$ sudo gedit /usr/local/bin/sage"
    print  'Add the path: export SAGE_ROOT="<your sageMath path>"'
    print  "Test it: $ sage"
    print "To run a python2 script using sageMath: $ sage -python script.py"
    print "If a module is missing in sageMath:"
    print "\t1- Download it."
    print "\t2- run within the module directory: $ sage --python setup.py install"
    sys.exit()

try:
    from pwn import *
except ImportError:
    print "Sorry, you have to install the pwntools module."
    print "for python2: http://docs.pwntools.com/en/stable/install.html"
    print "for python3: http://python3-pwntools.readthedocs.io/en/latest/install.html"
    sys.exit()
################################################################################


##############Functions#########################################################
##Convert a number to a 82-binary string.
def toBin(n):
    return '{0:082b}'.format(n)

##Compute the 'Z' constant.
def computeZ(z0):
    crc_z0 = crc.crc_82_darc(z0)
    return vector(GF(2), toBin(crc_z0))

##Compute the 'V-I' matrix
def computeV(z0):
    vi = matrix(GF(2), 82, 82)
    crc_z0 = crc.crc_82_darc(z0)
    for i in range(81, -1 , -1):
        e = pow(2, i)
        # V-row
        row = map(int, toBin(crc.crc_82_darc(toBin(e)) ^  crc_z0))

        #(V-I)-row
        vi.set_column(81-i, row)
        vi[81-i, 81-i] -= 1
    return vi
################################################################################


################Main############################################################
print "[+] Computing Z...",
z0 = '0' * 82
Z = computeZ(z0)
print "[Done]"

print("\n")

print "[+] Computing (V-I)...",
VI= computeV(z0)
print "[Done]"

print "\n"

print "[+] Solving the system..."
try:
    sol = VI.solve_right(Z)
    print "".join(map(str, sol))
    print "[Done]"
except ValueError:
    print "No solutions !"
    sys.exit()

print "\n"

print "[+] Sending the solution..."
cmd = 'echo '+ "".join(map(str, sol)) + ' | nc selfhash.ctfcompetition.com 1337 > tmp'
os.system(cmd)
print "[Done]"

print "\n"

print ""
with open('tmp', 'r') as myFile:
    data = myFile.read().replace('\n', '')

matSolution = re.match( r'.*(CTF\{.*\})', data, re.M|re.I)
if matSolution:
   print "Good job ! The soluion is : ", matSolution.group(1)
else:
   print "The solution that you found is wrong !!"

```

### run it
![run](/cryptography/Introspective-CRC/images/run.png)


# References
*  https://crypto.stackexchange.com/questions/34011/why-is-crc-said-to-be-linear
*  https://www.cosc.canterbury.ac.nz/greg.ewing/essays/CRC-Reverse-Engineering.html
*  https://github.com/glua-team-ctf/googlectf-quals-2017/blob/master/crypto/introspective-crc/README.md

# Used tools
* https://www.mathsisfun.com/binary-decimal-hexadecimal-converter.html
* sage: http://www.sagemath.org/
    * Download sageMath
    * In a terminal run (Ubuntu 16.04):
        * Copy the runnable sage file in /usr/local/bin: `$ sudo cp sage /usr/local/bin/`
        * Open the runnable sage file: `$ sudo gedit /usr/local/bin/sage`
        * In the runnable sage file, update the SAGE_ROOT environment variable: `export SAGE_ROOT="<your sageMath path>"`
        * Test it: `$ sage`
    * To run a python2 script (python3 not supported until 05 July 2017) using sageMath: `$ sage -python script.py`
    * If a module is missing in sageMath:
        * Download it
        * Run within the module's directory: `$ sage -python setup.py install`
* the pwntools module:
    * for python2: http://docs.pwntools.com/en/stable/install.html
    * for python3: http://python3-pwntools.readthedocs.io/en/latest/install.html
