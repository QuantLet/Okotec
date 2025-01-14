#!/usr/local/bin/python3
"""
Clustering Analysis using E-M algorithm
"""
import matplotlib as mpl
from Code.PreAnalyzing.EM_Algo import EM_Algo_1D

mpl.use("TKAgg")
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy as sc
import os
import sklearn.preprocessing as sp
import itertools
import statsmodels.tsa.api as smt
from Code.NonLinear_ForecastModels.LSTM_Params import res_dir, fastec_dir

def em_clustering_forecast():
    src = pd.read_csv('data/last_anonym_2017_vartime.csv', sep=';', index_col=0, parse_dates=True)
    outdata_path = ('Output/Data/')
    outplot_path = ('Output/plot/')
    print(outdata_path)
    # Drop out the dates that has continuously same value, 70865.614814...
    src_new = src[~ ((src['l'].values < 70865.615) & (src['l'].values > 70865.614))]

    # ============test
    # src_new['l'].plot()
    #
    # test = src_new[(src_new['l'].values < 70865.615) & (src_new['l'].values > 70865.614)]
    #
    # src_new['l'].value_counts()
    # src['l'].value_counts()
    # ============end test

    # hf_load = load_curve[(load_curve > 70865) & (load_curve < 70866)]


    # The exogenous variables can be separated into 2 groups
    group_1 = src_new.columns[1:19]
    group_2 = src_new.columns[19:44]
    group_3 = src_new.columns[44:]

    # schedule_group_1 = src_new.loc[:, group_1].values.reshape(1,-1).tolist()[0]
    schedule_group_1 = src_new.loc[:, group_1].sum(axis=1).values.reshape(1, -1).tolist()[0]
    # schedule_group_1_values = [ele for ele in schedule_group_1 if ele !=0]
    # print(len(schedule_group_1_values))
    # plt.hist(schedule_group_1_values,bins=50)

    # schedule_group_2 = src.loc[:, group_2].values.reshape(1,-1).tolist()[0]
    schedule_group_2 = src_new.loc[:, group_2].sum(axis=1).values.reshape(1, -1).tolist()[0]
    # schedule_group_2_values = [ele for ele in schedule_group_2 if ele !=0]
    # print(len(schedule_group_2_values))
    # plt.hist(schedule_group_2_values,bins=100)

    # schedule_group_3 = src.loc[:, group_3].values.reshape(1,-1).tolist()[0]
    schedule_group_3 = src_new.loc[:, group_3].sum(axis=1).values.reshape(1, -1).tolist()[0]
    # schedule_group_3_values = [ele for ele in schedule_group_3 if ele !=0]
    # print(len(schedule_group_3_values))
    # plt.hist(schedule_group_3_values,bins=50)

    # Combine 3 groups of exogenous variables and load curve
    gmm_df_4d = pd.DataFrame()
    gmm_df_4d['load'] = src_new['l']
    gmm_df_4d['schedule_1'] = schedule_group_1
    gmm_df_4d['schedule_2'] = schedule_group_2
    gmm_df_4d['schedule_3'] = schedule_group_3

    # ===Check===
    # gmm_df_4d['load'].plot()



    # ========================= Read Forecast results and true load values ==============================
    # Read best forecasting result: forecasting_model_grouped__445_l-200_l-10_l-20
    # model_cat_id = "forecasting_model_grouped_"
    # forecast_scheme = 'quarterly2quarterly'
    # code_path = os.getcwd()
    # fastec_dir = code_path + '/Output/FASTEC/'
    # res_dir = code_path + '/Output/LSTM/' + model_cat_id + forecast_scheme + '/Model_Output/results/'
    #
    # lstm_forecast = pd.read_csv(res_dir + 'Best_model_forecaste_result.csv', index_col=0, parse_dates=True)
    # lstm_best_pred = lstm_forecast['raw_best_pred']

    # On 1-dimensional clustering
    np.random.seed(666)
    X_test = gmm_df_4d['load'][0:10000]
    # X_test = lstm_best_pred[0:10000]
    cluster_num = 6
    transform_flag = False


    # ========================EM Algorithm=======================
    def em_fitting():
        if transform_flag:
            scaler = sp.MinMaxScaler()
            X_scaled = scaler.fit_transform(X_test.values.reshape(-1, 1))
            ran_idx = np.random.choice(len(X_scaled), cluster_num)
            sigma_init = np.random.random(cluster_num)
            mu_init = X_scaled[ran_idx].reshape(1, -1)[0]

            # plt.hist(X_scaled, bins=500)
        else:
            X_scaled = X_test.values
            ran_idx = np.random.choice(len(X_scaled), cluster_num)
            sigma_init = np.random.randint(1000, 10000, cluster_num)
            mu_init = X_scaled[ran_idx]
            plt.hist(X_scaled, bins=500)

        em = EM_Algo_1D(X=X_scaled, K=cluster_num, mu_init=mu_init, sigma_init=sigma_init, stop_criteria=0.0001)
        em.fit(iterate_num=5000)
        return em


    em_loadcurve = em_fitting()

    mu_record = pd.DataFrame(em_loadcurve.record_params['mu'])
    sigma_record = pd.DataFrame(em_loadcurve.record_params['sigma'])
    weight_record = pd.DataFrame(em_loadcurve.record_params['weight'])

    mu_record.to_csv(outdata_path + f'mu_record_{cluster_num}clusters.csv')
    sigma_record.to_csv(outdata_path + f'sigma_record_{cluster_num}clusters.csv')
    weight_record.to_csv(outdata_path + f'weight_record_{cluster_num}clusters.csv')

    """
    Iteration:2675
    weight: [0.10172497 0.51425737 0.15062232 0.1866101  0.0206829  0.02610234]
    sigma:[3439.41490276 1882.00964105 1378.23758782 1858.74728561 2829.829252 3499.90254549]
    mu:[13989.72576554 69694.15401414 78565.40467929 76240.37081904 29862.41488204 54434.97838222]
    Epsilon: 0.00998813280602917
    *************Converged**********
    """

    # =====================Plot the convergence of EM algorithm===============
    is_recorded = False

    if is_recorded:
        mu_record = pd.read_csv(outdata_path + f'mu_record_{cluster_num}clusters.csv', index_col=0)
        sigma_record = pd.read_csv(outdata_path + f'sigma_record_{cluster_num}clusters.csv', index_col=0)
        weight_record = pd.read_csv(outdata_path + f'weight_record_{cluster_num}clusters.csv', index_col=0)
    else:
        mu_record = pd.DataFrame(em_loadcurve.record_params['mu'])
        sigma_record = pd.DataFrame(em_loadcurve.record_params['sigma'])
        weight_record = pd.DataFrame(em_loadcurve.record_params['weight'])


    def rename_col(df, model_num=cluster_num):
        df.columns = [f'Model_{i+1}' for i in range(model_num)]
        return df


    def plot_em_convergence(mu, sigma, weight):
        plt.figure(figsize=(15, 6))
        max_iteration = len(mu)
        my_colors = ['b', 'r', 'g', 'y', 'k', 'm', 'c']
        my_style = ['-', '--', ':', "-."]
        my_line = list(itertools.product(my_colors, my_style))
        models = [f'Model_{i+1}' for i in range(cluster_num)]

        plt.subplot(3, 1, 1)
        for idx in range(len(mu.columns)):
            plt.plot(mu.loc[:, models[idx]], color=my_line[idx][0], linestyle=my_line[idx][1])
        # plt.xlim([0,65])
        plt.xlim([0, max_iteration])
        plt.title('Parameter: $\mu$', fontsize=16)
        # plt.ylabel('Mean Value')

        plt.subplot(3, 1, 2)
        for idx in range(len(sigma.columns)):
            plt.plot(sigma.loc[:, models[idx]], color=my_line[idx][0], linestyle=my_line[idx][1])
        # plt.xlim([0,65])
        plt.xlim([0, max_iteration])
        plt.title('Parameter: $\sigma$', fontsize=16)
        # plt.ylabel('Std Value')

        plt.subplot(3, 1, 3)
        for idx in range(len(weight.columns)):
            plt.plot(weight.loc[:, models[idx]], color=my_line[idx][0], linestyle=my_line[idx][1])
        # plt.xlim([0,65])
        plt.xlim([0, max_iteration])
        plt.title('Parameter: $\omega$', fontsize=16)
        plt.xlabel('Iteration', fontsize=17)
        # plt.ylabel('Weight Value')

        plt.tight_layout()
        plt.savefig(outplot_path + f'EM/EM_Convergence_{cluster_num}clusters.png', dpi=300)


    mu_record, sigma_record, weight_record = map(rename_col, (mu_record, sigma_record, weight_record))

    fig_em_convergence = plot_em_convergence(mu_record, sigma_record, weight_record)

    """
    Color of models:
    Model 1: blue
    Model 2: red
    Model 3: green
    Model 4: yellow
    Model 5: black
    Model 6: magenta
    """

    # fig_em_convergence.savefig(outplot_path + f'EM_Convergence_{cluster_num}clusters.png', dpi=300)

    # ====================compute the probability of sample that belongs to each distribution================
    # mu_est = em.mu

    use_record_params = False

    if use_record_params:
        em_estimator = {'weight': [0.10172497, 0.51425737, 0.15062232, 0.1866101, 0.0206829, 0.02610234],
                        'sigma': [3439.41490276, 1882.00964105, 1378.23758782, 1858.74728561, 2829.829252, 3499.90254549],
                        'mu': [13989.72576554, 69694.15401414, 78565.40467929, 76240.37081904, 29862.41488204,
                               54434.97838222]
                        }
    else:
        em_estimator = {'weight': em_loadcurve.weight,
                        'sigma': em_loadcurve.sigma,
                        'mu': em_loadcurve.mu
                        }

    """
    weight:
    [13990.10615243, 69775.30988833, 54418.63202583, 77427.65304675,
           29863.85491491]
    
    sigma:
    [3439.86652517, 1943.68563104, 3482.01753793, 1892.98292721,
           2828.60859839]
    
    mu:
    [13990.10615243, 69775.30988833, 54418.63202583, 77427.65304675,
           29863.85491491]
    """

    # test = list(zip(em_estimator['weight'], em_estimator['mu'], em_estimator['sigma']))

    em_optimal = EM_Algo_1D(K=cluster_num, mu_init=em_estimator['mu'], sigma_init=em_estimator['sigma'])

    # ================= Read forecasting result and classify=================

    best_prediction = pd.read_csv(res_dir + 'Best_model_forecaste_result.csv', index_col=0, parse_dates=True)
    # fastec_prediction = pd.read_csv(fastec_dir + 'actual_forecast.csv', index_col=0, parse_dates=True)

    load_forecast_values = best_prediction['raw_best_pred'].values

    load_clusters = list()
    # load_value = Load_clustering.values[321]

    for num, load_value in enumerate(load_forecast_values):
        forecast_load_cluster = list()
        # load_cluster.append(num)
        forecast_load_cluster.append(load_value)
        print(num)
        print(load_value)
        prob_x = em_optimal.E_Step(load_value)
        dis_idx = np.where(prob_x == max(prob_x))[0][0]
        forecast_load_cluster.append(dis_idx)
        forecast_load_cluster.append(max(prob_x))
        forecast_load_cluster.extend(prob_x)
        load_clusters.append(forecast_load_cluster)

    cols = [f'prob_m{k}' for k in range(cluster_num)]

    load_clusters_df = pd.DataFrame(data=load_clusters, index=best_prediction.index,
                                    columns=['forecast_load', 'cluster', 'max_prob'] + cols)

    load_clusters_df = pd.concat([load_clusters_df, gmm_df_4d['load']], axis=1)
    load_clusters_df.dropna(axis=0, inplace=True)

    # load_clusters_df['cluster'].value_counts()
    # load_clusters_df['probability'].describe()
    #
    plt.hist(load_clusters_df['max_prob'], bins=1000)
    # plt.hist(gmm_df_4d['load'], bins=1000)

    weighted_cluster_load = pd.DataFrame()
    for k in range(cluster_num):
        weighted_k = load_clusters_df[f'prob_m{k}'] * em_estimator['mu'][k]
        if k == 0:
            weighted_cluster_load = weighted_k
        else:
            weighted_cluster_load += weighted_k

    load_clusters_df['weighted_cluster_load'] = weighted_cluster_load
    load_clusters_df.drop(labels=cols, inplace=True, axis=1)

    # subtracted_load = list(map(lambda load, cls_num: load - em_estimator['mu'][int(cls_num)],
    #                            load_clusters_df['forecast_load'].values, load_clusters_df['cluster'].values))
    #
    load_clusters_df['cluster_mean'] = list(map(lambda cls_num: em_estimator['mu'][int(cls_num)], load_clusters_df['cluster'].values))
    load_clusters_df['cluster_sigma'] = list(map(lambda cls_num: em_estimator['sigma'][int(cls_num)], load_clusters_df['cluster'].values))
    # load_clusters_df['subtracted_load'] = subtracted_load
    load_clusters_df['cluster_error'] = load_clusters_df['load'] - load_clusters_df['cluster_mean']
    # plt.plot(load_clusters_df['cluster_error'])

    load_clusters_df['forecast_error'] = load_clusters_df['load'] - load_clusters_df['forecast_load']
    # plt.plot(load_clusters_df['forecast_error'])

    import pickle
    # pickle and svae the clustered results
    with open(outdata_path + 'ClusteredLoadsForTrading.pkl', 'wb') as cluter_df_file:
        pickle.dump(load_clusters_df, cluter_df_file)

    # load_clusters_df.to_csv(outdata_path + 'ClusteredLoadsForTrading.csv')

