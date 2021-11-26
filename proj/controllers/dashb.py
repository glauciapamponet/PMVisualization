import pandas as pd
import plotly as plt
from proj.controllers import default


def get_metrics(obj, c1, index):
    result = default.pdirectory[default.datafilter['arq']].copy()

    # ACT AVG
    res = result[result.cluster.isin(c1)]
    res['countAct'] = res['Sequence'].apply(lambda x: len(set(x.split(' '))))
    obj.activAvg[index] = int(res['countAct'].mean())

    # COUNT VARIANTS
    obj.varCount[index] = int(pd.DataFrame(res['Sequence'].explode().dropna().drop_duplicates()).count())

    # EVENTS AVG
    res['evnts'] = res['Sequence'].apply(lambda x: len(x.split(' ')))
    obj.evtAvg[index] = int(res['evnts'].mean())

    obj.totalCases[index] = int(res.shape[0])  # Total Cases

    obj.totalEvnts[index] = int(res['evnts'].sum())  # Total Events
