import numpy as np
import pandas as pd
import seaborn as sns
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt

sns.set_style('white')
plt.rcParams['figure.figsize'] = 8, 4
plt.rcParams['legend.frameon'] = True
palette = sns.color_palette('Set1')
sns.set_palette(palette)


def pe(y, y_pred):
    return (y_pred - y) / y * 100
    

def ape(y, y_pred):
    return np.abs(y_pred - y) / y * 100


def moving_avg(arr, window=10):
    average_arr = []
    for ind in range(len(arr) - window + 1):
        average_arr.append(np.mean(arr[ind:ind+window]))
    return average_arr


def plot_target_hist(y, y_pred):
    plt.title(f"Распределение логарифма целевой переменной")
    sns.histplot(y, label="Факт", bins=20, kde=True, linewidth=1.5,)
    sns.histplot(y_pred, label="Предсказано", bins=20, kde=True, linewidth=1.5,)
    plt.xlabel("Значение целевой переменной")
    plt.ylabel("Число наблюдений")
    plt.legend()
    plt.show()

    
def plot_ape_bins(y, y_pred, max_ape=160, step=5):
    apes = ape(y, y_pred)
    plt.title(f"Распределение процентной ошибки")
    sns.histplot(apes, bins=list(range(0, max_ape + 1, step)))
    plt.xlabel(xlabel="Абсолютная процентная ошибка, %")
    plt.grid()
    plt.show()

    
def plot_regression_residuals(y, y_pred, post_title=""):
    sign_resid = y - y_pred
    abs_resid = np.abs(sign_resid)

    fig, axes = plt.subplots(ncols=2, figsize=(14, 3))
    for i, resid in enumerate([abs_resid, sign_resid]):
        name = "|остатков|" if i == 0 else "остатков"
        axes[i].set_title(f'Диаграмма {name} регрессии {post_title}')

        label = "|Остатки|" if i == 0 else "Остатки"
        sns.regplot(y=resid, x=y_pred, label=label, data=None, scatter=True, ax=axes[i])

        axes[i].set_xlabel("Прогноз")
        axes[i].set_ylabel(f"{label} регрессии")
        axes[i].legend()

    plt.show()


def plot_scatter(y, y_pred, post_title=""):
    r = np.corrcoef(y_pred, y)[0, 1]
    
    plt.title(f"Диаграмма разброса факт vs прогноз {post_title}")
    sns.regplot(x=y_pred, y=y, scatter=True)

    # Фиксирует плашку в углу графика, независимо от масштаба осей
    plt.text(
        0.05, 0.95, f"Корреляция: {r:.2f}",
        transform=plt.gca().transAxes,
        fontsize=11,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="white", alpha=0.8)
    )
    plt.xlabel("Прогноз")
    plt.ylabel("Факт")
    plt.show()

    
def plot_predict_sorted(y, y_pred, y_low=None, y_high=None, window=3, post_title=""):    
    inds = list(range(len(y)))
    sorted_inds = np.argsort(y)

    y_mean = np.mean(y)
    y_sorted = y[sorted_inds]
    y_pred_sorted = y_pred[sorted_inds]
    y_pred_moving_avg = moving_avg(y_pred[sorted_inds], window)

    plt.title(f"Упорядоченный факт vs прогноз {post_title}")
    plt.axhline(y_mean, color="royalblue", label=f"Средний таргет: {y_mean:.2e}")
    plt.plot(inds, y_pred_sorted, label="Прогноз", color="tab:blue", alpha=0.5)
    plt.plot(inds, y_sorted, label="Факт", color="red")
    plt.plot(inds[window - 1:], y_pred_moving_avg, label="Сглаживание", color="lime")
    
    if y_low is not None:
        plt.axhline(y_low, color="black")
    if y_high is not None:
        plt.axhline(y_high, color="black")

    plt.legend()
    plt.ylabel("Целевая переменная")
    plt.xlabel("Объект (по порядку факта)")
    plt.grid()
    plt.show()


