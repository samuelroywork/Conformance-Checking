import pm4pycvxopt
import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.petrinet import factory as vis_factory
from pm4py.algo.conformance.alignments import factory as alignments_factory
from pm4py.objects.petri.importer.versions import pnml as pnml_importer
from pm4py.objects.petri.exporter.versions import pnml as pnml_exporter
from pm4py.algo.filtering.log.variants import variants_filter
from pm4py.algo.conformance.alignments.versions import state_equation_a_star  as align
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.visualization.petrinet import factory as pn_vis_factory
import functions
from pm4py.objects.petri import utils

net, im, fm = pnml_importer.import_net(("../../lab_testfiles/paperNet.pnml"))
variants = "a,c,f,m,d,g,j,k,h,n,p,q"

   # parameters = functions.GetAlignmentParameters([[net, initial_marking,final_marking]])
aligment = align.apply_from_variant(variants, utils.remove_unconnected_components(net), im, fm)
print(aligment)

