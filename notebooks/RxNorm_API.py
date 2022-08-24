import requests
import traceback
from rxnorm_restful_api import RXNORM_RESTFUL_API
from config import create_logger, REQUESTS_TIMEOUT
import xml.etree.cElementTree as ET
import pandas as pd
import numpy as np

headers = {'Accept': 'application/json',
           'user-agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'}

class RxNorm:
    def __init__(self):
        self.rxnorm_restful_api = RXNORM_RESTFUL_API()
        self.logger = None
        self.timeout = REQUESTS_TIMEOUT
        self.session = requests.Session()

    def approximate_term(self, task='get_approximate_term', **kwargs):
        self.logger = create_logger(task)
        self.logger.info(f'start task {task}...')
        
        if 'timeout' in kwargs:
            self.timeout = kwargs.get('timeout')

        if task == 'get_approximate_term':
            assert 'term' in kwargs, 'term must be provided for this task'
            return self.__get_approximate_term(term=kwargs.get('term'))

        # reset timeout to config timeout
        self.timeout = REQUESTS_TIMEOUT

    def __get_approximate_term(self, term):
        rest_api = self.rxnorm_restful_api.get_approx_term(term)
        #self.logger.info(f'restful api: {rest_api}')

        info = self.session.get(rest_api, headers=headers, timeout=self.timeout)
        #self.logger.info(f'status: {info.status_code}')
        if info.text == 'null':
            return False
        tree = ET.fromstring(requests.get(rest_api).text)
        rxcui = tree.findall('.//rxcui')[0] ## need to add an if statement, that if the score is less than X, return "no-match"
        return rxcui.text


    
    def get_codes(self, task='get_rxcui_codes', **kwargs):
        self.logger = create_logger(task)
        self.logger.info(f'start task {task}...')
        
        if 'timeout' in kwargs:
            self.timeout = kwargs.get('timeout')

        if task == 'get_rxcui_codes':
            assert 'rxcui' in kwargs, 'term must be provided for this task'
            return self.__get_rxcui_codes(rxcui=kwargs.get('rxcui'))
            
        # reset timeout to config timeout
        self.timeout = REQUESTS_TIMEOUT
    
    def __get_rxcui_codes(self, rxcui):
        rest_api = self.rxnorm_restful_api.get_rxcui_codes(rxcui)
        #self.logger.info(f'restful api: {rest_api}')

        info = self.session.get(rest_api, headers=headers, timeout=self.timeout)
        #self.logger.info(f'status: {info.status_code}')
        if info.text == 'null':
            return False
        tree = ET.fromstring(requests.get(rest_api).text)
        SNOMED_CT = [code.text for code in tree.findall(".//propConcept[propName='SNOMEDCT']/propValue")]
        MMSL = [code.text for code in tree.findall(".//propConcept[propName='MMSL_CODE']/propValue")]

        if not SNOMED_CT:
            SNOMED_CT = ['NULL']
        if not MMSL:
            MMSL = ['NULL']

        return pd.DataFrame(data = np.array([', '.join(SNOMED_CT),', '.join(MMSL)]).reshape(1,-1), columns = ['SNOMEDCT','MMSL'])


    def get_names(self, task='get_rxcui_names', **kwargs):
        self.logger = create_logger(task)
        self.logger.info(f'start task {task}...')
        
        if 'timeout' in kwargs:
            self.timeout = kwargs.get('timeout')

        if task == 'get_rxcui_names':
            assert 'rxcui' in kwargs, 'term must be provided for this task'
            return self.__get_rxcui_names(rxcui=kwargs.get('rxcui'))
            
        # reset timeout to config timeout
        self.timeout = REQUESTS_TIMEOUT
    
    def __get_rxcui_names(self, rxcui):
        rest_api = self.rxnorm_restful_api.get_rxcui_names(rxcui)
        #self.logger.info(f'restful api: {rest_api}')

        info = self.session.get(rest_api, headers=headers, timeout=self.timeout)
        #self.logger.info(f'status: {info.status_code}')
        if info.text == 'null':
            return False
        tree = ET.fromstring(requests.get(rest_api).text)
        try:
            name = tree.findall(".//propConcept[propName='RxNorm Name']/propValue")[0]
            return name.text
        except:
            return 'NULL'

def test():
    rxnorm = RxNorm()
    term = "warfarin"
    rxcui = rxnorm.approximate_term(term = term)
    codes = rxnorm.get_codes(rxcui = rxcui)
    names = rxnorm.get_names(rxcui = rxcui)

    codes['Name'] = names
    codes['rxcui'] = rxcui
    codes['input_term'] = term

    codes = codes[['input_term','Name','rxcui','SNOMEDCT','MMSL']]

    print(codes)

if __name__ == '__main__':
    test()
