import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import rc
rc('text', usetex=True)


def histogram_single_channel(data, out_path):

    data = data[data > 0]

    np.random.seed(8675309)

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    print("min deviation {}".format(data.min()))
    print("max deviation {}".format(data.max()))
    print("mean deviation {}".format(data.mean()))

    bins = np.linspace(0, 256, 256)
    ax.hist(data, color='#0FC25B', edgecolor='k', bins=bins, rwidth=0.80, density=False, alpha=0.5)

    # Reshape data for scikit-learn.
    #data = data[:, np.newaxis]
    #kde = KernelDensity(kernel='gaussian', bandwidth=0.5).fit(data)

    # Resize bins for probability density function.
    #bins = np.linspace(0, 256, 256)[:, np.newaxis]
    #log_dens = kde.score_samples(bins)

    # ax.plot(bins[:, 0], np.exp(log_dens), 'r-')
    # ax.plot(data[:, 0], -0.008 - 0.02 * np.random.random(data.shape[0]), 'kd')
    ax.tick_params(axis='both', which='major', labelsize=12)
    # ax.set_xlim(-.2, 16.2)
    # ax.set_ylim(-0.035, 0.26)

    ax.set_xlabel(r"\[\textbf{Pixel Intensity}\ \left({cm}\right)\]",
                  fontdict={"fontsize": 20},
                  labelpad=20)

    ax.set_ylabel(r"\[\textbf{Count}\]",
                  fontdict={"fontsize": 20},
                  labelpad=20)

    ax.set_title(label=r"\[\textbf{Distribution of Pixel Intensities}\]",
                 fontdict={"fontsize": 20})

    plt.savefig(out_path)
    plt.close('all')


def derivative_rigorous(curve_func, x, h=1e-4):
    dy = (curve_func(x + h) - curve_func(x)) / h

    return dy


def clean_poly_eq(coefficients, scientific_notation=True):
    n = len(coefficients)
    degs = list(range(n))
    coefficients = ["{0:.3E}".format(i).split('E') for i in coefficients]
    coefficients.reverse()
    print(coefficients)
    pieces = []
    for ((cof1,cof2), deg) in zip(coefficients, degs):
        if deg == 0:
            if float(cof1) > 0:
                piece = "{0}{{E}}^{{{1}}}".format(cof1, cof2) if cof2 != '+00' else "{0}".format(cof1)
            else:
                piece = "{0}{{E}}^{{{1}}}".format(cof1, cof2)

        elif deg == 1:
            if float(cof1) > 0:
                piece = "+{0}{{E}}^{{{1}}}{{x}}".format(cof1, cof2)
            else:
                piece = "{0}{{E}}^{{{1}}}{{x}}".format(cof1, cof2)

        else:
            if float(cof1) > 0:
                piece = "+{0}{{E}}^{{{1}}}{{x}}^{{{2}}}".format(cof1, cof2, deg)
            else:
                piece = "{0}{{E}}^{{{1}}}{{x}}^{{{2}}}".format(cof1, cof2, deg)

        pieces.append(piece)

    pieces.reverse()

    equation = r"\[{y} = " + "".join(pieces[::-1]) + "\]"

    return equation


def clean_lin_eq(coefficients, scientific_notation=True):
    n = len(coefficients)
    coefficients = [round(i, 2) for i in coefficients]

    if coefficients[1] > 0:
        eqn_string = "{0}{{x}} + {1}".format(coefficients[0], coefficients[1])
    else:
        eqn_string = "{0}{{x}} {1}".format(coefficients[0], coefficients[1])

    equation = r"\[{y} = " + eqn_string + "\]"

    return equation


def get_poly_hat(x_values, y_values, poly_degree):
    coeffs = np.polyfit(x_values, y_values, poly_degree)
    poly_eqn = np.poly1d(coeffs)

    y_bar = np.sum(y_values) / len(y_values)
    ssreg = np.sum((poly_eqn(x_values) - y_bar) ** 2)
    sstot = np.sum((y_values - y_bar) ** 2)
    r_square = ssreg / sstot

    return (coeffs, poly_eqn, r_square)


def plot_growth_curves_all_in_one(df, aom_ids, out_path, tag):
    fig, ax = plt.subplots(1, 1, figsize=(20, 10))
    plt.axvline(pd.to_datetime(['2019-06-05 12:00:00'], format='%Y-%m-%d %H:%M:%S'), linestyle=':')

    for id in aom_ids:
        df_this = df.loc[df['aom_name'] == id, ['pixel_count', 'date']]
        x = df_this.loc[:, 'date'].values
        y = df_this.loc[:, 'pixel_count'].values
        ax.plot(x, y, 'o')

    # ax.tick_params(axis='both', which='major', labelsize=12)

    ax.set_xlabel(r"\[\textbf{Index}\ \left({cm}\right)\]",
                  fontdict={"fontsize": 20},
                  labelpad=20)

    ax.set_ylabel(r"\[\textbf{Raw Pixel Counts}\]",
                  fontdict={"fontsize": 20},
                  labelpad=20)

    ax.set_title(label=r"\[\textbf{" + tag + r"Ground Cover Fraction Curve}\]",
                 fontdict={"fontsize": 20})

    plt.savefig(out_path)
    plt.close('all')