def plot_ape_sorted(y, y_pred, window=3, post_title=""):
    inds = list(range(len(y)))
    sorted_inds = np.argsort(y)

    y_mean = np.mean(y)
    y_sorted = y[sorted_inds]
    y_pred_sorted = y_pred[sorted_inds]

    apes = ape(y_sorted, y_pred_sorted)
    pes = pe(y_sorted, y_pred_sorted)
    apes_moving_avg = moving_avg(apes, window)
    pes_moving_avg = moving_avg(pes, window)


    fig, axes = plt.subplots(ncols=2, figsize=(14, 4))
    for i, err in enumerate([apes, pes]):
        err_moving_avg = moving_avg(err, window)

        err_mean = np.mean(err)
        err_median = np.median(err)
        axes[i].axhline(err_mean, color="red", label=f"Среднее: {err_mean:.2f}%")
        axes[i].axhline(err_median, color="magenta", label=f"Медиана: {err_median:.2f}%")

        axes[i].set_title(f"Упорядоченная ошибка {'(модуль)' * (1 - i)}{post_title}")
        axes[i].plot(inds, err, label="Ошибка", color="tab:blue", alpha=0.7)
        axes[i].plot(inds[window - 1:], err_moving_avg, label="Сглаживание", color="lime")

        axes[i].legend()
        axes[i].set_ylabel(f"{'A' * (1 - i)}PE, %")
        axes[i].set_xlabel("Объект (по порядку факта)")
        axes[i].grid()

    plt.show()


def confusion_matrix(y_true, y_pred, y_low, y_high, post_title=""):
    y_level = y_true.copy().to_numpy()
    y_level[y_level < y_low] = 1
    y_level[(y_level >= y_low) * (y_level < y_high)] = 2
    y_level[y_level >= y_high] = 3
    
    y_pred_level = y_pred.copy()
    y_pred_level[y_pred_level < y_low] = 1
    y_pred_level[(y_pred_level >= y_low) * (y_pred_level < y_high)] = 2
    y_pred_level[y_pred_level >= y_high] = 3
    
    labels = {1: "Низкая", 2: "Средняя", 3: "Высокая"}
    cm = np.zeros((3, 3))
    for i, l_true in enumerate(labels.keys()):
        for j, l_false in enumerate(labels.keys()):
            true_inds = np.argwhere(y_level == l_true)
            pred_mask = (y_pred_level[true_inds] == l_false)
            cm[j, i] = pred_mask.sum()#.astype(int)
            
    cm = pd.DataFrame(cm, columns=labels.values(), index=labels.values())
    cm = cm.iloc[[2, 1, 0]]
    
    sns.heatmap(cm, annot=True)
    plt.title(f"Матрица прогнозов (кол-во){post_title}")
    plt.xlabel("Истина")
    plt.ylabel("Прогноз")
    plt.show()


def confusion_matrix_ape(y_true, y_pred, y_low, y_high, post_title=""):
    y_level = y_true.copy().to_numpy()
    y_level[y_level < y_low] = 1
    y_level[(y_level >= y_low) * (y_level < y_high)] = 2
    y_level[y_level >= y_high] = 3
    
    y_pred_level = y_pred.copy()
    y_pred_level[y_pred_level < y_low] = 1
    y_pred_level[(y_pred_level >= y_low) * (y_pred_level < y_high)] = 2
    y_pred_level[y_pred_level >= y_high] = 3

    def ape(y_true, y_pred):
        return np.abs(y_true - y_pred) / np.abs(y_true)
    
    labels = {1: "Низкая", 2: "Средняя", 3: "Высокая"}
    cm = np.zeros((3, 3))
    for i, l_true in enumerate(labels.keys()):
        for j, l_pred in enumerate(labels.keys()):
            mask = (y_level == l_true) & (y_pred_level == l_pred)
            if mask.sum() == 0:
                cm[j, i] = 0.0
            else:
                cm[j, i] = ape(y_true[mask], y_pred[mask]).mean() * 100
            
    cm = pd.DataFrame(cm, columns=labels.values(), index=labels.values())
    cm = cm.iloc[[2, 1, 0]]
    
    sns.heatmap(cm, annot=True)
    plt.title(f"Матрица прогнозов (APE, %){post_title}")
    plt.xlabel("Истина")
    plt.ylabel("Прогноз")
    plt.show()
