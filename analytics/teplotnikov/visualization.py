import matplotlib.pyplot as plt
from matplotlib.colors import Colormap, ListedColormap
import seaborn as sns

sns.set(style='whitegrid')
palette = sns.color_palette('tab10', n_colors=50)
cmap = ListedColormap(palette)

colors = {
    0: 'teal',
    1: 'darkturquoise',
    2: 'red',
    3: 'crimson',
    4: 'darkorange',
    5: 'gold',
    6: 'magenta',
    7: 'purple',
    8: 'darkorchid',
    9: 'lime',
    10: 'limegreen',
    11: 'mediumvioletred',
    12: 'sienna',
    13: 'limegreen',
    14: 'royalblue',
    15: 'mediumblue',
}

import pandas as pd
import numpy as np
from wordcloud import WordCloud

def get_inds(labels, k):
    return np.argwhere(labels == k).reshape((-1,))

def draw_wordcloud(texts, max_words=1000, width=900, height=400, random_state=10):
    wordcloud = WordCloud(background_color='white', max_words=max_words,
                          width=width, height=height, random_state=random_state)

    joint_texts = ' '.join(list(texts))
    wordcloud.generate(joint_texts)
    return wordcloud.to_image()


def draw_cluster_clouds(data, clusters, n_clusters, alert_by='text', cloud_kwargs={}):
    for i in range(n_clusters):
        inds = get_inds(clusters, i)
        print('cluster: {}; samples: {}'.format(i + 1, len(inds)))
        if len(inds) == 0:
            print('empty')
            continue
        display(draw_wordcloud(data.iloc[inds][alert_by], **cloud_kwargs))