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


class DCinit(object):
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

        # cwd = Path(os.getcwd())

        # p_dir = cwd.parent.absolute()
        # print(p_dir)
        # main_dir = os.path.join(p_dir, cali_dir)
        # # copy your model to main cali folder
        # if os.path.exists(main_dir):
        #     try:
        #         shutil.rmtree(main_dir, onerror=self._remove_readonly)
        #     except Exception as e:
        #         raise Exception("unable to remove existing worker dir:" + \
        #                         "{0}\n{1}".format(main_dir,str(e)))
        # else:
        #     try:
        #         # os.mkdir(main_dir)
        #         shutil.copytree(model_dir,main_dir)
        #         print("model dir copied to main ...")
        #     except Exception as e:
        #         raise Exception("unable to copy files from model dir: " + \
        #                         "{0} to main worker dir: {1}\n{2}".format(model_dir,main_dir,str(e)))
        # os.chdir(main_dir)
        # org_par_file = "daycent_pars.csv"
        # suffix = ' passed'
        # if os.path.exists(org_par_file):
        #     print("    We found DayCent parameter base file.")
        # else:
        #     shutil.copy2(os.path.join(database_path, org_par_file), os.path.join(main_dir, org_par_file))
        #     print(f"    '{org_par_file}' file copiped ..." + colored(suffix, 'green'))
        # print("    Open the file and select parameters you are goint to use ..., ")
        # print("    then save it as 'seleted_pars.csv'.")

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


