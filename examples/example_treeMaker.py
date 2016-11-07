''' Simple example of a TreeMaker. Creates a new TTree by looping a TreeReader over a sample and filling.
'''

# Standard imports
import sys
import logging
import ROOT

#RootTools
from RootTools.core.standard import *

# argParser
import argparse
argParser = argparse.ArgumentParser(description = "Argument parser")
argParser.add_argument('--logLevel', 
      action='store',
      nargs='?',
      choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG', 'TRACE', 'NOTSET'],
      default='INFO',
      help="Log level for logging"
)

args = argParser.parse_args()
logger = get_logger(args.logLevel, logFile = None)


# from files
s0 = Sample.fromFiles("s0", files = ["example_data/file_0.root"], treeName = "Events")

read_variables =  [ TreeVariable.fromString( "nJet/I"), TreeVariable.fromString('Jet[pt/F,eta/F,phi/F]' ) ] \
                + [ TreeVariable.fromString(x) for x in [ 'met_pt/F', 'met_phi/F' ] ]

new_variables =     [ TreeVariable.fromString('MyJet[pt2/F]' ) ] \
                  + [ TreeVariable.fromString(x) for x in [ 'myMetOver2/F' ] ]

# Define a reader
reader = s0.treeReader( variables = read_variables,  selectionString = "met_pt>50")

# Define a filler

#A simple eample
def filler(struct):
    struct.nMyJet = reader.data.nJet
    for i in range(reader.data.nJet):
        struct.MyJet_pt2[i] = reader.data.Jet_pt[i]**2
    struct.myMetOver2 = reader.data.met_pt/2.
    return

maker  =    TreeMaker( filler = filler, variables = new_variables )
reader.start()
maker.start()
while reader.run():
    maker.run()
