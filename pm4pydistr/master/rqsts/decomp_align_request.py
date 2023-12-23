from pm4pydistr.master.rqsts.basic_request import BasicMasterRequest
from pm4pydistr.configuration import KEYPHRASE
import requests
import json
from pm4py.objects.log.util import xes


class DecompAlignRequest(BasicMasterRequest):
    def __init__(self, session, target_host, target_port, use_transition, no_samples, process, content):
        print("check3: create post request from master to slaves")
        self.session = session
        self.target_host = target_host
        self.target_port = target_port
        self.content = content
        self.use_transition = use_transition
        self.no_samples = no_samples
        self.process = process
        BasicMasterRequest.__init__(self, None, target_host, target_port, use_transition, no_samples, content)

    def run(self):
        uri = "http://" + self.target_host + ":" + self.target_port + "/calculateDecompAlignments?keyphrase=" + KEYPHRASE + "&use_transition=" + str(
            self.use_transition) + "&no_samples=" + str(self.no_samples) + "&process=" + str(
            self.process)

        r = requests.post(uri, data=json.dumps(self.content))
        self.content = json.loads(r.text)
