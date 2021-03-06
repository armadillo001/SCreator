import importlib
import requests
import json
import numpy as np
import pandas as pd
import os
import time

class stream:


    def __init__(self, logging, credential, now_time, path_indicator_state):
        self.logging = logging
        self.session_cookie = credential
        self.create_time = now_time
        self.indicator = ''

        self.name = ""
        self.description = ""
        self.dateStart = ""
        self.target = ""
        self.model_type = "indicator"

        self.authors = []
        self.pctgs = []

        self.path_indicator_state = path_indicator_state
        self.pd_indicator_record = pd.read_csv(self.path_indicator_state, index_col=0)

        self.flag_loader_ready = 1
        self.flag_init = 1
        self.flag_ongoing = 1

    def load_config(self, config):
        """
        Load from configuration and save to the stream class
        :param config: configuration file
        :return:
        """
        try:
            self.name = config.name
            self.description = config['description']
            self.dateStart = config['dateStart']
            if 'model_type' in config:
                self.model_type = config['model_type'] # 'stoploss'
            self.target = config['target']
            self.authors = config['authors']
            self.pctgs = config['pctgs']
            self.range = config['range']
            self.logging.info('Loading configurations of data stream %s' % (self.name))
        except:
            self.logging.error('Loading configurations failed!' % (self.name))

    def process(self):
        """
        Load and process the data stream based on the operations defined in loader/
        :return:
        """
        path_loader = 'loader.' + self.name
        try:
            loader = importlib.import_module(path_loader)
            self.logging.info('Downloading...')
            arr_loaded = loader.fun_load_data(self.dateStart)
            self.logging.info('Computing...')
            self.arr_computed = loader.fun_compute_data(arr_loaded)
            self.arr_computed.index.name = 'Date'
            if not pd.api.types.is_numeric_dtype(self.arr_computed): # check whether it is a pd.series
                self.logging.error('Loader format error, please check whether the output of data loader is a time series' % (path_loader))
                self.flag_loader_ready = 0
            self.flag_loader_ready = 1
            self.logging.info('Loaded and computed the data stream: %s' % (self.name))
        except:
            self.logging.error('Failed to process %s, please check whether the loader is ready' % (path_loader))
            self.flag_loader_ready = 0


    def fun_save_hist(self):
        """
        Load and save the historic data file
        :return:
        """
        self.path_histfile = os.path.join('data', "init_with", self.name + '.csv')
        self.flag_init = not np.sum(self.pd_indicator_record.ModelName.str.fullmatch(self.name).values)>=1
        if self.flag_init==True:
            try:
                self.arr_data_hist = self.arr_computed[:-1]
                self.arr_data_hist.to_csv(self.path_histfile)
            except:
                self.logging.error('Failed to save history file %s' % (self.path_histfile))


    def create_indicator(self):
        """
        Upload the data stream onto the S-creator data platform
        :return:
        """
        try:
            if self.flag_init==True:
                date_create = str(self.arr_data_hist.index[-1]).split(' ')[0]
                my_file = open(self.path_histfile, 'r')
                pd_temp = pd.read_csv(self.path_histfile) # Try to read it
                history_file_str = my_file.read().strip()
                url = "https://us-central1-modelcreator-cdd8f.cloudfunctions.net/functions/create_model_api"
                querystring = {
                    "session_cookie": self.session_cookie,
                    "authors[]": self.authors.split(','),
                    "pctgs[]": self.pctgs.split(','),
                    "model_name": self.name,
                    "model_description": self.description,
                    "model_type": self.model_type ,
                    "history_file": history_file_str,
                    "stocks": self.target,
                    "range": self.range  # put in (0 - 4) for (na, up to tmr, up to 1 week, up to 2 weeks, up to a month)
                }
                headers = {
                    'cache-control': "no-cache",
                    'Postman-Token': "3f5179b9-d4c2-4a08-9334-046efee45f25",
                    'Content-Type': "application/json"
                }
                response = requests.request("POST", url, headers=headers, data=json.dumps(querystring))
                modelID = response.text
                if response.status_code==200:
                    df_line = [[self.name, modelID, date_create, self.create_time , 1]]
                    df = pd.DataFrame(df_line, columns=['ModelName', 'ModelID', 'LastUpdateLocalTime', 'LastUpdateModelTime', 'CreateFlag'])
                    self.pd_indicator_record = self.pd_indicator_record.append(df, ignore_index=True)
                    self.pd_indicator_record.to_csv(self.path_indicator_state)
                    self.flag_init = False
                    self.logging.info('Create data stream Success! We uploaded %s to the server' % self.path_histfile)
                else:
                    self.logging.error('Create data stream failed! We cannot upload %s to the server' % self.path_histfile)
                    self.logging.error('Reason: %s', response.text)
        except:
            self.logging.error('Failed to create datastream %s' % (self.path_currentfile))


    def fun_save_ongoing(self):
        """
        Load and save the on-going data stream
        :return:
        """

        self.path_currentfile = os.path.join('data', 'on_going', self.name + '.csv')
        self.pd_indicator_record_result = pd.read_csv(self.path_indicator_state, index_col=0)
        time_model_last_updated = self.pd_indicator_record[self.pd_indicator_record['ModelName']==self.name].LastUpdateLocalTime.iloc[-1]
        self.arr_computed.index = self.arr_computed.index.strftime("%Y-%m-%d")
        if time_model_last_updated in self.arr_computed.index.to_list():
            idx_date_last_in_data = self.arr_computed.index.to_list().index(time_model_last_updated)
        else:
            for idx0,date_now in enumerate(self.arr_computed.index.to_list()):
                if date_now>=time_model_last_updated:
                    idx_date_last_in_data = idx0 -1
        try:
            if idx_date_last_in_data<(len(self.arr_computed)-1):
                self.arr_data_last = pd.DataFrame.from_dict({'Date': self.arr_computed.index[idx_date_last_in_data+1:].to_list(), 'signal': self.arr_computed.values[idx_date_last_in_data+1:].ravel().tolist()})
                self.arr_data_last.to_csv(self.path_currentfile, index=False, header=False)
                pd_temp = pd.read_csv(self.path_currentfile) # Try to read it
            else:
                self.logging.error('Indicator is up-to-date, does not update file %s' % (self.path_currentfile))
                self.flag_ongoing = 0
        except:
            self.logging.error('Failed to save update file %s' % (self.path_currentfile))
            self.flag_ongoing = 0


    def update_indicator(self):
        """
        Update the on-going data stream to the S-creator platform
        :return:
        """
        modelID = self.pd_indicator_record[self.pd_indicator_record['ModelName']==self.name].ModelID.unique().tolist()[0]

        if self.flag_ongoing!=0:
            url = "https://us-central1-modelcreator-cdd8f.cloudfunctions.net/functions/upload_api"
            my_file = open(self.path_currentfile, 'r')
            file_data = my_file.read().strip()
            date_create = file_data.split('\n')[-1].split(' ')[0].split(',')[0] # Use the last date
            payload = {
                "model_id": modelID,
                "file_data": file_data,
                "session_cookie": self.session_cookie
            }
            headers = {
                'Content-Type': "application/json",
                'cache-control': "no-cache"
            }
            response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
            if response.status_code==200:
                self.logging.info('Update status Success! We uploaded %s to the server' % self.path_currentfile)
                df_line = [[self.name, modelID, date_create, self.create_time, 0]]
                df = pd.DataFrame(df_line, columns=['ModelName', 'ModelID', 'LastUpdateLocalTime', 'LastUpdateModelTime', 'CreateFlag'])
                self.pd_indicator_record = self.pd_indicator_record.append(df, ignore_index=True)
                self.pd_indicator_record.to_csv(self.path_indicator_state)
            else:
                self.logging.error('Update failed, we did not update %s to the server' % self.path_currentfile)
                self.logging.error('Reason: %s', response.text)
        else:
            self.logging.error('Update not executed, we did not update %s to the server' % self.path_currentfile)

