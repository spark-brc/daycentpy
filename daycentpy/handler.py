import os
import numpy as np
import pandas as pd
import spotpy
import subprocess
from distutils.dir_util import copy_tree, remove_tree
import shutil
from tqdm import tqdm
# from modules.tqdm import tqdm
from termcolor import colored 
import time
from pathlib import Path


database_path = os.path.join(
                    os.path.dirname(os.path.abspath( __file__ )),
                    'database')

cali_dir = "main"
multi_cali_dir = "multi_main"


class SingleInit(object):
    def __init__(self, proj_dir, model_dir):

        if not os.path.exists(proj_dir):
            print("'{}' directory doesn't exist and created in the path '{}' ...")
            os.mkdir(proj_dir)
        os.chdir(proj_dir)
        main_dir = os.path.join(proj_dir,"main")

        if os.path.exists(main_dir):
            try:
                shutil.rmtree(main_dir, onerror=_remove_readonly)#, onerror=del_rw)
            except Exception as e:
                raise Exception("unable to remove existing worker dir:" + \
                                "{0}\n{1}".format(main_dir,str(e)))
            try:
                shutil.copytree(model_dir, main_dir)
            except Exception as e:
                raise Exception("unable to copy files from model dir: " + \
                                "{0} to new main dir: {1}\n{2}".format(model_dir, main_dir,str(e)))                  
        else:
            try:
                shutil.copytree(model_dir, main_dir)
            except Exception as e:
                raise Exception("unable to copy files from model dir: " + \
                                "{0} to new main dir: {1}\n{2}".format(model_dir, main_dir,str(e)))        
        org_par_file = "daycent_pars.csv"
        suffix = ' passed'
        if os.path.exists(org_par_file):
            print("    We found DayCent parameter base file.")
        else:
            shutil.copy2(os.path.join(database_path, org_par_file), os.path.join(proj_dir, org_par_file))
            print(f"    '{org_par_file}' file copiped ..." + colored(suffix, 'green'))
        print("    Open the file and select parameters you are goint to use ..., ")
        print("    then save it as 'seleted_pars.csv'.")

    def _remove_readonly(self, func, path, excinfo):
        """remove readonly dirs, apparently only a windows issue
        add to all rmtree calls: shutil.rmtree(**,onerror=remove_readonly), wk"""
        os.chmod(path, 128)  # stat.S_IWRITE==128==normal
        func(path)

    def read_sel_dc_pars(self):
        df = pd.read_csv('selected_pars.csv')
        self.sel_df = df.loc[df['select']==1]
        print(f"You have selected a total of {len(self.sel_df):d} parameters.")
        return self.sel_df


def _remove_readonly(func, path, excinfo):
    """remove readonly dirs, apparently only a windows issue
    add to all rmtree calls: shutil.rmtree(**,onerror=remove_readonly), wk"""
    os.chmod(path, 128)  # stat.S_IWRITE==128==normal
    func(path)


def get_cali_date():
    data_run_file = "DayCentRUN.DAT"
    with open(data_run_file, "r") as f:
        data = [x.strip().split() for x in f]
    for l, i in enumerate(range(len(data))):
        if (len(data[i]) != 0) and ((data[i][0]).lower() == "obs:"):
            cal_line = l
    cali_dates = data[cal_line][1].split('-')
    return int(cali_dates[0]), int(cali_dates[1])


def obs_masked():
    cali_start, cali_end = get_cali_date()
    # model run
    with open("DayCentRUN.DAT", "r") as f:
        data = [x.strip().split() for x in f]
    sim_df = pd.DataFrame()

    for l, i in enumerate(range(len(data))):
        if len(data[i]) == 0:
            mlines = l
    # mlines indicate only lines including model info
    for i in range(mlines):
        outf = (data[i][1]+".lis").lower()
        df = pd.read_csv( outf, sep=r'\s+', skiprows=1)
        # daycent time shift
        cali_sshift = cali_start + .08
        cali_eshift = cali_end + 1.00
        df_sel = df.loc[(df['time']>=cali_sshift) & (df['time']<=cali_eshift)]
        df_sel.index = pd.date_range(start='1/1/{}'.format(cali_start), periods=len(df_sel), freq='M')
        dfa = df_sel.loc[:, ['somsc']].resample('A').mean()
        dfa.index = dfa.index.year
        nam_ex = len(data[i][0]) + 1  # length of treatment
        dfa.rename(columns = {'somsc':'somsc_'+data[i][1][nam_ex:]}, inplace = True)
        sim_df = pd.concat([sim_df, dfa], axis=1)

    # get all obds
    obd_f = "soc_obd.csv"
    obd_df = pd.read_csv(obd_f).set_index('Year')  
    obd_df.replace(-999, np.nan, inplace=True)

    # filter only for calibration
    tot_df = pd.DataFrame()
    for col in sim_df.columns:
        tt =  pd.concat([sim_df.loc[:, col], obd_df.loc[:, col]], axis=1).dropna(axis=0)
        tt.columns = ['sim', 'obd']
        tt['name'] = col
        tot_df = pd.concat([tot_df, tt], axis=0)
    obd_list = tot_df.loc[:, 'obd'].tolist()
    return obd_list


def init_run():
    with open("DayCentRUN.DAT", "r") as f:
        data = [x.strip().split() for x in f]
    print('')
    print('  **** Initial simulation begins ... ****')

    for l, i in enumerate(range(len(data))):
        if len(data[i]) == 0:
            mlines = l
    # mlines indicate only lines for model info
    for i in range(mlines):
        if os.path.isfile(data[i][1]+".bin"):
            os.remove(data[i][1]+".bin")
        if len(data[i]) > 2:
            comline = 'DDcentEVI.exe -s {} -n {} -e {}'.format(data[i][1], data[i][1], data[i][3])
        else:
            comline = 'DDcentEVI.exe -s {} -n {}'.format(data[i][1], data[i][1])
        run_model = subprocess.Popen(comline, cwd=".", stdout=subprocess.DEVNULL)
    #     run_model = subprocess.Popen(comline, cwd=".")
        run_model.wait()
        comline2 = 'DDlist100.exe {} {} {}'.format(data[i][1], data[i][1], 'outvars.txt')
        # os.system("start cmd {}".format(comline2))
        extract_model = subprocess.Popen(comline2, cwd=".", stdout=subprocess.DEVNULL)
        extract_model.wait()
        print(f"   {data[i][1]} simulation complete ...")
        print(f"   {data[i][1]} extracting simulation outputs ...")
    print('  **** Initial simulation ends ... ****')


