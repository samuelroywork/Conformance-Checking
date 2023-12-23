import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.append('E:\Lab\GitHub\Conformance-Checking-Lab')
import pm4pycvxopt
import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.visualization.petrinet import factory as vis_factory
from pm4py.algo.conformance.alignments import factory as alignments_factory
from pm4py.objects.petri.importer.versions import pnml as pnml_importer
from pm4py.objects.petri.exporter.versions import pnml as pnml_exporter
from collections import Counter
from pm4py.algo.filtering.log.variants import variants_filter
import pm4pydistr.slave.functions as functions
from pm4py.algo.conformance.alignments.versions import state_equation_a_star  as align
from pm4py.objects.petri import utils
from pm4py.objects.petri.petrinet import PetriNet, Marking
from pm4py.visualization.petrinet import factory as pn_vis_factory
import copy
import recomposition





def perform_recomposition(subnets, varlist):
    #print(subnets)
    alignmentres=[]
    #get the border trace
    border_trace= get_border_trans(subnets)
    varlistcost=0
    print(border_trace)
    i=1
    for variant in varlist:
        subnets_copy = copy.deepcopy(subnets)
        result =perform_alignment(variant[0],subnets_copy)
        print ( "Nets has been recomposed")
        print(result)
        cost=0
        alignments=[]
        j=1
        for aligment in result:
            if aligment is not None:
                #print(aligment)
                cost = cost + aligment['cost']
                alignments.append({"aligment"+str(j):aligment['alignment'],"cost"+str(j): aligment['cost']})
                j+=1
        varlistcost =varlistcost+(variant[1]*cost)
        alignmentres.append({"Variant"+str(i):alignments})
        i+=1
    print("cost ")
    print("recomp alignments", varlistcost)
    return {"alignment_result": alignmentres, "varlist_cost": varlistcost}

def perform_alignment(variant, nets):
    #after the subnet are recomposed for a trace do we use the recomposed for the next traces or we  use the original nets list
    result = []
    nets_plus_alignment =[]
    subnets_copy = copy.deepcopy(nets)
    projectedVariant = functions.ProjectVariant(variant, nets)
    parameters = functions.GetAlignmentParameters(nets)
    print("projectedVariant")
    print(projectedVariant)
    for i in range(len(nets)): 
        petrinet, im, fm = nets[i]
        print(petrinet.transitions)
        gviz = pn_vis_factory.apply(petrinet, im, fm, parameters={"format":"svg"})
        pn_vis_factory.save(gviz, "nets\\recomposed_subnet-{}.svg".format(i+1))
    for net in nets:
        test = projectedVariant[net]
        if len(projectedVariant[net]) > 0:
            print("............................")
            print(projectedVariant[net])
            print(net[0].transitions)
            #print(net[0].arcs)
            alignment = align.apply_from_variant(projectedVariant[net], net[0], net[1], net[2])#, parameters[net])
            print("alignment")
            #print(alignment)
            result.append(alignment)
            nets_plus_alignment.append((net[0],alignment,net[1], net[2]))
        else:
            result.append(None)
            nets_plus_alignment.append((net[0],None,net[1], net[2]))
    merged_net = merge_all_borderissue(nets_plus_alignment)
    while len(merged_net) != len(subnets_copy):
        subnets_copy = copy.deepcopy(merged_net)
        return perform_alignment(variant,subnets_copy)
    print("result")
    #print(result)
    return ( result )


def get_border_trans(subnets_list):
    border=[]
    #get the border transitions and the number of subnet where they occur
    for net, i, f in subnets_list:
        for trans in net.transitions:
            if len(trans.out_arcs)==0 or len(trans.in_arcs)==0:
                border= border + [trans.label]
    return border


#subnet that doesn' meet the requirement have to be merged
def merge_all_borderissue(subnet_alignment):
    l=subnet_alignment
    taken=[False]*len(l)
    ret=[]
    for i,node in enumerate(l):
        if not taken[i]:
            result = dfs(l,node,i, taken)
            if result is not None:
                ret.append(result)
    print(len(ret))
    return ret


