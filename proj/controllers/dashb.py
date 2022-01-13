import json
import pandas as pd
import plotly
import plotly.express as px

from proj.controllers.default import pdirectory, datafilter
from proj.controllers.graphsconstr import get_vertices, get_edges


def get_activs(df, seq_df_colname='Sequence'):
    df['act seq'] = df[seq_df_colname].apply(lambda x: x.split(' '))
    activs = [i[1] for i in enumerate(df['act seq'].explode().dropna().drop_duplicates())]
    return activs


def count_var(activ, df_var):
    return len([line for line in df_var['Sequence'] if activ in line])


# TEventos> TCases > TVariants > AVG Ev > AVG Act > AVG Time

def get_metrics(obj, c1, index):
    result = pdirectory[datafilter['arq']].copy()

    # ACTIVITIES MIN, AVG, MAX
    res = result[result.cluster.isin(c1)]
    res['countAct'] = res['Sequence'].apply(lambda x: len(set(x.split(' '))))
    obj.activ[index] = {'min': res['countAct'].min(), 'avg': "{:.1f}".format(res['countAct'].mean()), 'max': res['countAct'].max()}

    # COUNT VARIANTS
    obj.varCount[index] = int(pd.DataFrame(res['Sequence'].explode().dropna().drop_duplicates()).count())

    # EVENTS AVG
    res['evnts'] = res['Sequence'].apply(lambda x: len(x.split(' ')))
    obj.evt[index] = {'min': res['evnts'].min(), 'avg': "{:.1f}".format(res['evnts'].mean()), 'max': res['evnts'].max()}

    # Total Cases
    obj.totalCases[index] = int(res.shape[0])

    # Total Events
    obj.totalEvnts[index] = int(res['evnts'].sum())


def heat_activs(obj, cl, index):
    result = pdirectory[datafilter['arq']].copy()

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
    print(df)
    print(df.transpose())
    fig = px.imshow(df.transpose(), labels={'x': 'Cluster', 'y': 'Activity', 'z': 'Total Variants'}, x=list_activs, y=list_clusters,
                    color_continuous_scale='blues')
    fig.update_layout(xaxis={'type': 'category'}, yaxis_nticks=len(list_clusters), xaxis_nticks=len(list_activs))
    fig.update_xaxes(side="top")

    obj.heatmaps[index] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def heat_trans(obj, cl, index):
    result = pdirectory[datafilter['arq']].copy()
    result['Sequence'] = result['Sequence'].apply(lambda x: 'Start_Process ' + x + ' End_Process')
    vertices, verts = get_vertices(result)
    edges_labels, edges_ids = get_edges(result[result.cluster.isin(cl)], verts, vertices)
    edlog_labels, _ = get_edges(result, verts, vertices)
