import json
import pandas as pd
import plotly
import plotly.express as px

from proj.controllers import default as dft
from proj.controllers.graphsconstr import get_vertices, get_key


def choice_view(obj, wrd_choice):
    if wrd_choice == 'activ':
        heat_activs(obj, obj.c1, 0)
        heat_activs(obj, obj.c2, 1)
    elif wrd_choice == 'trans':
        heat_trans(obj, obj.c1, 0)
        heat_trans(obj, obj.c2, 1)


def get_log():
    result = dft.pdirectory[0].copy()
    result['Sequence'] = result['Sequence'].apply(lambda x: 'Start_Process ' + x + ' End_Process')
    # result = result.drop_duplicates(subject='Sequence') # para mudar para visu por case
    vertices, verts = get_vertices(result)
    vert_dict = {vertices[i]: verts[i] for i in vertices.keys()}  # abreviação: nome
    return result, vert_dict


def get_datalog():
    res, vdict = get_log()
    variants = int(pd.DataFrame(res['Sequence'].explode().dropna().drop_duplicates()).count())
    cases = int(res.shape[0])
    act = len(vdict.keys())
    return vdict, {'v': variants, 'c': cases, 'a': act}


def count_freq(item, df):
    return len([line for line in df if item in line])


# TEventos> TCases > TVariants > AVG Ev > AVG Act > AVG Time
def get_metrics(obj, c1, index):
    result = dft.pdirectory[0].copy()

    # ACTIVITIES MIN, AVG, MAX
    res = result[result.cluster.isin(c1)]
    res['countAct'] = res['Sequence'].apply(lambda x: len(set(x.split(' '))))
    obj.activ[index] = {'min': res['countAct'].min(),
                        'avg': "{:.1f}".format(res['countAct'].mean()),
                        'max': res['countAct'].max()}

    # COUNT VARIANTS
    obj.varCount[index] = int(pd.DataFrame(res['Sequence'].explode().dropna().drop_duplicates()).count())

    # EVENTS AVG
    res['evnts'] = res['Sequence'].apply(lambda x: len(x.split(' ')))
    obj.evt[index] = {'min': res['evnts'].min(),
                      'avg': "{:.1f}".format(res['evnts'].mean()),
                      'max': res['evnts'].max()}

    # Total Cases
    obj.totalCases[index] = int(res.shape[0])

    # Total Events
    obj.totalEvnts[index] = int(res['evnts'].sum())


def get_data(labels, df, clist, columns):
    dftrans = pd.DataFrame(columns=[columns[0]])
    dftrans[columns[0]] = labels

    # frequencia por cluster
    dfheat = pd.DataFrame({str(i): dftrans[columns[0]].apply(
        lambda x: count_freq(x, df[df.cluster == i][columns[1]])).tolist() for i in clist}, index=labels)

    # frequencia de toda a seleção
    if len(clist) > 1:
        dfheat['Selection'] = dftrans[columns[0]].apply(
            lambda x: count_freq(x, df[df.cluster.isin(clist)][columns[1]])).tolist()

    return dfheat


def heat_activs(obj, cl, index):
    result, act_dict = get_log()
    act_log = sorted(act_dict.keys())

    df = get_data(act_log, result, cl, ['Activs', 'Sequence'])
    list_clusters = df.columns.tolist()

    fig = px.imshow(df.transpose(), labels={'x': 'Activity', 'y': 'Cluster', 'z': 'Total Variants'}, x=act_log,
                    y=list_clusters, width=700, height=450, color_continuous_scale='blues')
    fig.update_layout(xaxis={'type': 'category'}, yaxis_nticks=len(list_clusters), xaxis_nticks=len(act_log))
    fig.update_xaxes(side="top")
    obj.heatmaps[index] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def get_transitions(df, dictio):
    df['transitions'] = df['act seq'].apply(
        lambda x: [(get_key(x[i - 1], dictio), get_key(x[i], dictio)) for i in range(1, len(x))])
    labels = list(df['transitions'].explode().dropna().drop_duplicates())
    return [(i, j) for i, j in labels]


def heat_trans(obj, cl, index):
    result, vert_dict = get_log()

    # lista de todas as transições possiveis (usa o log para os heatmaps serem iguais)
    trans_log = sorted(list(set(get_transitions(result, vert_dict))))

    df = get_data(trans_log, result, cl, ['Transitions', 'transitions'])
    list_clusters = df.columns.tolist()

    fig = px.imshow(df.transpose(), labels={'x': 'Transition', 'y': 'Cluster', 'z': 'Total Variants'},
                    x=[str(i[0]) + "," + str(i[1]) for i in trans_log],
                    y=list_clusters, color_continuous_scale='blues', width=700, height=450)
    fig.update_layout(xaxis={'type': 'category'}, yaxis_nticks=len(list_clusters), xaxis_nticks=len(trans_log))
    fig.update_xaxes(side="top", autorange=False, constrain="range")
    obj.heatmaps[index] = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

# terminar de montar o heatmap, consertar o count_var() que nao vai dar pra usar em trans
# ver a questão de visualização de cases vs variantes (o que precisa mudar??)
