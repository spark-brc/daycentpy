import os
import numpy as np
import pandas as pd
import spotpy
from distutils.dir_util import copy_tree, remove_tree
import subprocess
import shutil
from spotpy.objectivefunctions import rmse
from daycentpy.handler import get_cali_date

class multi_setup(object):
    def __init__(
        self, main_dir, observed_data, pars_df, parallel="seq", obj_func=None
        ):
        """_summary_

        Args:
            swatmd (_type_): _description_
            observed_data (_type_): _description_
            pars_df (_type_): params will be used
            parallel (str, optional): _description_. Defaults to "seq".
        """
        # proj_dir = os.getcwd()
        # main_dir = os.path.join(proj_dir,"main")
        self.obj_func = obj_func
        self.curdir = os.getcwd()
        self.main_dir = main_dir
        self.observed_data = observed_data
        # main_dir = parm.path_TxtInout
        os.chdir(main_dir)

        # parameters
        # pars_df = self.read_dc_pars()    
        self.params = [] # parameters used
        for i in range(len(pars_df)):
            self.params.append(
                    spotpy.parameter.Uniform(
                    name=pars_df.iloc[i, 0],
                    low=pars_df.iloc[i, 3],
                    high=pars_df.iloc[i, 4],
                    optguess=np.mean(
                        [float(pars_df.iloc[i, 3]), float(pars_df.iloc[i, 4])])))
        
        self.pars_df = pars_df
        self.parallel = parallel
        if self.parallel == "seq":
            pass
        if self.parallel == "mpi":
            from mpi4py import MPI
            comm = MPI.COMM_WORLD
            self.mpi_size = comm.Get_size()
            self.mpi_rank = comm.Get_rank()

    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def update_fix_pars(self, updated_df):
        fix_pars_df = updated_df.loc[updated_df['category']=='fix']
        with open('fix.100', "r") as f:
            updated = []
            for line in f.readlines():
                parnam = line.split()[1].strip().replace("'", "").replace(",", "_")
                if (parnam in fix_pars_df.loc[:, "name"].tolist()):
                    new_val = fix_pars_df.loc[fix_pars_df['name'] == parnam, "val"].tolist()[0]
                    new_line = f"{new_val:<14.4f}{line.split()[1].strip()}\n"
                    updated.append(new_line)
                else:
                    updated.append(line)
        with open('fix.100', "w") as wf:
            wf.writelines(updated)
        # print('  fix pars updated ...')

    def update_site_pars(self, updated_df):
        site_pars_df = updated_df.loc[updated_df['category']=='site']
        with open('sitepar.in', "r") as f:
            updated = []
            for line in f.readlines():
                parnam = line.split()[2].strip()
                if (parnam in site_pars_df.loc[:, "name"].tolist()):
                    new_val = site_pars_df.loc[site_pars_df['name'] == parnam, "val"].tolist()[0]
                    new_line = f"{new_val:<11f}{line.split()[1].strip()} {line.split()[2].strip()}\n"
                    updated.append(new_line)
                else:
                    updated.append(line)
        with open('sitepar.in', "w") as wf:
            wf.writelines(updated)
        # print('  site pars updated ...')

    def find_site_file(self):
        with open("DayCentRUN.DAT", "r") as f:
            data = [x.strip().split() for x in f]        
        for l, i in enumerate(range(len(data))):
            if len(data[i]) == 0:
                mlines = l
        return mlines

    def backup_site_files(self, site_file):
        org_bak_file = site_file + ".org_bak"
        if not os.path.exists(org_bak_file):
            shutil.copy(site_file, org_bak_file)
            # print('The original site file "{}" has been backed up...'.format(site_file))
        # else:
        #     print("The '{}' file already exists...".format(org_bak_file))
        return org_bak_file
    
    def backup_org_cult_file(self, cult_file):
        org_bak_file = cult_file + ".org_bak"
        if not os.path.exists(org_bak_file):
            shutil.copy(cult_file, org_bak_file)
            print('The original site file "{}" has been backed up...'.format(cult_file))
        # else:
        #     print("The '{}' file already exists...".format(org_bak_file))
        return org_bak_file
    
    def update_soc_soms_vals(self, updated_df):
        fbm_val = (updated_df.loc[updated_df['name']=='FBM', 'val']).values[0]
        fhp_val = (updated_df.loc[updated_df['name']=='FHP', 'val']).values[0]
        with open("DayCentRUN.DAT", "r") as f:
            data = [x.strip().split() for x in f]
        for i in range(self.find_site_file()):
            # find sch file
            sch_file = data[i][1] + ".sch"
            with open(sch_file, "r") as f:
                sch_data = [x.strip().split() for x in f]
            site_file = sch_data[2][0]
            org_bak_file = self.backup_site_files(site_file)
            # get soc_soms_vals
            with open(org_bak_file, 'r') as sfile:
                sdata = [x.strip().split() for x in sfile]
            idxs_somcs = {}
            for l, i in enumerate(range(len(sdata))):
                if sdata[i][1] == 'SOM1CI(2,1)':
                    idxs_somcs['SOM1CI(2,1)'] = float(sdata[i][0])
                if sdata[i][1] == 'SOM2CI(2,1)':
                    idxs_somcs['SOM2CI(2,1)'] = float(sdata[i][0])
                if sdata[i][1] == 'SOM3CI(1)':
                    idxs_somcs['SOM3CI(1)'] = float(sdata[i][0])    
            soc_val = idxs_somcs['SOM1CI(2,1)'] + idxs_somcs['SOM2CI(2,1)'] + idxs_somcs['SOM3CI(1)']
            new_som1ci = fbm_val * soc_val
            new_som3ci = fhp_val * (soc_val - idxs_somcs['SOM1CI(2,1)'])
            new_som2cl = soc_val - idxs_somcs['SOM1CI(2,1)'] - idxs_somcs['SOM3CI(1)']
            # update somc vals
            idxs_somcs['SOM1CI(2,1)'] = new_som1ci
            idxs_somcs['SOM2CI(2,1)'] = new_som2cl
            idxs_somcs['SOM3CI(1)'] = new_som3ci

            # update soc_soms_vals
            with open(site_file, 'r') as sfile:
                updated_lines = []
                for line in sfile.readlines():
                    parnam = line.split()[1].strip()
                    if parnam in idxs_somcs.keys():
                        new_line = f"{idxs_somcs[parnam]:<17.4f} {parnam}\n"
                        updated_lines.append(new_line)
                    else:
                        updated_lines.append(line)
            with open(site_file, 'w') as wsfile:
                wsfile.writelines(updated_lines)
        print('  FBM and FHP pars, and somc values updated ...')

    def update_cult_pars(self, updated_df):
        teff_val = (updated_df.loc[updated_df['name']=='Till_Eff', 'val']).values[0]
        cult_file = "cult.100"
        org_bak_file = self.backup_org_cult_file(cult_file)
        tillages = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K"]
        till_adjust = [0.0144, 0.1156, 0.1878, 0.2678, 0.3167, 0.3911, 0.4733, 0.5622, 0.6300, 0.9711, 1.0]
        till_dic = dict(zip(tillages, till_adjust))
        # update soc_soms_vals
        # find the line 
        with open(org_bak_file, 'r') as cult_org:
            data = cult_org.readlines()
        for tk in till_dic.keys():
            for i in range(len(data)):
                if tk == data[i].split()[0]:
                    culteff = round(1 + (teff_val-1) * till_dic[tk], 4)
                    data[i+8] = f"{culteff:<18.4f}{data[i+8].split()[1]}\n"
                    data[i+9] = f"{culteff:<18.4f}{data[i+9].split()[1]}\n"
                    data[i+11] = f"{culteff:<18.4f}{data[i+11].split()[1]}\n"
        with open(cult_file, 'w') as wcfile:
            wcfile.writelines(data)
        # print('  cult par and CLTEFF values updated ...')

    def update_dc_pars(self, parameters):
        print(f"this iteration's parameters:")
        print(parameters)
        dc_parms = self.pars_df
        dc_parms['val'] = parameters
        self.update_fix_pars(dc_parms)
        self.update_site_pars(dc_parms)
        self.update_soc_soms_vals(dc_parms)

    # get info from *.sch file
    def get_start_end_years(self, model_name):
        sch_file =  model_name + ".sch"
        with open(sch_file, "r") as f:
            data = [x.strip().split() for x in f]
        start_yr = int(data[0][0])
        end_yr = int(data[1][0])
        return start_yr, end_yr
    
    # def get_cali_date(self):
    #     data_run_file = "DayCentRUN.DAT"
    #     with open(data_run_file, "r") as f:
    #         data = [x.strip().split() for x in f]
    #     for l, i in enumerate(range(len(data))):
    #         if (len(data[i]) != 0) and ((data[i][0]).lower() == "obs:"):
    #             cal_line = l
    #     cali_dates = data[cal_line][1].split('-')
    #     if len(cali_dates)==1:
    #         return int(cali_dates[0]), int(cali_dates[0])
    #     else:
    #         return int(cali_dates[0]), int(cali_dates[1])


    def get_sites(self):
        return os.listdir(self.main_dir)


    # Simulation function must not return values besides for which evaluation values/observed data are available
    def simulation(self, parameters):
        if self.parallel == "seq":
            call = ""
        elif self.parallel == "mpi":
            # Running n parallel, care has to be taken when files are read or written
            # Therefor we check the ID of the current computer core
            call = str(int(os.environ["OMPI_COMM_WORLD_RANK"]) + 2)
            # And generate a new folder with all underlying files
            copy_tree(self.main_dir, self.main_dir + call)

        elif self.parallel == "mpc":
            # Running n parallel, care has to be taken when files are read or written
            # Therefor we check the ID of the current computer core
            call = str(os.getpid())
            # And generate a new folder with all underlying files
            # os.chdir(self.wd)
            copy_tree(self.main_dir, self.main_dir + call)
            
        else:
            raise "No call variable was assigned"
        # print(self.wd)
        self.main_dir_call =self.main_dir + call
        os.chdir(self.main_dir_call)
        try:
            site_list = self.get_sites()
            for st in site_list:
                os.chdir(os.path.join(self.main_dir_call, st))
                self.update_dc_pars(parameters)
           
                # model run
                with open("DayCentRUN.DAT", "r") as f:
                    data = [x.strip().split() for x in f]
                # print('')
                # print('  Simulation start ...')
                mlines = []
                for l, i in enumerate(range(len(data))):
                    if len(data[i]) == 0:
                        mlines.append(l)
                # mlines indicate only lines for model info
                mlines = mlines[0]
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
                self.read_sim_obd(data, mlines, st)
            all_df = self.all_sim_obd(self.main_dir_call)
        except Exception as e:
            raise Exception("Model has failed")
        os.chdir(self.curdir)
        # os.chdir("d:/Projects/Tools/DayCent-CUTE/tools")
        if self.parallel == "mpi" or self.parallel == "mpc":
            remove_tree(self.main_dir + call)
        return all_df['somsc_sim'].tolist()


    def read_sim_obd(self, data, mlines, st):
        sim_df = pd.DataFrame()
        for i in range(mlines):
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
            dfa['site_name'] = st
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

    def all_sim_obd(self, main_dir_call):
        self.main_dir_call = main_dir_call
        all_df = pd.DataFrame()
        for i in self.get_sites():
            os.chdir(os.path.join(self.main_dir_call, i))
            df = pd.read_csv('sim_obd.csv')
            all_df = pd.concat([all_df, df], axis=0)
        os.chdir(self.curdir)
        return all_df    


    def evaluation(self):
        return self.observed_data

    # if we want to minimize our function, we can select a negative objective function
    def objectivefunction(self, simulation, evaluation):
        if not self.obj_func:
            like = rmse(evaluation, simulation)
        else:
            like = self.obj_func(evaluation, simulation)
        return like



def cov_obs_obd(obs_dir, md_dir, site_name):
    os.chdir(obs_dir)
    soc_df = pd.read_csv(f'soc_{site_name}.csv')
    soc_columns = soc_df.columns[1:].tolist()
    soc_df = soc_df.rename(columns={'Yr':'Year'})
    for i in soc_columns:
        soc_df = soc_df.rename(columns={i: f"{site_name}_{i}"})
    os.chdir(os.path.join(md_dir, site_name))
    soc_df.to_csv('soc_obd.csv', index=False)