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

To resolve tins challenge, we have to do some linear Algebra ;)

# Linear Algebra: Linearity of the CRC function
Let's denote that: crc_82_darc(x) = f(x)
After a long time of research, I found that in general the the CRC function is linear.

### The formula
![formula1](/cryptography/Introspective-CRC/images/f1.png)
