import os
import spotpy
import pandas as pd
import numpy as np
from daycentpy.models import single_setup
from spotpy.objectivefunctions import rmse
from spotpy.likelihoods import gaussianLikelihoodMeasErrorOut as GausianLike


def run_fast(
        wd, pars_df, rep, 
        dbname="DREAM_daycent", dbformat="csv", parallel='seq', obj_func=None):
    os.chdir(wd)
    obs_m = obs_masked()
    # spot_setup = spot_setup(GausianLike)
    spot_setup = single_setup(
        wd, obs_m, pars_df, parallel=parallel, obj_func=obj_func)
        # temp_dir=temp_dir
    # spot_setup = spot_setup(spotpy.objectivefunctions.rmse)
    # Select number of maximum allowed repetitions
    sampler = spotpy.algorithms.fast(
            spot_setup, dbname=dbname, 
            dbformat=dbformat, parallel=parallel
            )
    sampler.sample(rep)


def run_dream(
        wd, pars_df, rep, nChains=10, 
        dbname="DREAM_daycent", dbformat="csv", parallel='seq', obj_func=None):
    os.chdir(wd)
    obs_m = obs_masked()
    # spot_setup = single_setup(GausianLike)

    # Bayesian algorithms should be run with a likelihood function
    obj_func = spotpy.likelihoods.gaussianLikelihoodMeasErrorOut
    spot_setup = single_setup(
        wd, obs_m, pars_df, parallel=parallel, obj_func=obj_func)
    # Select seven chains and set the Gelman-Rubin convergence limit
    delta = 3
    convergence_limit = 1.2

    # Other possible settings to modify the DREAM algorithm, for details see Vrugt (2016)
    c = 0.1
    nCr = 3
    eps = 10e-6
    runs_after_convergence = 100
    acceptance_test_option = 6

    sampler = spotpy.algorithms.dream(
        spot_setup, dbname=dbname, dbformat=dbformat, parallel=parallel)
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
    if dbformat == 'ram':
        results = pd.DataFrame(sampler.getdata())
        results.to_csv(f"{dbname}.csv", index=False)
        #########################################################
        # Example plot to show the convergence #################
        results02 = spotpy.analyser.load_csv_results(f"{dbname}")
        spotpy.analyser.plot_gelman_rubin(results02, r_hat, fig_name="DREAM_r_hat.png")
        ########################################################
        
def run_sceua(wd, pars_df, rep, ngs=7, parallel='seq'):
    os.chdir(wd)
    obs_m = obs_masked()
    # spot_setup = spot_setup(GausianLike)
    spot_setup = single_setup(
        wd, obs_m, pars_df, parallel=parallel)
        # temp_dir=temp_dir
    # spot_setup = spot_setup(spotpy.objectivefunctions.rmse)

    # Select number of maximum allowed repetitions
    sampler = spotpy.algorithms.sceua(
        spot_setup, dbname="SCEUA_daycent", dbformat="csv", parallel=parallel)
    # Start the sampler, one can specify ngs, kstop, peps and pcento id desired
    sampler.sample(rep, ngs=ngs, kstop=3, peps=0.1, pcento=0.1)


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



def get_cali_date():
    data_run_file = "DayCentRUN.DAT"
    with open(data_run_file, "r") as f:
        data = [x.strip().split() for x in f]
    for l, i in enumerate(range(len(data))):
        if (len(data[i]) != 0) and ((data[i][0]).lower() == "calibration:"):
            cal_line = l
    cali_dates = data[cal_line][1].split('-')
    return int(cali_dates[0]), int(cali_dates[1])