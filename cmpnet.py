#!/usr/local/bin/python3 #This si a file to test Python3
import re
import json
import sys          #So that I can use sys.exit()
import os           #So that I can check if file exists

from netlist import Netlist
from netlist import PartList
from netlist import diffNL  #Class that stores how netlist diff is stored
#Functions
def cmpNetlistPrt(new_netlst, old_netlst, diffNL, new_prts, old_prts):
    #This funciton will take two objects of class Netlist and compare for differences
    #It needs to report components that has been added and removed <TO-DO> show modified 
    #Show added, removed and modified nets.
    # diff Object
    added_parts = []
    removed_parts = []
    has_parts_detail = 0
    if not new_prts: #Nothing was passed
        pass
    else:
        has_parts_detail +=1
    if not old_prts: #Nothin was passed
        pass
    else:
        has_parts_detail +=1

    parts1 = new_netlst.getAllParts()
    parts2 = old_netlst.getAllParts()
    print (f"The number of new parts is {len(parts1)}\nThe number of old parts is {len(parts2)}")
    for part in parts1:
        if part in parts2:
            pass
        else :
            added_parts.append(part)
            diffNL.insertAddParts(part) #USE Class to record added part

    for part in parts2:
       if part in parts1:
            pass
       else:
            removed_parts.append(part)
            diffNL.insertDelParts(part)

    print (">>>>>>>>>>>Printing Parts details")
    if has_parts_detail == 2: #Print parts details
        for part in diffNL.getAddParts():
            print (f"{part} : {new_prts.parts[part]}")

    print (f"Added Parts are **********: \n {diffNL.getAddParts()}")
    print (f"Removed Partes are *******: \n {diffNL.pdiff['del']}")

def cmpNetlist(new_netlst, old_netlst, diffNL):

     for key, value in new_netlst.netlst.items():
        if key in old_netlst.netlst:
            # pass #compare netlists here

            l1 = value #Elements of NET_NAME - NEW 
            l2 = old_netlst.netlst[key] #Elements of NET_NAME - OLD
            s1 = set(l1)
            s2 = set(l2)
            z = s1.difference(s2)
            if z: #NET is not the same
                print (f"Nets are different {key}")
                list_add = [i for i in l1 + l2 if i not in l2]
                list_del = [i for i in l1 + l2 if i not in l1]
                diffNL.insertModNets_add(key,list_add)
                diffNL.insertModNets_del(key,list_del)
                print (f"added elements: {diffNL.getModNets_add(key)}")
                print (f"removed elements: {diffNL.getModNets_del(key)}")
        else:
            diffNL.insertAddNets(key, value)
            print (f"New NET: {key} :  {new_netlst.netlst[key]} was added!!!")

     for key, value in old_netlst.netlst.items():
        if not key in new_netlst.netlst:
            diffNL.insertDelNets(key, value) #Deleted Nets

    # end cmpNetlistPrt()

def printDiff(diffNL):
    #This function will print statistics and difference
    print("**************************************************")
    print("*                                                *")
    print("*                                                *")
    print("*              KORONA DIFF (KDIFF)               *")
    print("*                                                *")
    print("*                                                *")
    print("**************************************************")
    print("\n")
    print("************** Added Parts *************************")
    print(json.dumps(diffNL.getAddParts(), indent=0))
    print("************** Deleted Parts *************************")
    print(json.dumps(diffNL.getDelParts(), indent=0))
    print("************** Added Nets *************************")
    diffNL.printAddNets()
    print("\n************** Deleted Nets *************************")
    diffNL.printDelNets()
    print("\n************** Modified Nets *************************")
    diffNL.printModNets()
    print(f"The number of parts added : {diffNL.addPartsCount()}")
    print(f"The number of parts deleted : {diffNL.delPartsCount()}")
    print(f"New NETs        : {diffNL.addNetsCount()}")
    print(f"Removed NETs    : {diffNL.delNetsCount()}")
    print(f"Modified NETs   : {diffNL.modNetsCount()}")


##################### MAIN ########################
def main(args):
    print ("This will test a class, which parses netlist")

    # dfltNewFile = "pstxnet.dat" #Default New Netlist
    # dfltOldFile = "pstxnet.dat,1" #Default Old File

    dfltNewFile = "pstxnetNEW.dat" #Default New Netlist
    dfltOldFile = "pstxnet.dat" #Default Old File

    if args.dir:    #Directory is specified
        dfltNewFile = args.dir + "/" + dfltNewFile
        dfltOldFile = args.dir + "/" + dfltOldFile
    #<TO-DO> Check that files exist
    #<TO-DO> 
    # mynl1 = Netlist("data/pstxnetNEW.dat") #Open new design netlist
    # mynl2 = Netlist("data/pstxnet.dat") #Open new design netlist
    if not os.path.isfile(dfltNewFile):
        print (f"File {dfltNewFile} doesn't exist")
        sys.exit()
    if not os.path.isfile(dfltOldFile):
        print (f"File doesn't exist")
        sys.exit()

    mynl1 = Netlist(dfltNewFile) #Open new design netlist
    mynl2 = Netlist(dfltOldFile) #Open new design netlist
    myprts1 = PartList("data/pstxprtNEW.dat")
    myprts2 = PartList("data/pstxprt.dat")
    mydiff = diffNL(mynl1, mynl2)

    if mynl1 is mynl2:
        print ("Same pointer!!!! ERROR")
    cmpNetlistPrt(mynl1, mynl2,mydiff, myprts1, myprts2)
    cmpNetlist(mynl1, mynl2,mydiff)
    print ("The number of netlists is " + str(Netlist.num_netlist))
    print ("End of test")
    printDiff(mydiff)
    # end main

if __name__ =="__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test")
    parser.add_argument("--new","-n", required=False, help="File containing new netlist")
    parser.add_argument("--old","-o", required=False, help="File with old netlist")
    parser.add_argument("--dir", required=False, help="Netlist(s) are in another dirctory, only applies to both or new")
    parser.add_argument("--dirold", required=False, help="Optional directory for old netlsit directory")
    args = parser.parse_args()

    main(args)
