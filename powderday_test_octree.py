#built off of test_octree.py, but to use a powderday refined array (instead of 1's and 0's)
import pdb
from octree_sanity_check import *


def test_octree(refined):
    #convert refined to a string to make life easy for octree_sanity_check
    rs = str(refined)
    rs = rs.replace("[","").replace(',','').replace("]","")
    rs = rs.replace("True","T").replace("False","F")
    rs = rs.replace(" ","")
    
    sanity_check(rs)
