''' Class for a making a new tree based in a TChain in a Sample.
'''

# Standard imports
import ROOT
import copy

# Logging
import logging
logger = logging.getLogger(__name__)

# RootTools
from RootTools.core.LooperBase import LooperBase
from RootTools.core.TreeVariable import ScalarTreeVariable, VectorTreeVariable, TreeVariable
class TreeMaker( LooperBase ):

    def __init__(self, variables, filler = None, treeName = "Events"):
        
        for v in variables:
            if not isinstance(v, TreeVariable):
                raise ValueError( "Not a proper variable: %r '%s'"%(v,v) )

        super(TreeMaker, self).__init__( variables = variables)

        self.makeClass( "data", variables = variables, useSTDVectors = False, addVectorCounters = True)

        # Create tree to store the information and store also the branches
        self.treeIsExternal = False
        self.tree = ROOT.TTree( treeName, treeName )
        self.branches = []
        self.makeBranches()

        # function to fill the data 
        self.filler = filler

    def cloneWithoutCompile(self, externalTree = None):
        ''' make a deep copy of self to e.g. avoid re-compilation of class in a loop. 
            Reset TTree as to not create a memory leak.
        '''
        # deep copy by default
        res = copy.deepcopy(self)
        res.branches = []

        # remake TTree
        treeName = self.tree.GetName()
        if res.tree: res.tree.IsA().Destructor( res.tree )
        if externalTree:
            res.treeIsExternal = True
            assert self.tree.GetName() == externalTree.GetName(),\
                "Treename inconsistency (instance: %s, externalTree: %s). Change one of the two"%(treeName, externalTree.GetName())
            res.tree = externalTree
        else:
            res.treeIsExternal = False
            res.tree = ROOT.TTree( treeName, treeName )

        res.makeBranches()

        return res

    def makeBranches(self):

        scalerCount = 0
        for s in LooperBase._branchInfo( self.variables, restrictType = ScalarTreeVariable, addVectorCounters = True):
            self.branches.append( 
                self.tree.Branch(s['name'], ROOT.AddressOf( self.data, s['name']), '%s/%s'%(s['name'], s['type']))
            )
            scalerCount+=1

        vectorCount = 0
        for s in LooperBase._branchInfo( self.variables, restrictType = VectorTreeVariable, addVectorCounters = True ):
            self.branches.append(
                self.tree.Branch(s['name'], ROOT.AddressOf( self.data, s['name'] ), "%s[%s]/%s"%(s['name'], s['counterInt'], s['type']) )
            )
            vectorCount+=1
        logger.debug( "TreeMaker created %i new scalars and %i new vectors.", scalerCount, vectorCount )

    def clear(self):
        if self.tree: self.tree.IsA().Destructor( self.tree )

    def fill(self):
        # Write to TTree
        if self.treeIsExternal:
            for b in self.branches:
                b.Fill()
        else:
            self.tree.Fill()

    def _initialize(self):
        self.position = 0
        # Initialize struct
        self.data.init()
        pass

    def _execute(self):
        ''' Use filler to fill struct and then fill struct to tree'''
        # FIXME for sequence!
        if (self.position % 10000)==0:
            logger.info("TreeMaker is at position %6i", self.position)

        # Call external filler method: variables first
        if self.filler:
            self.filler( self.data )

        self.fill()

        # Initialize struct
        self.data.init()
 
        return 1 
