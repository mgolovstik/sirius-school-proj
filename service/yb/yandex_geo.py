from sklearn.neighbors import BallTree
import numpy as np
import pandas as pd
from collections import Counter

data = pd.read_excel("yb/data/geo_data.xlsx")
data = data.dropna(subset=["lat", "lon", "rubrics"])
data["rub_list"] = (
    data["rubrics"]
        .astype(str)
        .str.split(";")
        .apply(lambda x: [s.strip() for s in x if s.strip()])
)

EARTH_R = 6371000.0
all_rubrics = Counter(x for lst in data["rub_list"] for x in lst)
keep_rubrics = {k for k, v in all_rubrics.items() if v >= 100}

coords_data = np.radians(data[["lat", "lon"]].values)
tree = BallTree(coords_data, metric  = "haversine")

async def get_lst(lat, lon, R_m):
    idxs = tree.query_radius(np.radians([[lat, lon]]), r = R_m / EARTH_R)[0]
    lst = {}
    for i in idxs:
        for r in data.iloc[i]["rub_list"]:
            if r in keep_rubrics:
                lst[r] = lst.get(r, 0) + 1
    return lst

async def get_yandex_data(lat, lon, radius, rubrics) -> pd.DataFrame:
    geo_df = pd.DataFrame([await get_lst(lat, lon, radius)]).fillna(0).astype(int)
    geo_df.columns = [f"cnt_{c.replace(' ', '_')}" for c in geo_df.columns]
    geo_df = geo_df.reindex(columns=rubrics, fill_value=0)
    print(geo_df)
    return geo_df
