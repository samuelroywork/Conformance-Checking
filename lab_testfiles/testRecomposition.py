

import pm4pycvxopt
import sys
# # insert at 1, 0 is the script path (or '' in REPL)
# sys.path.append('C:\\Users\\Mo\\OneDrive - rwth-aachen.de\\Uni\\2.Semester\\Praktikum\\Git Project\\Conformance-Checking-Lab')

from pm4pydistr.slave.recomposition import perform_recomposition
from pm4py.objects.petri.importer.versions import pnml as pnml_importer
from pm4pydistr.slave.functions import DecomposeModel

net, im, fm = pnml_importer.import_net("paperNet.pnml")

subnets = DecomposeModel(net, im, fm)


var_list_paper = []
var_list_paper.append(["a,b,e,i,l,d,g,j,h,k,n,p,q", 10])
var_list_paper.append(["a,c,f,m,d,g,j,k,h,n,p,q", 10])
var_list_paper.append(["a,e,i,l,d,g,j,h,k,n,p,q", 10])

print(perform_recomposition(subnets, var_list_paper))
