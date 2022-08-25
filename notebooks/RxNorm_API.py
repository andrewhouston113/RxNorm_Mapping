from select import select
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
        rxcui = [rxcui_.text for rxcui_ in tree.findall('.//rxcui')]
        return rxcui

    def primary_ingredient(self, task='get_primary_ingredient', **kwargs):
        self.logger = create_logger(task)
        self.logger.info(f'start task {task}...')
        
        if 'timeout' in kwargs:
            self.timeout = kwargs.get('timeout')

        if task == 'get_primary_ingredient':
            assert 'rxcui' in kwargs, 'rxcui must be provided for this task'
            return self.__get_primary_ingredient(rxcui=kwargs.get('rxcui'))

        # reset timeout to config timeout
        self.timeout = REQUESTS_TIMEOUT

    def __get_primary_ingredient(self, rxcui):
        rest_api = self.rxnorm_restful_api.get_primary_ingredient(rxcui)
        #self.logger.info(f'restful api: {rest_api}')

        info = self.session.get(rest_api, headers=headers, timeout=self.timeout)
        #self.logger.info(f'status: {info.status_code}')
        if info.text == 'null':
            return False

        tree = ET.fromstring(requests.get(rest_api).text)
        ingredient = [ing.text for ing in tree.findall(".//conceptGroup[tty='IN']/conceptProperties/rxcui")]
        
        if not ingredient:
            return 'NULL'
        else:
            return ingredient[0]

        

    
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
    term = "sodium chloride 0.9% intravenous solution 500 mL(s)"
    rxcui = rxnorm.approximate_term(term = term)

    i=0
    while i < len(rxcui):
        codes = rxnorm.get_codes(rxcui = rxcui[i])

        if (codes[['SNOMEDCT','MMSL']]=='NULL').all(axis=1).values[0]:
            i+=1
            codes = rxnorm.get_codes(rxcui = rxcui[i])
        else:
            selected_rxcui = rxcui[i]
            i=len(rxcui)
        
    if selected_rxcui == 'NULL':
        print(pd.DataFrame(np.array([term,'NULL',rxcui,'NULL','NULL']).reshape(1,-1), columns=['input_term','Name','rxcui','SNOMEDCT','MMSL']))
    else:
        primary_IN_rxcui = rxnorm.primary_ingredient(rxcui=selected_rxcui)

        if primary_IN_rxcui == 'NULL':
            primary_IN_rxcui = selected_rxcui

        #codes = rxnorm.get_codes(rxcui = primary_IN_rxcui)
        #names = rxnorm.get_names(rxcui = primary_IN_rxcui)

        #codes['Name'] = names
        #codes['rxcui'] = primary_IN_rxcui
        #codes['input_term'] = term

        #codes = codes[['input_term','Name','rxcui','SNOMEDCT','MMSL']]

        #print(codes)

if __name__ == '__main__':
    test()