def growth_curve_by_aom(ext_df, aom_ids, start_date, poly_degree, h, out_path, tag):

    for aom in aom_ids:
        df = ext_df.loc[(ext_df['aom_name'] == aom) &
                        (ext_df['date'] >= start_date), ['pixel_count', 'date']]

        fig, ax = plt.subplots(1,1, figsize=(20,10))

        x = df.loc[:, 'date'].values
        y = df.loc[:, 'pixel_count'].values
        x_num = np.arange(0, len(x), 1)
        x_date_range = pd.date_range(x[0], x[-1], periods=len(x))

        coeffs, poly_eqn, r_square = get_poly_hat(x_values=x_num, y_values=y, poly_degree=poly_degree)

        y_hat = poly_eqn(x_num)

        clean_equation = clean_poly_eq(coefficients=coeffs)

        dyy = derivative_rigorous(poly_eqn, x_num, h=h)

        ax.plot(x, y, '-o')
        ax.plot(x_date_range, y_hat, color='red')
        ax.plot(x_date_range, dyy, color='green')

        y_min, y_max = ax.get_ylim()
        hail_line = np.linspace(y_min, y_max, 200)

        ax.plot([pd.to_datetime('2019-06-05 12:00:00', format='%Y-%m-%d %H:%M:%S')]*200, hail_line, ':')

        ax.legend(('Pixel counts', 'Modeled growth', 'Derivative', 'Hail event'))

        ax.set_xlabel(r"\[\textbf{Flight Date}\]",
                      fontdict={"fontsize": 20},
                      labelpad=20)

        ax.set_ylabel(r"\[\textbf{Raw Pixel Counts}\]",
                      fontdict={"fontsize": 20},
                      labelpad=20)

        title = 'Ground Cover Fraction for ' + aom.split('_')[1]

        ax.set_title(label=r"\[\textbf{" + tag + title + r"}\]",
                     fontdict={"fontsize": 20})

        plt.savefig(out_path)
        plt.close('all')


if __name__=='__main__':

    # Read in growth curve data.
    control_df_counts = pd.read_csv('/home/will/matrix_gibberellin_study/growth_curve_data_sets/control_growth_data.csv')
    control_df_counts.loc[:, 'date'] = pd.to_datetime(control_df_counts.loc[:, 'date'], format='%Y-%m-%d')
    gib_treat_df_counts = pd.read_csv('/home/will/matrix_gibberellin_study/growth_curve_data_sets/gib_treat_growth_data.csv')
    gib_treat_df_counts.loc[:, 'date'] = pd.to_datetime(gib_treat_df_counts.loc[:, 'date'], format='%Y-%m-%d')

    # Growth curve for a single AOM.
    control_growth_curve_path = '//home/will/matrix_gibberellin_study/gib_experiment_visuals/control_growth_curve_single_aom_raw_pixel_counts_22.pdf'
    gib_treat_growth_curve_path = '/home/will/matrix_gibberellin_study/gib_experiment_visuals/gib_treat_growth_curve_single_aom_raw_pixel_counts_22.pdf'

    aom_ids = ['id_22.tif']
    params = {
        'ext_df': control_df_counts,
        'aom_ids': aom_ids,
        'start_date': '2019-03-01',
        'out_path': control_growth_curve_path,
        'poly_degree': 4,
        'h': 1e-5,
        'tag': r'Control\ ',
    }
    growth_curve_by_aom(**params)

    aom_ids = ['id_22.tif']
    params = {
        'ext_df': gib_treat_df_counts,
        'aom_ids': aom_ids,
        'start_date': '2019-03-01',
        'out_path': gib_treat_growth_curve_path,
        'poly_degree': 4,
        'h': 1e-5,
        'tag': r'Gibberellin Test\ '
    }
    growth_curve_by_aom(**params)

    # # Growth curve for many AOMs.
    # growth_curves_all_path = '/home/will/peanut_growth_curves/peanut_growth_curve_visuals/growth_curve_all_raw_pixel_counts.pdf'
    # plot_growth_curves_all_in_one(df=df_counts, aom_ids=aom_ids, out_path=growth_curves_all_path)