em_clustering_forecast()
# shift_sigma = 1
#
# load_clusters_df['cluster_shift_sigma'] = load_clusters_df['cluster_mean'] + load_clusters_df['cluster_sigma']
"""
plt.figure(figsize=(15, 5))
plt.subplot(2, 1, 1)
plt.plot(load_clusters_df['load'])
# plt.plot(load_clusters_df['forecast_load'])
plt.plot(load_clusters_df['cluster_mean'])
# plt.plot(load_clusters_df['cluster_shift_sigma'])

plt.subplot(2, 1, 2)
plt.plot(load_clusters_df['load'])
plt.plot(load_clusters_df['forecast_load'], 'g')
plt.tight_layout()
plt.savefig(outplot_path + 'load_forecast_cluster.png', dpi=300)

# ====Forecast errors distribution
plt.hist(load_clusters_df['forecast_error'], bins=500)

# plt.plot(load_clusters_df['subtracted_load'])


# =============Analyze typical forecasting structure
# type 1:
import datetime as dt

sample_1 = load_clusters_df[load_clusters_df.index.date == dt.date(2017, 10, 3)]
plt.figure(figsize=(15, 5))
plt.plot(sample_1.loc[:, ['load']])
plt.plot(sample_1.loc[:, ['forecast_load']])
plt.plot(sample_1.loc[:, ['weighted_cluster_load']])


# =================Analyze the exogenous variables for each cluster========

# cluster_1 = load_clusters_df[load_clusters_df['cluster'] == 1]
#
# plt.figure(figsize=(15,5))
#
# plt.hist(cluster_1['schedule_1'], bins=50)
# plt.hist(cluster_1['schedule_2'], bins=50)
# plt.hist(cluster_1['schedule_3'], bins=50)
#
# def plot_cluster_schedules(cluster_df):
#     pass


# =================ACF and PACF of subtracted load curve

def plot_acf_pacf(signal, lags=None, name=None):
    plt.figure(figsize=(20, 5))
    acf = plt.subplot(1, 2, 1)
    smt.graphics.plot_acf(signal, lags=lags, ax=acf)
    plt.xlabel('Time Lag', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    pacf = plt.subplot(1, 2, 2)
    smt.graphics.plot_pacf(signal, lags=lags, ax=pacf)
    plt.xlabel('Time Lag', fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.tight_layout()
    plt.savefig(name + '.pdf', dpi=300)
    plt.show()


def plot_acf(y, lags=None, name=None):
    plt.figure(figsize=(20, 5))
    acf_all = plt.subplot(2, 1, 1)
    smt.graphics.plot_acf(y, lags=None, ax=acf_all, unbiased=True)
    plt.xticks(fontsize=17)
    plt.yticks(fontsize=17)
    plt.title('')
    acf_lags = plt.subplot(2, 1, 2)
    smt.graphics.plot_acf(y, lags=lags, ax=acf_lags, unbiased=True)
    plt.xlabel('Time Lag', fontsize=18)
    plt.xticks(fontsize=17)
    plt.yticks(fontsize=17)
    plt.title('')
    plt.tight_layout()
    plt.savefig(name + '.pdf', dpi=300)
    plt.show()


if_acf_plot = False
if if_acf_plot:
    plot_acf(y=load_clusters_df['subtracted_load'], lags=1500)
"""