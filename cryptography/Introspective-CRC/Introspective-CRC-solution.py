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
