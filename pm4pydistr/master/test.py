import unittest
import functions
from pm4py.objects.petri.importer import versions
import os


class FunctionsTestCase(unittest.TestCase):
  
    
    #########################################################################################
    # Decomposition
     
    
    def IsEqual(net_1, net_2):
        # checking for equality of petri nets
        p_1, im_1, fm_1 = net_1
        p_2, im_2, fm_2 = net_2
        
        places_1 = [x.name for x in p_1.places]
        places_1.sort()
        places_2 = [x.name for x in p_2.places]
        places_2.sort()
        
        if (places_1 != places_2):
            return False
            
        
        if str(im_1) != str(im_2):
            return False
        
        if str(fm_1) != str(fm_2):
            return False
        
        trans_1 = [str(x) for x in p_1.transitions]
        trans_1.sort()
        trans_2 = [str(x) for x in p_2.transitions]
        trans_2.sort()
               
        if (trans_1 != trans_2):
            return False
                
        arcs_1 = [str(x) for x in p_1.arcs]
        arcs_1.sort()
        arcs_2 = [str(x) for x in p_1.arcs]
        arcs_2.sort()
                
        if (arcs_1 != arcs_2):
            return False
        
        return True
    
    
    
    def GetOutputFiles(case_id):
        path = '../../lab_testfiles/testcases'
        prefix = 'output_{}'.format(case_id)
        return [os.path.join(path,i) for i in os.listdir(path) if os.path.isfile(os.path.join(path,i)) and i.startswith(prefix)]
    
    
    
    def test_Decomposition(self):
        DecompositionTestCases = [1, 2]
        for case_id in DecompositionTestCases:
            net, initial_marking, final_marking = versions.pnml.import_net(("../../lab_testfiles/testcases/input_{}.pnml".format(case_id)))
            decomposition = functions.DecomposeModel(net, initial_marking, final_marking)
            
            # get coorect output files and check count equality
            files = FunctionsTestCase.GetOutputFiles(case_id)
            self.assertEqual(len(decomposition), len(files), 'different count of sub nets')
    
            for i in range(len(files)):
                net = versions.pnml.import_net(files[i])
                sysnet = None;
                for s in decomposition:
                    if FunctionsTestCase.IsEqual(s, net):
                        sysnet = s
                        break
                       
                # assert sub net found
                self.assertNotEqual(sysnet, None, 'sub not not found in the correct output')
                decomposition.remove(sysnet)
      

    
    #########################################################################################
    # Alignments Parameters
                 
                
    def test_AlignmentParameters(self):
        net, initial_marking, final_marking = versions.pnml.import_net("../../lab_testfiles/testcases/input_2.pnml")
        subnets = functions.DecomposeModel(net, initial_marking, final_marking)
        
        costs = {
                'a': 1/3,
                'b': 1,
                'c': 1/2,
                'd': 1/3,
                'e': 1/3,
                'f': 1/2,
                'g': 1/2,
                'h': 1/2
                }
        
        parameters = functions.GetAlignmentParameters(subnets)
        for param in parameters.values():
            cost_function = param['model_cost_function']
            for t, c in cost_function.items():
                if str(t) in costs.keys():
                    self.assertEqual(c, costs[str(t)], 'cost value different for transition \"{}\"'.format(t))

    #########################################################################################
    # Alignments

    
    def IsEqualAlignment(alignment_1, alignment_2):
        if alignment_1 == alignment_2:
            return True
        if alignment_1['cost'] != alignment_2['cost']:
            return False
        if alignment_1['alignment'] != alignment_2['alignment']:
            return False
        return True
    

    def test_Alignment(self):
        net, initial_marking, final_marking = versions.pnml.import_net("../../lab_testfiles/testcases/input_2.pnml")
        subnets = functions.DecomposeModel(net, initial_marking, final_marking)
        parameters = functions.GetAlignmentParameters(subnets)
        alignments = functions.PrefromAlignment(['a,b,d,e,c,d,g,f,h'], subnets, parameters)
        alignments = [v[0] for k,v in alignments.items() ]
        correctAlignments = [
                {'alignment': [('g', 'g'), ('f', 'f'), ('>>', None), ('h', '>>')], 'cost': 0.5}, 
                {'alignment': [('a', 'a'), ('b', 'b'), ('d', 'd'), ('e', 'e'), ('>>', None), ('d', 'd')], 'cost': 0}, 
                {'alignment': [('d', '>>'), ('c', 'c'), ('d', 'd')], 'cost': 1/3}, 
                {'alignment': [('d', 'd'), ('e', '>>'), ('d', 'd'), ('>>', None), ('g', 'g'), ('f', 'f'), ('h', 'h')], 'cost': 1/3}, 
                {'alignment': [('a', 'a')], 'cost': 0},
                {'alignment': [('d', 'd'), ('>>', None), ('e', '>>'), ('d', 'd'), ('g', 'g'), ('f', 'f'), ('h', 'h')], 'cost': 1/3},
                {'alignment': [('a', '>>'), ('e', 'e'), ('c', 'c')], 'cost': 1/3}]
        
        for aa in alignments:
            match = None
            for ca in correctAlignments:
                if FunctionsTestCase.IsEqualAlignment(ca, aa):
                    match = ca
                    break
            
            if aa is not None:
                self.assertNotEqual(match, None, 'alignment does not belong to the correct alignment set')
            correctAlignments.remove(match)
            
    
        
if __name__ == '__main__':
    unittest.main()