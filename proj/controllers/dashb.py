import json
import pandas as pd
import plotly
import plotly.express as px

from proj.controllers import default


def get_activs(df, seq_df_colname='Sequence'):
    df['act seq'] = df[seq_df_colname].apply(lambda x: x.split(' '))
    activs = [i[1] for i in enumerate(df['act seq'].explode().dropna().drop_duplicates())]
    return activs


def count_var(activ, df_var):
    return len([line for line in df_var['Sequence'] if activ in line])


# TEventos> TCases > TVariants > AVG Ev > AVG Act > AVG Time

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


def heat(obj, cl, index):
    result = default.pdirectory[default.datafilter['arq']].copy()

    r1 = result[result.cluster.isin(cl)]
    r1['act seq'] = r1['Sequence'].apply(lambda x: x.split(' '))
    r1['transitions'] = r1['act seq'].apply(lambda x: [(x[i - 1], x[i]) for i in range(1, len(x))])

    total_var_activs = pd.DataFrame(columns=['Activs'])
    total_var_activs['Activs'] = get_activs(r1)
    vartotal = result.drop_duplicates(subset='Sequence')
    for cluster in cl:
        total_var_activs[str(cluster)] = total_var_activs['Activs'].apply(
            lambda x: count_var(x, vartotal[vartotal.cluster == cluster]))

    list_activs = total_var_activs['Activs'].tolist()
    list_clusters = total_var_activs.columns.tolist()[1:]

    df = pd.DataFrame({str(i): total_var_activs[i].tolist() for i in list_clusters}, index=list_activs)
    fig = px.imshow(df, labels={'x': 'Cluster', 'y': 'Activity', 'z': 'Total Variants'}, x=list_clusters, y=list_activs,
                    color_continuous_scale='blues')
    fig.update_layout(xaxis={'type': 'category'}, yaxis_nticks=len(list_activs), xaxis_nticks=len(list_clusters))
    fig.update_xaxes(side="top")

    obj.heatmaps[index] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
