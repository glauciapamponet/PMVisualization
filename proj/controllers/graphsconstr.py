from igraph import Graph, plot
from proj.controllers import default as dft


def get_key(val, dictio):
    for key, value in dictio.items():
        if val == value:
            return key
    return "none"


def rotulo(n):
    i = -1
    if n < 26: return chr(n + 65)
    while n > 25:
        n -= 26
        i += 1
    return chr(i + 65) + chr(n % 26 + 65)


def get_edglog(c1, c2):
    result = dft.pdirectory[0].copy()
    result['Sequence'] = result['Sequence'].apply(lambda x: 'Start_Process ' + x + ' End_Process')
    vert, verts = get_vertices(result)
    vertices = {'conv': {vert[i]: verts[i] for i in vert.keys()},  # abreviação: nome
                'orig': vert}
    edges = {
        'log': get_edges(result, verts, vert),
        'c1': get_edges(result[result.cluster.isin(c1)], verts, vert),
        'c2': get_edges(result[result.cluster.isin(c2)], verts, vert)
    }
    return result, vertices, edges


def get_vertices(df, seq_df_colname='Sequence'):
    df['act seq'] = df[seq_df_colname].apply(lambda x: x.split(' '))
    verts = {i: act for i, act in enumerate(df['act seq'].explode().dropna().drop_duplicates())}
    vertices = {i: rotulo(i) for i in verts.keys()}

    vertices[get_key('Start_Process', verts)] = 'ST'
    vertices[get_key('End_Process', verts)] = 'END'
    return vertices, verts


def get_edges(df, verts, vertices):
    df['transitions'] = df['act seq'].apply(lambda x: [(x[i - 1], x[i]) for i in range(1, len(x))])
    labels = list(df['transitions'].explode().dropna().drop_duplicates())
    edges_ids = [(get_key(i, verts), get_key(j, verts)) for i, j in labels]
    return edges_ids


colors = ['#6c0303']  # bordô do PET
edges_colors = ['#ff0077', '#007bff', '#ff8c00', '#00d43f']  # rosa, azul, amarelo, verde


def get_graph(vertices, edges):
    g = Graph(directed=True)
    g.add_vertices(vertices.keys())
    g.vs["label"] = list(vertices.values())
    g.vs["color"] = ['#001c57' if v != 'ST' and v != 'END' else 'black' for v in vertices.values()]
    g.add_edges(edges)
    layout = g.layout_reingold_tilford(root=[0])
    return g


def get_vert_ativ(vertices, edges_ids):
    return [v for v in vertices.keys() if v not in [v for edg in edges_ids if edg[0] == v or edg[1] == v]]


def paint_edges(g, color1, color2, edgelist):
    g.es['color'] = [color1 if edge.tuple in edgelist else color2 for edge in g.es]


def view_config(g, vertices, edges_ids):
    def sizes(op1, op2, op3):
        return [op1 if v == get_key('ST', vertices) or v == get_key('END', vertices)
                else op2 if v not in get_vert_ativ(vertices, edges_ids) else op3 for v in vertices.keys()]

    vshape = ["circle" if edge == 'ST' or edge == 'END' else "rectangle" for edge in vertices.values()]
    laylist = list(g.layout_reingold_tilford(root=get_key('ST', vertices)))
    laylist[get_key('END', vertices)][0] = 0.0
    bigger = laylist[get_key('END', vertices)][1]
    for a in laylist:
        if a[1] > bigger:
            bigger = a[1]
    laylist[get_key('END', vertices)][1] = bigger + 1.0
    layout = laylist

    return sizes(30, 25, 0), sizes(10, 15, 0), vshape, layout  # sizev, sizel, vshape, layoutgraph


def createimgtrans(c1, c2, nome):
    result, vertices, edges = get_edglog(c1, c2)

    diffes = list(set(edges['c1']) - set(edges['c2']))  # recebendo as diferenças do que tem em c1 e não em c2.
    ord_edges = list(set(edges['log']) - set(edges['c1']) - set(diffes)) + list(set(edges['c1']) - set(diffes)) + diffes

    g = get_graph(vertices['orig'], ord_edges)
    g.es['color'] = ['#ff0000' if edge.tuple in diffes else '#a1a1a1' if edge.tuple in edges['c1']
                    else 'white' for edge in g.es]

    # setando configurações de visualização

    sizev, sizel, shapev, layout = view_config(g, vertices['orig'], edges['c1'])

    edwitdh = [3 if edge.tuple in diffes else 0 if edge.tuple not in edges['c1'] else 2 for edge in g.es]
    plot(g, layout=layout, vertex_shape=shapev, vertex_label_color="white", vertex_size=sizev, edge_width=edwitdh,
         margin=[30, 40, 40, 30], vertex_label_size=sizel, bbox=(665, 665), target='proj/static/graphs/'+nome+'.png')



def get_diff_cluster(vertices, edges_ids, edges_ids2):
    dif1 = get_vert_ativ(vertices, edges_ids)  # nao tem no C1
    dif2 = get_vert_ativ(vertices, edges_ids2)  # nao tem no C2
    return [i for i in dif2 if i not in dif1 and vertices[i] != 'ST' and vertices[i] != 'END']


def createimgativs(c1, c2, nome):  # c2 são dois clusters
    result, vertices, edges = get_edglog(c1, c2)

    g = get_graph(vertices['orig'], list(set(edges['log']) - set(edges['c1'])) + edges['c1'])
    g.es['color'] = ['black' if edge.tuple in edges['c1'] else 'white' for edge in g.es]

    diffclus = get_diff_cluster(vertices['orig'], edges['c1'], edges['c2'])  # procura atividades que tem em C2, mas não tem em C1
    atcolor = ['black' if vertices['orig'][n] == 'ST' or vertices['orig'][n] == 'END' else '#f0a202' if n in diffclus and nome == "g1"
    else '#f27cc9' if n in diffclus and nome == "g2" else '#001c57' for n in vertices['orig'].keys()]

    lcolor = ['black' if n in get_diff_cluster(vertices['orig'], edges['c1'], edges['c2']) else 'white' for n in vertices['orig'].keys()]
    sizev, sizel, shapev, layout = view_config(g, vertices['orig'], edges['c1'])
    diffclus = [vertices['orig'][k] for k in diffclus]
    plot(g, layout=layout, vertex_shape=shapev, vertex_label_color=lcolor, vertex_size=sizev, edge_width=2,
         margin=[30, 40, 40, 30], vertex_label_size=sizel, vertex_color=atcolor, bbox=(665, 665),
         keep_aspect_ratio=False, target='proj/static/graphs/' + nome + '.png')

    return diffclus
