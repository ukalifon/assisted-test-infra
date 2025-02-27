import json
import logging
import os

from python_terraform import Terraform, IsFlagged


class TerraformUtils:
    VAR_FILE = "terraform.tfvars.json"
    STATE_FILE = "terraform.tfstate"

    def __init__(self, working_dir):
        logging.info("TF FOLDER %s ", working_dir)
        self.working_dir = working_dir
        self.var_file_path = os.path.join(working_dir, self.VAR_FILE)
        self.tf = Terraform(working_dir=working_dir, state=self.STATE_FILE, var_file=self.VAR_FILE)
        self.init_tf()

    def init_tf(self):
        self.tf.cmd("init -plugin-dir=/root/.terraform.d/plugins/", raise_on_error=True)

    def apply(self, refresh=True):
        return_value, output, err = self.tf.apply(no_color=IsFlagged, refresh=refresh,
                                                  input=False, skip_plan=True)
        if return_value != 0:
            message = f'Terraform apply failed with return value {return_value}, output {output} , error {err}'
            logging.error(message)
            raise Exception(message)

    def change_variables(self, variables, refresh=True):
        with open(self.var_file_path, "r+") as _file:
            tfvars = json.load(_file)
            tfvars.update(variables)
            _file.seek(0)
            _file.truncate()
            json.dump(tfvars, _file)
        self.apply(refresh=refresh)

    def get_state(self):
        self.tf.read_state_file(self.STATE_FILE)
        return self.tf.tfstate

    def set_new_vip(self, api_vip):
        self.change_variables(variables={"api_vip": api_vip}, refresh=True)

    def destroy(self):
        self.tf.destroy(force=True, input=False, auto_approve=True)
