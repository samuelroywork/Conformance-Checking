from pm4py.objects.petri.importer import versions
import time
from functions import GetAlignmentParameters, DecomposeModel, PrefromAlignment, BorderAgreement



net, initial_marking, final_marking = versions.pnml.import_net(("../../lab_testfiles/paper_net.pnml"))
#subnets = DecomposeModel(net, initial_marking, final_marking)
#

#subnets.append(MergeModels(subnets))

trace = 'a,b,e,i,l,d,g,h,n,j,k,p,q'

subnets = [(net, initial_marking, final_marking)]
parameters = GetAlignmentParameters(subnets)
startTime = time.perf_counter()
alignments = PrefromAlignment([trace], subnets, parameters)
endTime = time.perf_counter()

cost = 0
for k,v in alignments.items():   
    if v[0] != None:
        cost += v[0]['cost']
        #print(v[0]['alignment'])

print("Classical approach time:", endTime - startTime, ', cost =' , cost)



subnets = DecomposeModel(net, initial_marking, final_marking)
startTime = time.perf_counter()
alignments = PrefromAlignment([trace], subnets, GetAlignmentParameters(subnets))
alignments = BorderAgreement(alignments, 0, trace)
endTime = time.perf_counter()
cost = 0
for k,v in alignments.items():   
    if v[0] != None:
        cost += v[0]['cost']
        #print(v[0]['alignment'])

print("Decomposing/recomposing approach time:", endTime - startTime, ', cost =' , cost)

# parameters = GetAlignmentParameters(subnets)
# log = xes_importer.import_log("../../lab_testfiles/running-example.xes")
# variants = list(variants_filter.get_variants_from_log_trace_idx(log).keys())
# variants = ['sdds,dsdsde,frew']
# alignments = PrefromAlignment(variants, subnets, parameters)


# cost = 0
# for k,v in alignments.items():
#     cost += v[0]['cost']
#     if (v[0]['cost'] != 0):
#         print(str(v[0]['alignment'])+  " , cost = "+str( v[0]['cost']))
    
# print("Total cost for the first trace: {}".format(cost))

#for visualization
import os
from pm4py.visualization.petrinet import factory as pn_vis_factory

os.environ["PATH"] += os.pathsep + "C:\\Program Files (x86)\\Graphviz2.38\\bin"
gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters={"format":"svg"})
pn_vis_factory.save(gviz, "nets\\main.svg")
for i in range(len(subnets)): 
    net, initial_marking, final_marking = subnets[i]
    gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters={"format":"svg"})
    pn_vis_factory.save(gviz, "nets\\subnet-{}.svg".format(i+1))



