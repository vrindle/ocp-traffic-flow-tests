import common
from logger import logger
from testConfig import TestConfig
from thread import ReturnValueThread
from task import Task
from host import Result
from typing import Optional
import sys
import yaml
import json
import jc

class GetVfRep(Task):
    def __init__(self, tft: TestConfig, node_name: str, tenant: bool):
        super().__init__(tft, 0, node_name, tenant)

        self.in_file_template = "./manifests/tools-pod.yaml.j2"
        self.out_file_yaml = f"./manifests/yamls/tools-pod-{self.node_name}-get-vf-rep.yaml"
        self.template_args["pod_name"] = f"tools-pod-{self.node_name}-get-vf-rep"
        self.template_args["test_image"] = common.TFT_TOOLS_IMG

        self.pod_name = self.template_args["pod_name"]

        common.j2_render(self.in_file_template, self.out_file_yaml, self.template_args)
        logger.info(f"Generated Server Pod Yaml {self.out_file_yaml}")
        
    def run_st(self) -> Result:
        cmd = f'exec -n default {self.pod_name} -- /bin/sh -c "crictl --runtime-endpoint=/host/run/crio/crio.sock ps -a --name=tools-pod-{self.node_name}-get-vf-rep -o json "'
        return self.run_oc(cmd)

    def run(self, duration: int):
        self.exec_thread = ReturnValueThread(target=self.run_st)
        self.exec_thread.start()

    def stop(self):
        logger.info(f"Stopping Get Vf Rep execution on {self.pod_name}")
        r = self.exec_thread.join()
        if r.returncode != 0:
            logger.info(r)
        ethtool_output = r.out
        data = json.loads(r.out)
        self.vf_rep= data["containers"][0]["podSandboxId"][:15]

        logger.debug(f"GetVfRep.stop(): {r.out}")
        logger.debug(f"GetVfRep.stop().vf_rep: {self.vf_rep}")
    def output(self):
        #TODO: handle printing/storing output here
        pass

