from pm4pydistr.configuration import PARAMETERS_PORT, PARAMETERS_HOST, PARAMETERS_MASTER_HOST, PARAMETERS_MASTER_PORT, \
    PARAMETERS_CONF, BASE_FOLDER_LIST_OPTIONS, PARAMETERS_AUTO_HOST, PARAMETERS_AUTO_PORT

from pm4pydistr.slave.slave_service import SlaveSocketListener
from pm4pydistr.slave.slave_requests import SlaveRequests
from pathlib import Path
from pm4py.objects.log.importer.parquet import factory as parquet_importer
from pm4pydistr.slave.do_ms_ping import DoMasterPing
import uuid
import socket
from contextlib import closing

import os
import shutil

import time

from pm4py.algo.conformance.alignments.versions import state_equation_a_star
from pm4py.algo.conformance.tokenreplay.versions import token_replay

from pm4py.objects.petri.importer.versions import pnml as pnml_importer
from pm4py.objects.petri.exporter.versions import pnml as pnml_exporter

from pm4pydistr.slave.recomposition import perform_recomposition



def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


class Slave:
    def __init__(self, parameters):
        self.parameters = parameters
        self.host = parameters[PARAMETERS_HOST]
        self.port = str(parameters[PARAMETERS_PORT])
        self.master_host = parameters[PARAMETERS_MASTER_HOST]
        self.master_port = str(parameters[PARAMETERS_MASTER_PORT])
        self.conf = parameters[PARAMETERS_CONF]
        if PARAMETERS_AUTO_HOST in parameters and parameters[PARAMETERS_AUTO_HOST] == "1":
            self.conf = str(uuid.uuid4())
            self.host = str(socket.gethostname())
        if PARAMETERS_AUTO_PORT in parameters and parameters[PARAMETERS_AUTO_PORT] == "1":
            self.port = str(find_free_port())
        self.id = None
        self.ping_module = None

        self.filters = {}

        if not os.path.exists(self.conf):
            os.mkdir(self.conf)

        # sleep a while before taking the slaves up :)
        time.sleep(2)

        self.slave_requests = SlaveRequests(self, self.host, self.port, self.master_host, self.master_port, self.conf)

        self.service = SlaveSocketListener(self, self.host, self.port, self.master_host, self.master_port, self.conf)
        self.service.start()

        # sleep a while before taking the slaves up :)
        time.sleep(2)

        self.slave_requests.register_to_webservice()

    def create_folder(self, folder_name):
        # print("create folder " + str(folder_name))
        if not os.path.isdir(os.path.join(self.conf, folder_name)):
            os.mkdir(os.path.join(self.conf, folder_name))

    def load_log(self, folder_name, log_name):
        # print("loading log " + str(log_name)+" into "+str(folder_name))
        if not os.path.exists(os.path.join(self.conf, folder_name, log_name)):
            for folder in BASE_FOLDER_LIST_OPTIONS:
                if folder_name in os.listdir(folder):
                    list_paths = parquet_importer.get_list_parquet(os.path.join(folder, folder_name))
                    list_paths_corr = {}
                    for x in list_paths:
                        list_paths_corr[Path(x).name] = x
                    if log_name in list_paths_corr:
                        # print("log_name",log_name," in ",os.path.join(folder, folder_name),list_paths_corr[log_name])
                        shutil.copyfile(list_paths_corr[log_name], os.path.join(self.conf, folder_name, log_name))

    def enable_ping_of_master(self):
        self.ping_module = DoMasterPing(self, self.conf, self.id, self.master_host, self.master_port)
        self.ping_module.start()


def perform_alignments(petri_string, var_list, parameters=None):
    if parameters is None:
        parameters = {}

    parameters["ret_tuple_as_trans_desc"] = True
    petri_net, im, fm = pnml_importer.import_petri_from_string(petri_string)
    varlistcost=0
    alignmentres=[]
    for variant in var_list:
        alignment= state_equation_a_star.apply_from_variant(variant[0], petri_net, im, fm)
        cost = alignment['cost']
        alignmentres.append({"variant: "+str(variant):alignment['alignment'],"cost": alignment['cost']})
        varlistcost =varlistcost+(variant[1]*cost)
    # order alignments



    return {"alignment_result": alignmentres, "varlist_cost": varlistcost}



def calculate_decomp_alignments(subnets_string, var_list):
    print("check5: a slave processes the request (alignments and recomposition should take place here)")
    #print("The slave has received the varlist:", var_list)
    # The decomposed subnets are stored in this list as petri net object with initial an final marking
    subnets = [(pnml_importer.import_petri_from_string(net)) for net in subnets_string] 

    
    result = perform_recomposition(subnets, var_list)

    print("calculation successful for a slave")
    return result



def perform_token_replay(petri_string, var_list, parameters=None):
    if parameters is None:
        parameters = {}

    parameters["return_names"] = True

    return token_replay.apply_variants_list_petri_string(var_list, petri_string, parameters=parameters)
