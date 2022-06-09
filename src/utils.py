import pandas as pd
import requests, json
from datetime import datetime

import os


def allocs_to_frame(json_allocations):
    alloc_list = []
    for json_alloc in json_allocations:
        #print(json_alloc)
        allocs = pd.DataFrame(json_alloc['allocations'])
        allocs.set_index('ticker', inplace=True)
        alloc_serie = allocs['alloc']
        alloc_serie.name = json_alloc['date'] 
        alloc_list.append(alloc_serie)
    all_alloc_df = pd.concat(alloc_list, axis=1).T
    return all_alloc_df


class ApiBmeHandler:
    
    def __init__(self, market):
        self.url_base = 'https://miax-gateway-jog4ew3z3q-ew.a.run.app'
        self.competi = 'mia_8'
        self.user_key = 'AIzaSyAKdNDiSWfA34KriNalTyAPIXJogTrYW1E'
        self.market = market
        
    def get_ticker_master(self):
        url = f'{self.url_base}/data/ticker_master'
        params = {'competi': self.competi,
                  'market': self.market,
                  'key': self.user_key
                  }
        response = requests.get(url, params)
        tk_master = response.json()
        maestro_df = pd.DataFrame(tk_master['master'])
        return maestro_df
    
    # def get_close_data_tck(self, tck):
    #     url = f'{self.url_base}/data/time_series'
    #     params = {'market': self.market,
    #               'key': self.user_key,
    #               'ticker': tck,
    #               'close':False
    #               }
    #     response = requests.get(url, params)
    #     tk_data = response.json()
    #     series_data = pd.read_json(tk_data, typ='series')
    #     return series_data

    def get_close_data_tck(self, tck, only_close):
        url2 = f'{self.url_base}/data/time_series'
        params = {'market': self.market,
              'key': self.user_key,
              'ticker': tck,
              'close': only_close}
        response = requests.get(url2, params)
        tk_data = response.json()

        if only_close:
            df_data = pd.read_json(tk_data, typ='serie')
        else:
            df_data = pd.read_json(tk_data, typ='frame')

        return df_data
    
    def get_all_close_data(self):
        try:
            url = f'{self.url_base}/data/time_series'
            datos_close = {}
            maestro_df = self.get_ticker_master()
            for idx, datos in maestro_df.iterrows():
                tck = datos.ticker
                series_data = self.get_close_data_tck(tck)
                print(tck, end = ' ')
                datos_close[tck] = series_data
            stock_master = pd.DataFrame(datos_close)
            return stock_master
        except:
            print('No fue posible obtener los datos de cierre')
    
    def get_algos(self):
        url = f'{self.url_base}/participants/algorithms'
        params = {'competi': self.competi,
                  'key': self.user_key
                  }
        response = requests.get(url, params)
        algos = response.json()
        if algos:
            algos_df = pd.DataFrame(algos)
            return algos_df
        
    def post_alloc(self, algo_tag, str_date, allocation):
        try:
            url = f'{self.url_base}/participants/allocation'
            url_auth = f'{url}?key={self.user_key}'
            params = {
                      'competi': self.competi,
                      'algo_tag': algo_tag,
                      'market': self.market,
                      'date': str_date,
                      'allocation': allocation
                      }
            response = requests.post(url_auth, data=json.dumps(params))
            print (response.json())
        except:
            print('No fue posible enviar los pesos')

    def get_allocs(self, algo_tag):
        try:
            url = f'{self.url_base}/participants/algo_allocations'
            params = {
                      'key': self.user_key,
                      'competi': self.competi,
                      'algo_tag': algo_tag,
                      'market': self.market,
                      }
            response = requests.get(url, params)
            response_json = response.json()
            df = pd.DataFrame()
            if response_json:
                df = allocs_to_frame(response_json)
            return df
        except:
            print('No fue posible obtener las alocaciones')
    
    def exec_backtest(self, algo_tag):
        url = f'{self.url_base}/participants/exec_algo' 
        url_auth = f'{url}?key={self.user_key}' 
        params = {
                  'competi': self.competi,
                  'algo_tag': algo_tag,
                  'market': self.market,
                  }
        response = requests.post(url_auth, data=json.dumps(params))
        if response.status_code == 200:
            exec_data = response.json()
            status = exec_data.get('status')
            res_data = exec_data.get('content')
            trades = None
            if res_data:
                result = pd.Series(res_data['result'])
                trades = pd.DataFrame(res_data['trades'])
            return result, trades
        else:
            exec_data = dict()
            print(response.text)
            
    def show_backtest(self, algo_tag):
        url = f'{self.url_base}/participants/algo_exec_results'
        params = {
            'key': self.user_key,
            'competi': self.competi,
            'algo_tag': algo_tag,
            'market': self.market,
                }
        response = requests.get(url, params)
        exec_data = response.json()
        status = exec_data.get('status')
        content = exec_data.get('content')
        result = pd.Series(content['result'])
        trades = pd.DataFrame(content['trades'])
        return result, trades
        
    def delete_allocs(self, algo_tag):
        try:
            url = f'{self.url_base}/participants/delete_allocations'
            url_auth = f'{url}?key={self.user_key}'
            params = {
                      'competi': self.competi,
                      'algo_tag': algo_tag,
                      'market': self.market,
                      }
            response = requests.post(url_auth, data=json.dumps(params))
            return response.text
        except:
            print('No fue posible borrar las alocaciones')