class dc_cali_setup(object):
    def __init__(
        self, wd, observed_data, pars_df, parallel="seq", temp_dir=None
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

        self.curdir = os.getcwd()
        self.wd = wd
        self.observed_data = observed_data
        # wd = parm.path_TxtInout
        os.chdir(wd)
        dbfile = 'db_results.csv'
        if os.path.exists(os.path.join(self.wd, dbfile)):
            os.remove(os.path.join(self.wd, dbfile))

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
        self.temp_dir = temp_dir
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
        print('  fix pars updated ...')

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
        print('  site pars updated ...')

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
            print('The original site file "{}" has been backed up...'.format(site_file))
        else:
            print("The '{}' file already exists...".format(org_bak_file))
        return org_bak_file
    

    def backup_org_cult_file(self, cult_file):
        org_bak_file = cult_file + ".org_bak"
        if not os.path.exists(org_bak_file):
            shutil.copy(cult_file, org_bak_file)
            print('The original site file "{}" has been backed up...'.format(cult_file))
        else:
            print("The '{}' file already exists...".format(org_bak_file))
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
        print('  cult par and CLTEFF values updated ...')

    def update_dc_pars(self, parameters):
        print(f"this iteration's parameters:")
        print(parameters)
        dc_parms = self.pars_df
        dc_parms['val'] = parameters
        cpars = dc_parms.loc[:, 'val'].tolist()
        self.update_fix_pars(dc_parms)
        self.update_site_pars(dc_parms)
        self.update_soc_soms_vals(dc_parms)
        return cpars

        
                
    # # Simulation function must not return values besides for which evaluation values/observed data are available
    # def simulation(self, parameters):
    #     self.update_dc_parms(parameters)
    #     # model run
    #     with open("DayCentRUN.DAT", "r") as f:
    #         data = [x.strip().split() for x in f]
    #     print('')
    #     print('  Simulation start ...')
    #     for i in range(len(data)):
    #         if os.path.isfile(data[i][1]+".bin"):
    #             os.remove(data[i][1]+".bin")

    #         # os.system("start /wait cmd /c {command}")
    #         comline = 'DD17centEVI.exe -s {} -n {} -e {}'.format(data[i][1], data[i][1], data[i][3])
    #         # os.system("start cmd {}/k".format(comline))
    #         run_model = subprocess.Popen(comline, cwd=".", stdout=subprocess.DEVNULL)
    #         run_model.wait()
    #         comline2 = 'DD17list100.exe {} {} {}'.format(data[i][1], data[i][1], 'outvars.txt')
    #         # os.system("start cmd {}".format(comline2))
    #         extract_model = subprocess.Popen(comline2, cwd=".", stdout=subprocess.DEVNULL)
    #         extract_model.wait()
    #     print('')
    #     print('  Simulation complete ...')
    #     print('')
    #     print('  extracting simulation outputs ...')
    #     # get all sims
    #     sim_df = pd.DataFrame()
    #     for i in range(len(data)):
    #         outf = data[i][1]+".lis"
    #         df = pd.read_csv( outf, sep=r'\s+', skiprows=1)
    #         df_sel = df.loc[(df['time']>=1971.08) & (df['time']<=1994.00)]
    #         df_sel.index = pd.date_range(start='1/1/1971', periods=len(df_sel), freq='M')
    #         dfa = df_sel.loc[:, ['somsc']].resample('A').mean()
    #         dfa.index = dfa.index.year
    #         dfa.rename(columns = {'somsc':'somsc_'+data[i][1][8:]}, inplace = True)
    #         sim_df = pd.concat([sim_df, dfa], axis=1)
            
    #     # get all obds
    #     obd_f = "soc_obd.csv"
    #     obd_df = pd.read_csv(obd_f).set_index('Year')  
    #     obd_df.replace(-999, np.nan, inplace=True)

    #     # filter only for calibration
    #     tot_df = pd.DataFrame()
    #     for col in sim_df.columns:
    #         tt =  pd.concat([sim_df.loc[:, col], obd_df.loc[:, col]], axis=1).dropna(axis=0)
    #         tt.columns = ['sim', 'obd']
    #         tt['name'] = col
    #         tot_df = pd.concat([tot_df, tt], axis=0)

    #     sim_list = tot_df.loc[:, 'sim'].tolist()
    #     print('  extracting simulation outputs ... passed')
    #     return sim_list

    # get info from *.sch file
    def get_start_end_years(self, model_name):
        sch_file =  model_name + ".sch"
        with open(sch_file, "r") as f:
            data = [x.strip().split() for x in f]
        start_yr = int(data[0][0])
        end_yr = int(data[1][0])
        return start_yr, end_yr
    
    def get_cali_date(self):
        data_run_file = "DayCentRUN.DAT"
        with open(data_run_file, "r") as f:
            data = [x.strip().split() for x in f]
        for l, i in enumerate(range(len(data))):
            if (len(data[i]) != 0) and ((data[i][0]).lower() == "calibration:"):
                cal_line = l
        cali_dates = data[cal_line][1].split('-')
        return int(cali_dates[0]), int(cali_dates[1])


    # Simulation function must not return values besides for which evaluation values/observed data are available
    def simulation(self, parameters):
        if self.parallel == "seq":
            call = ""
        elif self.parallel == "mpi":
            # Running n parallel, care has to be taken when files are read or written
            # Therefor we check the ID of the current computer core
            call = str(int(os.environ["OMPI_COMM_WORLD_RANK"]) + 2)
            # And generate a new folder with all underlying files
            copy_tree(self.wd, self.wd + call)

        elif self.parallel == "mpc":
            # Running n parallel, care has to be taken when files are read or written
            # Therefor we check the ID of the current computer core
            call = str(os.getpid())
            # And generate a new folder with all underlying files
            # os.chdir(self.wd)
            copy_tree(self.wd, self.wd + call)
            
        else:
            raise "No call variable was assigned"
        # print(self.wd)
        os.chdir(self.wd + call)
        try:
            os.write(1, "text\n".encode())
            self.update_dc_pars(parameters)
            # cpars = self.update_dc_pars(parameters)
            # model run
            with open("DayCentRUN.DAT", "r") as f:
                data = [x.strip().split() for x in f]
            print('')
            print('  Simulation start ...')

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
            print('')
            print('  Simulation complete ...')
            print('')
            print('  extracting simulation outputs ...')
            
            
            # get all sims
            sim_df = pd.DataFrame()
            for i in range(mlines):
                # start_yr, end_yr = self.get_start_end_years(data[i][1])
                outf = data[i][1]+".lis"
                df = pd.read_csv( outf, sep=r'\s+', skiprows=1)
                cali_start, cali_end = self.get_cali_date()
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
            sim_list = tot_df.loc[:, 'sim'].tolist()
            print('  extracting simulation outputs ... passed')
        except Exception as e:
            raise Exception("Model has failed")
        os.chdir(self.curdir)
        # os.chdir("d:/Projects/Tools/DayCent-CUTE/tools")
        if self.parallel == "mpi" or self.parallel == "mpc":
            remove_tree(self.wd + call)

        # obj_val = self.objf(tot_df)
        # self.saving_results(obj_val, cpars, sim_list)
        # print(sim_list)
        return sim_list
    

    def evaluation(self):
        return self.observed_data

    def objf(self, tot_df):
        sims = tot_df.loc[:, 'sim'].tolist()
        obds = tot_df.loc[:, 'obd'].tolist()
        obj_val = spotpy.objectivefunctions.nashsutcliffe(
            obds, sims)
        return obj_val

    # if we want to minimize our function, we can select a negative objective function
    def objectivefunction(self, simulation, evaluation):

        print("simulation")
        print(len(simulation))
        print("evaluation")
        print(len(evaluation))

        objectivefunction = spotpy.objectivefunctions.abs_pbias(
            evaluation, simulation
        )
        return objectivefunction


    def saving_results(self, obj_val, cpars, csims):
        #create dummy file
        lockfile = 'db_results.locked'
        dbfile = 'db_results.csv'
        # while os.path.exists(os.path.join(self.wd, lockfile)):
        #     time.sleep(10)
        #     print('waiting ...')
        # else:
        #     with open(os.path.join(self.wd, lockfile), 'w') as f:
        #         f.write('temp ...')

        data = [obj_val] + cpars + csims
        if os.path.exists(os.path.join(self.wd, dbfile)):
            with open(os.path.join(self.wd, dbfile), 'a') as inf:
                # inf.writelines(data + '\n')
                inf.write(",".join(map(str, data)) + "\n")
        else: 
            with open(os.path.join(self.wd, dbfile), 'w') as inf:
                # inf.writelines(data + '\n')
                inf.write(",".join(map(str, data)) + "\n")
        # os.remove(os.path.join(self.wd, lockfile))

def run_dream(wd, pars_df, parallel, rep, ngs):
    os.chdir(wd)
    parallel = "mpc"
    obs_m = obs_masked()
    # spot_setup = spot_setup(GausianLike)
    spot_setup = dc_cali_setup(
        wd, obs_m, pars_df, parallel=parallel)
        # temp_dir=temp_dir
    # spot_setup = spot_setup(spotpy.objectivefunctions.rmse)

    # Select number of maximum allowed repetitions
    sampler = spotpy.algorithms.sceua(spot_setup, dbname="SCEUA_hymod", dbformat="csv", parallel='mpc')
    # Start the sampler, one can specify ngs, kstop, peps and pcento id desired
    sampler.sample(rep, ngs=ngs, kstop=3, peps=0.1, pcento=0.1)

    # Load the results gained with the sceua sampler, stored in SCEUA_hymod.csv
    # results = spotpy.analyser.load_csv_results("SCEUA_hymod")

def run_dream02(wd, pars_df, parallel, rep, ngs):
    os.chdir(wd)
    parallel = "mpc"
    obs_m = obs_masked()
    # spot_setup = spot_setup(GausianLike)
    spot_setup = dc_cali_setup(
        wd, obs_m, pars_df, parallel=parallel)
        # temp_dir=temp_dir
    # spot_setup = spot_setup(spotpy.objectivefunctions.rmse)

    # Select number of maximum allowed repetitions
    sampler = spotpy.algorithms.sceua(spot_setup, dbname="SCEUA_hymod", dbformat="csv", parallel='mpc')
    # Start the sampler, one can specify ngs, kstop, peps and pcento id desired
    sampler.sample(rep, ngs=ngs, kstop=3, peps=0.1, pcento=0.1)
    spotpy.database
    # Load the results gained with the sceua sampler, stored in SCEUA_hymod.csv
    # results = spotpy.analyser.load_csv_results("SCEUA_hymod")

def run_fast(wd, pars_df, parallel, rep):
    os.chdir(wd)
    parallel = "mpc"
    obs_m = obs_masked()
    # spot_setup = spot_setup(GausianLike)
    spot_setup = dc_cali_setup(
        wd, obs_m, pars_df, parallel=parallel)
        # temp_dir=temp_dir
    # spot_setup = spot_setup(spotpy.objectivefunctions.rmse)

    # Select number of maximum allowed repetitions
    sampler = spotpy.algorithms.fast(spot_setup, dbname="FAST_hymod", dbformat="csv", parallel='mpc')
    sampler.sample(rep)


def get_cali_date():
    data_run_file = "DayCentRUN.DAT"
    with open(data_run_file, "r") as f:
        data = [x.strip().split() for x in f]
    for l, i in enumerate(range(len(data))):
        if (len(data[i]) != 0) and ((data[i][0]).lower() == "calibration:"):
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
    # mlines indicate only lines for model info
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
        nam_ex = len(data[i][0]) + 1  # length of treatmen
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


def demo_cali(wd, params, rep, nChains):
    os.chdir(wd)
    parallel = "mpc"
    # df_fix = pd.read_csv('dc_fix.parms.csv')
    # df_site = pd.read_csv('dc_site.parms.csv')
    # param_defs = pd.concat([df_fix, df_site], axis=0)

    obs_m = obs_masked()
    # spot_setup = spot_setup(GausianLike)
    spot_setup = dc_cali_setup(
        wd, obs_m, params, parallel=parallel)
        # temp_dir=temp_dir

    # Select number of maximum repetitions
    rep = rep

    # Select seven chains and set the Gelman-Rubin convergence limit
    delta = 3
    nChains = nChains
    convergence_limit = 1.2

    # Other possible settings to modify the DREAM algorithm, for details see Vrugt (2016)
    c = 0.1
    nCr = 3
    eps = 10e-6
    runs_after_convergence = 2
    acceptance_test_option = 6

    sampler = spotpy.algorithms.dream(
        spot_setup, dbname="DREAM_dc_bias", dbformat="ram", parallel=parallel
    )
    r_hat = sampler.sample(
        rep,
        nChains,
        nCr,
        delta,
        c,
        eps,
        convergence_limit,
        runs_after_convergence,
        acceptance_test_option,
    )
    results = pd.DataFrame(sampler.getdata())
    results.to_csv('testest.csv')
    print(os.getcwd())


def demo_cali_sql(wd, params, rep, nChains):
    os.chdir(wd)
    parallel = "mpc"
    # df_fix = pd.read_csv('dc_fix.parms.csv')
    # df_site = pd.read_csv('dc_site.parms.csv')
    # param_defs = pd.concat([df_fix, df_site], axis=0)

    obs_m = obs_masked()
    # spot_setup = spot_setup(GausianLike)
    spot_setup = dc_cali_setup(
        wd, obs_m, params, parallel=parallel)
        # temp_dir=temp_dir

    # Select number of maximum repetitions
    rep = rep

    # Select seven chains and set the Gelman-Rubin convergence limit
    delta = 3
    nChains = nChains
    convergence_limit = 1.2

    # Other possible settings to modify the DREAM algorithm, for details see Vrugt (2016)
    c = 0.1
    nCr = 3
    eps = 10e-6
    runs_after_convergence = 2
    acceptance_test_option = 6

    sampler = spotpy.algorithms.dream(
        spot_setup, dbname="DREAM_dc_bias", dbformat="sql", parallel=parallel
    )
    r_hat = sampler.sample(
        rep,
        nChains,
        nCr,
        delta,
        c,
        eps,
        convergence_limit,
        runs_after_convergence,
        acceptance_test_option,
    )

