import pm4pycvxopt
import os
import pm4pydistr.slave.functions as functions
from pm4py.algo.conformance.alignments.versions import state_equation_a_star  as align
import copy



def perform_recomposition(subnets, varlist):
    alignmentres=[]
    varlistcost=0
    for variant in varlist:
        result =perform_alignment(variant[0],subnets)
        cost=0
        alignments=[]
        for aligment, projection in result:
            if aligment is not None:
                cost = cost + aligment['cost']
                diff=""
                if projection == variant[0]:
                    diff="Difference here"
                alignments.append({"projection: "+str(projection)+str(diff):aligment['alignment'],"cost": aligment['cost']})
        varlistcost =varlistcost+(variant[1]*cost)
        alignmentres.append({variant[0]:alignments})
        # order alignments
    return {"alignment_result": alignmentres, "varlist_cost": varlistcost}

def perform_alignment(variant, nets):
    #after the subnet are recomposed for a trace do we use the recomposed for the next traces or we  use the original nets list
    result = []
    nets_plus_alignment =[]
    subnets_copy = copy.deepcopy(nets)
    projectedVariant = functions.ProjectVariant(variant, nets)
    #parameters = functions.GetAlignmentParameters(nets)
    for net in nets:
        if len(projectedVariant[net]) > 0:
            alignment = align.apply_from_variant(projectedVariant[net], net[0], net[1], net[2])#, parameters[net])
            result.append((alignment, projectedVariant[net]))
            nets_plus_alignment.append((net[0],alignment,net[1], net[2]))
        else:
            result.append((None, None))
            nets_plus_alignment.append((net[0],None,net[1], net[2]))
    merged_net = merge_all_borderissue(nets_plus_alignment)
    while len(merged_net) != len(subnets_copy):
        subnets_copy = copy.deepcopy(merged_net)
        return perform_alignment(variant,subnets_copy)
    return ( result)



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
            if  len(intersec)>0:
                for activity in intersec:
                    concern_moves_item = [x for x in item_move if x[0]==activity.label or x[1]== activity.label]
                    concern_moves_node = [x for x in node_move if x[0]==activity.label or x[1]== activity.label]
                    if len(concern_moves_item)==0 or len(concern_moves_node)==0:
                        nextstep= True
                        continue
                    #if they dont have the same number then merge
                    if len(concern_moves_item) != len(concern_moves_node) or len([x for x in concern_moves_item if x in [y for y in concern_moves_node]]) != len(concern_moves_item) or not concern_moves_item == concern_moves_node :
                        return functions.MergeModels([(result, initial_m, final_m), dfs(subnet_alignment,item,i,taken)])
                        
            if nextstep:
                continue                                  
    return (result, initial_m, final_m)