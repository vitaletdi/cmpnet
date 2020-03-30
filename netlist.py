#!/usr/local/bin/python3 #This si a file to test Python3
import re
import json
import sys

#GLOBALS VARs - Always a bad idea! 
# DoL = {}    #Name object that gets the netlist

#FUNCTIONS - supporting parsers

def getNodes (net_list, lines, nline, sofList):
# Search all NODES, quit function if it finds NET_NAME or ENDkk
# net_list - object list that is attached to main dictionary array
# As Input takes pstxnet.dat lines buffer
# nline - index into pstxnet.dat buffer
# sofList - Size of List, so that we know how far we can go...

    # print ("I am in getNodes Function")
    node_num=0
    i = nline + 1       #Look at the next line
    while i < sofList:
        line = lines[i]
        match = re.search(r"NET_NAME|END",line)
        if match:
            # print ("I found NET_NAME or END, MUST GET OUT")
            break
        match = re.match("NODE_NAME", line)
        if match:
            node_num += 1
            # print ("Node found")
        # Try to grap the name of Net and drop it in the dictionary. 
            pattern = r"NODE_NAME\s+(\w+)\s+(\w+)" #This is a pattern for netname
            m = re.search (pattern, line)
            if m:
                node_num+=1
                # print (f"There is some RefDes {m.group(1)} and Pins {m.group(2)} ")
                new_node = m.group(1) + "." + m.group(2)
                net_list.append(new_node)
        i += 1 #end-of-while
    #end of getNodes
    nline = i       #Set i to main function 
    # print ("Exit getNodes")
    # print (net_list)
    return



def parseFile(filename, DoL):

    # print (f"Filename is {filename}")
    try:
        f = open(filename, 'r')
    except IOError:
        print('ERROR: There was an error opening the file!')
        sys.exit()

    lines = f.readlines()

    # print ("This is the end of the file... I PRINTED THAT!!!!")
    # print ("The length is {}".format(len(lines)))
    print (f"The length of file is {len(lines)}")

    nets = 0
    i = 0
    sofList = len(lines)
    while i < sofList:
        line = lines[i]
        match = re.match("NET_NAME", line)
        if match:
            nets += 1
        # Try to grap the name of Net and drop it in the dictionary. 
            pattern = r"([A-Za-z0-9_+-\\#]+)" #This is a pattern for netname
            m = re.search (pattern, lines[i+1])
            # print ("*****",lines[i+1])
            if m:
                key = m.group(1)
                # print (key)
                DoL[key] = []   #Assign Empty List to Dictionary
                getNodes (DoL[key], lines, i, sofList)
        i += 1 #end-of-while

    print (f"NETS in file: {nets} ")

    print (f"Entry in Netlist Dict: {len(DoL.keys())} ")
    # print ("I am going to dump entire NETLIST NOW")
    # print (json.dumps(DoL, indent=4))


def parsePrtFile(filename, partDict):
    #This funciton parses file

    with open(filename,'r') as f:
        lines = f.readlines()

    sofList = len(lines)    #Size of file in lines
    print (f"The length of file is {sofList}")
    parts = 0
    i = 0

    while i < sofList:
        line = lines[i]
        m = re.match("PART_NAME", line)
        if m:
            parts += 1
            line = lines[i+1] #Increment one line to get Actual RefDes and Part
            pattern = r"([A-Z0-9]+)\s+\'([@/A-Z0-9_\s\.-]+)\'"
            match = re.search(pattern,line)
            if match:
                key = match.group(1)
                val = match.group(2)
                partDict[key]=val
                # print (f"Refdes : {key}, Part: {val}")
            else: #not match
                print(f"****can't parse {line}")
        i += 1
        #end-of-while

    print (f"FUNC: parsePrt() The number of parts is {parts}")

