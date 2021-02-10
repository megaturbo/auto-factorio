import base64
import hashlib
import hmac
import json
from urllib.parse import quote, urlencode
from urllib.request import urlopen


class Exoscale:
    API_ENDPOINT = 'https://api.exoscale.com/compute'

    __COMMAND_VM_LIST = 'listVirtualMachines'
    __COMMAND_VM_START = 'startVirtualMachine'
    __COMMAND_VM_STOP = 'stopVirtualMachine'
    __COMMAND_JOB_RESULT = 'queryAsyncJobResult'

    def __init__(self, server_id, api_key, api_secret):
        self.__server_id = server_id
        self.__api_key = api_key
        self.__api_secret = api_secret

    def request(self, command_name, command_params=None):
        """Generates a formatted and signed URL for exoscale API queries"""
        if command_params is None:
            command_params = {}
        command = {
                      'command': command_name,
                      'apikey': self.__api_key
                  } | command_params

        params = self.__sign(command)
        query_string = urlencode(params)

        url = f"{Exoscale.API_ENDPOINT}?{query_string}"
        with urlopen(url) as f:
            return json.load(f)

    def __sign(self, command):
        """
        Adds the signature bit to a command expressed as a dict.

        from: https://community.exoscale.com/api/compute/
        """
        # order matters
        arguments = sorted(command.items())

        # urllib.parse.urlencode is not good enough here.
        # key contains should only contain safe content already.
        # safe="*" is required when producing the signature.
        query_string = "&".join("=".join((key, quote(value, safe="*")))
                                for key, value in arguments)

        # Signing using HMAC-SHA1
        digest = hmac.new(
            self.__api_secret.encode("utf-8"),
            msg=query_string.lower().encode("utf-8"),
            digestmod=hashlib.sha1).digest()

        signature = base64.b64encode(digest).decode("utf-8")

        return dict(command, signature=signature)

    def is_machine_running(self):
        response = self.request(self.__COMMAND_VM_LIST, {'id': self.__server_id})
        return response['listvirtualmachinesresponse']['virtualmachine'][0]['state'] == 'Running'

    def start_machine(self):
        response = self.request(self.__COMMAND_VM_START, {'id': self.__server_id})
        return response['startvirtualmachineresponse']['jobid']

    def stop_machine(self):
        response = self.request(self.__COMMAND_VM_STOP, {'id': self.__server_id})
        return response['stopvirtualmachineresponse']['jobid']

    def job_result(self, job_id):
        response = self.request(self.__COMMAND_JOB_RESULT, {'jobid': job_id})
        return response['queryasyncjobresultresponse']