def dfs(subnet_alignment, node,index,taken):
    taken[index]=True
    ret=node
    result=node[0]
    initial_m= node[2]
    final_m =node[3]
    if ret[1] is None:
        return (result,initial_m, final_m)
    for i,item in enumerate(subnet_alignment):
        nextstep= False
        if not taken[i]:
            if item[1] is None:
                continue
            item_move =  item[1]['alignment']
            node_move =  ret[1]['alignment']
            intersec=[]
            for trans in ret[0].transitions:
                if (len(trans.out_arcs)==0 or len(trans.in_arcs)==0) and trans.label is not None and trans.label in [x.label for x in item[0].transitions]:
                    intersec.append(trans)
        #intersec= set(concern_trans_item).intersection(set(concern_trans_node))
            
            if  len(intersec)>0:
                print("intersection is there")
                for activity in intersec:
                    concern_moves_item = [x for x in item_move if x[0]==activity.label or x[1]== activity.label]
                    concern_moves_node = [x for x in node_move if x[0]==activity.label or x[1]== activity.label]
                    if len(concern_moves_item)==0 or len(concern_moves_node)==0:
                        nextstep= True
                        continue
                    #if they dont have the same number then merge
                    if len(concern_moves_item) != len(concern_moves_node) or len([x for x in concern_moves_item if x in [y for y in concern_moves_node]]) != len(concern_moves_item) or not concern_moves_item == concern_moves_node :
                        print("no border aggreement")
                        print(concern_moves_item)
                        print(concern_moves_node)
                        #helper, im, fm= dfs(subnet_alignment,item,i,taken)
                        # nodenet = PetriNet(result.name)
                        # for place in result.places:
                        #     nodenet.places.add(place)
                        # for transition in result.transitions:
                        #     nodenet.transitions.add(transition)
                        # for netarc in result.arcs:
                        #     utils.add_arc_from_to(netarc.source, netarc.target,nodenet)
                        
                        #result =nodenet
                        return functions.MergeModels([(result, initial_m, final_m), dfs(subnet_alignment,item,i,taken)])
                        # for place in helper.places:
                        #     result.places.add(place)
                        #     out_arcs =place.out_arcs.copy()
                        #     in_arcs =place.in_arcs.copy()
                        #     for arc in out_arcs:
                        #         if arc not in result.arcs:
                        #             common_trans=[x for x in result.transitions if x.label is arc.target.label and arc.target.label is not None]
                        #             if arc.target.label is None or arc.target.label not in [x.label for x in result.transitions]:
                        #                 t= arc.target
                        #                 result.transitions.add(t)
                        #                 a=[x for x in result.arcs if x.source.name is place.name and x.target.name is t.name]
                        #                 if len(a)==0:
                        #                     utils.add_arc_from_to(place,t,result)
                        #             else:
                        #                 for trans in common_trans:
                        #                     a=[x for x in result.arcs if x.source.name is place.name and x.target.name is trans.name]
                        #                     if len(a)==0:
                        #                         utils.add_arc_from_to(place, trans ,result)

                        #     for arc in in_arcs:
                        #         if arc not in result.arcs:
                        #             common_trans = [x for x in result.transitions if x.label == arc.source.label and arc.source.label is not None]
                        #             if arc.source.label is None or  arc.source.label not in [x.label for x in result.transitions]:
                        #                 t= arc.source
                        #                 result.transitions.add(t)
                        #                 a=[x for x in result.arcs if x.source.name is t.name and x.target.name is place.name]
                        #                 if len(a)==0:
                        #                     utils.add_arc_from_to(t,place,result)
                        #             else:
                        #                 for trans in common_trans:
                        #                     a=[x for x in result.arcs if x.source.name is trans.name and x.target.name is place.name]
                        #                     if len(a)==0:
                        #                         utils.add_arc_from_to(trans, place ,result)
                                            
                        
                        # for m,count in im.items():
                        #     initial_m[m] = count
                        # for f, count in fm.items():
                        #     final_m[f] = count
                        
                    else:
                        print( "border aggree")
            if nextstep:
                continue
    print(initial_m)
    print(final_m)                                     
    return (result, initial_m, final_m)




#log = xes_importer.apply("E:\Lab\log_IEEE.xes_\log_IEEE filtered.xes")

#net, im, fm = pnml_importer.import_net(os.path.join("tests","input_data","E:\Lab\Petrinet\petrinet.pnml"))

#print("Traces to align "+ str(len(log)))
#variants = list(variants_filter.get_variants_from_log_trace_idx(log).keys())
#subnets = functions.DecomposeModel(net,im,fm)
#alignments = perform_recomposition(subnets,variants)
#print(alignments)

net, initial_marking, final_marking = pnml_importer.import_net(("../../lab_testfiles/paperNet.pnml"))
subnets = functions.DecomposeModel(utils.remove_unconnected_components(net), initial_marking, final_marking)
# for i in range(len(subnets)): 
#     net, initial_marking, final_marking = subnets[i]
#     gviz = pn_vis_factory.apply(net, initial_marking, final_marking, parameters={"format":"svg"})
#     pn_vis_factory.save(gviz, "nets\\subnet-{}.svg".format(i+1))
#log = xes_importer.import_log("../../lab_testfiles/running-example.xes")
#variants = list(variants_filter.get_variants_from_log_trace_idx(log).keys())
var_list_paper = [["a,c,f,m,d,g,j,k,h,n,p,q", 1]]
#var_list_paper = [["a,b,e,i,l,d,g,j,h,k,n,p,q", 20], ["a,c,f,m,d,g,j,k,h,n,p,q", 5], ["a,e,i,l,d,g,j,h,k,n,p,q", 5]]
alignments = perform_recomposition(subnets, var_list_paper)
print(alignments)








