from pm4py.visualization.petrinet.util import performance_map, vis_trans_shortest_paths as s, alignments_decoration
from pm4py.visualization.petrinet.util.vis_trans_shortest_paths import get_shortest_paths

def compute_fitness(cost_sum, loglength, net, sum_move_log):
    fitness=0.0
    spaths = get_shortest_paths(net)
    fitness =1-(cost_sum/(10000*(loglength*len(spaths)+sum_move_log)))
    return fitness