#Classes ######################
class Netlist:
    num_netlist = 0
    def __init__(self, file):
        DoL = {}
        self.file = file
        parseFile(self.file, DoL) #This should parse the pstxnet.dat
        self.netlst = DoL #Set up the actual netlist. 
        Netlist.num_netlist +=1

    def getAllParts(self):
        #Get all unique parts in the netlist
        #Returns a ist
        tmp_parts = []
        parts = []
        for dkey, dvalue in self.netlst.items():
            for part in dvalue:
                tmp_parts.append(part.split(".")[0])

        parts=list(set(tmp_parts))
        print (f"Number of parts is {len(parts)} **** inside of Class Netlist")
        return parts
        #end getAllParts

    def getParts(self, net1, net2):
        #Simple function that returns all parts that are connected to both nets
        parts = []

        # tmp_parts = []
        # for part in self.netlst[net1]:
            # tmp_parts.append(part.split(".")[0])
        #Let me try to do the same with comprehension
        tmp_parts = [i.split(".")[0] for i in self.netlst[net1] ]

        # tmp_parts2 = []
        # for part in self.netlst[net2]:
            # tmp_parts2.append(part.split(".")[0])

        tmp_parts2 = [i.split(".")[0] for i in self.netlst[net2] ]
        #Now we have tmp_parts and tmp_parts2
        print (f"Net1: {net1} has the following parts")
        print (tmp_parts)
        for part in tmp_parts:
            if part in tmp_parts2:
                parts.append(part)
        return parts
        #end getParts

    def nlprint (self):
        print (json.dumps(self.netlst, indent=4))
    #end class-Netlist

class PartList:
    num_partlist = 0
    def __init__(self, file):
        partDict = {}
        self.file = file
        parsePrtFile(file, partDict)    #Parses pstxprt.dat
        self.parts = partDict
        PartList.num_partlist  += 2
    # end-class PartList
    def getPartCount(self):
        return len(self.parts)

class diffNL:
    #Class that keeps a difference of two netlists
    def __init__(self, new_ntlst, old_ntlst):
    # diff Object
        netsDIFF = {}
        netsDIFF['add'] = {} #This is a Dictionary  of all new nets added
        netsDIFF['del'] = {} #This is a Dictionary  of all deleted nets
        netsDIFF['mod'] = {} #This is a dict of all modified nets
        # dict-of-modded = { name: name_of_net, 'add': list-of-add, 'del' : list-of-del}
        #dict ---> add --> List of Dictionary
        #   | ---> del --> List of Dictionary
        #   | ---> mod --> Two entries (Added|Removed) -> Dictionary of Lists
        partsDIFF = {} #Contains the datastructure for changed parts
        partsDIFF['add'] = []  #New List with added parts, NOTE Netlist knows nothing about parts besides RefDes
        partsDIFF['del'] = []    #New List of all removed/Deleted parts
        self.pdiff= partsDIFF #Set up the actual netlist. 
        self.ndiff = netsDIFF
        self.new = new_ntlst
        self.old = old_ntlst

    def addPartsCount(self):
        return len(self.pdiff['add'])

    def delPartsCount(self):
        return len(self.pdiff['del'])

    def addNetsCount(self):
        return len(self.ndiff['add'])

    def delNetsCount(self):
        return len(self.ndiff['del'])

    def modNetsCount(self):
        return len (self.ndiff['mod'])

    def insertAddParts(self, part):
        #Inserts part that has been added to the netlist
        self.pdiff['add'].append(part)

    def insertDelParts(self, part):
        #Inserts part that has been deleted from the new netlist
        self.pdiff['del'].append(part)
    def getAddParts(self):
        return self.pdiff['add']

    def getDelParts(self):
        return self.pdiff['del']

    def insertAddNets(self, net_name, element_list):
        self.ndiff['add'][net_name] = element_list #DEEP COPY???

    def insertDelNets(self, name_name, element_list):
        self.ndiff['del'][net_name] = element_list

    def insertModNets_add(self,net_name, part_list):
         # dict-of-modded = { name: name_of_net, 'add': list-of-add, 'del' : list-of-del}
        if net_name not in self.ndiff['mod']:
            self.ndiff['mod'][net_name] = {}    #Create Dictionary if not there
        self.ndiff['mod'][net_name]['add'] = part_list

    def insertModNets_del(self,net_name, part_list):
        if net_name not in self.ndiff['mod']:
            self.ndiff['mod'][net_name] = {}    #Create Dictionary if not there
        self.ndiff['mod'][net_name]['del'] = part_list

    def getModNets_add(self,net_name):
        #return the list of new net connections
        # <TO-DO> Add Error handing, does the key exist????
        return self.ndiff['mod'][net_name]['add']

    def getModNets_del(self,net_name):
        # return the list of net connections removed
        # <TO-DO add error handling
        return self.ndiff['mod'][net_name]['del']

    def printAddNets (self):
        #This will print all added nets
        print (json.dumps(self.ndiff['add'], indent=4))

    def printDelNets(self):
        print (json.dumps(self.ndiff['del'], indent=4))

    def printModNets (self):
        # This will print all modifed nets
        print (json.dumps(self.ndiff['mod'], indent=4))
    #end-class diffNL
#END
