import pandas as pd
import numpy as np
EARTH_RADIUS = 6371.009

def haversin(theta):
    return (1 - np.cos(theta)) / 2.0


def haversine_2D_mat(data1, data2):
    lats1, lons1 = data1['lat'].values, data1['lon'].values
    phis1, lambs1 = np.radians(lats1).reshape(-1, 1), np.radians(lons1).reshape(-1, 1)

    lats2, lons2 = data2['lat'].values, data2['lon'].values
    phis2, lambs2 = np.radians(lats2).reshape(-1, 1), np.radians(lons2).reshape(-1, 1)

    deltas_lats = phis1 - phis2.T
    deltas_lons = lambs1 - lambs2.T

    cos_phis1 = np.cos(phis1)
    cos_phis2 = np.cos(phis2)
    a = haversin(deltas_lats) + cos_phis1 * cos_phis2.T * haversin(deltas_lons)

    vec_dist = 2 * EARTH_RADIUS * np.arcsin(np.sqrt(a))
    return vec_dist * 1000


def get_list(lat, lon, R, rub):
    point_df = pd.DataFrame({"lat": [lat], "lon": [lon]})
    ls = haversine_2D_mat(point_df, df)[0]
    r = df.loc[ls <= R, "rubrics"]
    rub_split = r.str.split(";").dropna()
    rub_split = rub_split.apply(lambda x: set(x))
    lst = {}
    for sub in rub_split:
        for a in rub:
            fl = False
            for x in a:
                if x in sub:
                    fl = True
            if fl:
                lst["_".join(a)] = lst.get("_".join(a), 0) + 1
    return lst


df = pd.read_csv("geo_data.csv")
df = df.dropna(subset = ["lat"])
df = df[df["address"] != "Москва"]
df = df.drop("geocode_status", axis = 1)
