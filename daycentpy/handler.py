import os
import numpy as np
import pandas as pd
import spotpy
import subprocess
from distutils.dir_util import copy_tree, remove_tree
import shutil
from tqdm import tqdm
from termcolor import colored 
import time
from pathlib import Path
from tqdm import trange


database_path = os.path.join(
                    os.path.dirname(os.path.abspath( __file__ )),
                    'database')
exes_path = os.path.join(
                    os.path.dirname(os.path.abspath( __file__ )),
                    'exes')

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
    if len(cali_dates)==1:
        return int(cali_dates[0]), int(cali_dates[0])
    else:
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
    print('  **** Initial run begins ... ****')

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


class MultiInit(object):
    def __init__(self, proj_dir, model_dir):
        self.proj_dir = proj_dir
        if not os.path.exists(proj_dir):
            print("'{}' directory doesn't exist and created in the path '{}' ...")
            
            os.mkdir(self.proj_dir)
        os.chdir(self.proj_dir)
        self.main_dir = os.path.join(self.proj_dir,"multi_main")
        if os.path.exists(self.main_dir):
            try:
                shutil.rmtree(self.main_dir, onerror=_remove_readonly)#, onerror=del_rw)
            except Exception as e:
                raise Exception("unable to remove existing worker dir:" + \
                                "{0}\n{1}".format(self.main_dir,str(e)))
            try:
                shutil.copytree(model_dir, self.main_dir)
            except Exception as e:
                raise Exception("unable to copy files from model dir: " + \
                                "{0} to new main dir: {1}\n{2}".format(model_dir, self.main_dir,str(e)))                  
        else:
            try:
                shutil.copytree(model_dir, self.main_dir)
            except Exception as e:
                raise Exception("unable to copy files from model dir: " + \
                                "{0} to new main dir: {1}\n{2}".format(model_dir, self.main_dir,str(e)))        
        org_par_file = "daycent_pars.csv"
        suffix = ' passed'
        if os.path.exists(org_par_file):
            print("    We found DayCent parameter base file.")
        else:
            shutil.copy2(os.path.join(database_path, org_par_file), os.path.join(proj_dir, org_par_file))
            print(f"    '{org_par_file}' file copiped ..." + colored(suffix, 'green'))
        print("    Open the file and select parameters you are goint to use ..., ")
        print("    then save it as 'seleted_pars.csv'.")

    def k_fold_setup(self, k=5):
        site_num = len(os.listdir(self.main_dir))
        np.random.choice([0, 1], size=(site_num,), p=[1./k, 4./k])




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

    def get_sites(self):
        return os.listdir(self.main_dir)
    

    def init_run(self):
        print('**** Initial simulation begins ... ****')
        site_list = self.get_sites()
        tprogress = trange(len(site_list), desc='model: ', leave=True)
        for tp in tprogress:
            s = site_list[tp]
            os.chdir(os.path.join(self.main_dir, s))
            exe01_file = "DDcentEVI.exe"
            exe02_file = "DDlist100.exe"
            suffix = ' passed'
            if not os.path.exists(exe01_file):
                shutil.copy2(os.path.join(exes_path, exe01_file), os.path.join(self.main_dir, s, exe01_file))
                shutil.copy2(os.path.join(exes_path, exe02_file), os.path.join(self.main_dir, s, exe02_file))
            with open("DayCentRUN.DAT", "r") as f:
                data = [x.strip().split() for x in f]
            tprogress.set_description(f"{s} ... run")
            # print(f" {s} run ...")
            mlines = []
            for l, i in enumerate(range(len(data))):
                if len(data[i]) == 0:
                    mlines.append(l)
            # mlines indicate only lines for model info
            for i in range(mlines[0]):
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
            tprogress.set_description(f"{s} ... passed")
            tprogress.refresh()
            # print(f" ...{s} run ... done")
            self.read_sim_obd(data, mlines, s)
        print('**** Initial simulation ends ... ****')
        os.chdir(self.proj_dir)

    def read_sim_obd(self, data, mlines, s):
        sim_df = pd.DataFrame()
        for i in range(mlines[0]):
            # start_yr, end_yr = self.get_start_end_years(data[i][1])
            outf = data[i][1]+".lis"
            df = pd.read_csv( outf, sep=r'\s+', skiprows=1)
            cali_start, cali_end = get_cali_date()
            # daycent time shift
            cali_sshift = cali_start + .08
            cali_eshift = cali_end + 1.00
            df_sel = df.loc[(df['time']>=cali_sshift) & (df['time']<=cali_eshift)]
            df_sel.index = pd.date_range(start='1/1/{}'.format(cali_start), periods=len(df_sel), freq='M')
            dfa = df_sel.loc[:, ['somsc']].resample('A').mean()
            dfa['site_name'] = s
            dfa['treat_name'] = data[i][1]
            dfa['time'] = dfa.index.year
            dfa.rename(columns = {'somsc':'somsc_sim'}, inplace = True)
            sim_df = pd.concat([sim_df, dfa], axis=0)
        # get all obds
        obd_f = "soc_obd.csv"
        obd_df = pd.read_csv(obd_f) 
        obd_df.replace(-999, np.nan, inplace=True)
        for i in range(len(sim_df)):
            tn = sim_df.treat_name[i]
            tm = sim_df.time[i]
            if obd_df[tn].loc[obd_df['Year']==tm].size > 0:
                sim_df.loc[(sim_df["treat_name"]==tn) & (sim_df["time"]==tm), 'obd'] = obd_df[tn].loc[obd_df['Year']==tm].values[0] 
        sim_df = sim_df.dropna(axis=0)
        sim_df.to_csv("sim_obd.csv", index=False, float_format='%.3f')

    def all_sim_obd(self):
        all_df = pd.DataFrame()
        for i in self.get_sites():
            os.chdir(os.path.join(self.main_dir, i))
            df = pd.read_csv('sim_obd.csv')
            all_df = pd.concat([all_df, df], axis=0)
        os.chdir(self.proj_dir)
        return all_df    
