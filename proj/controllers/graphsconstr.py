from igraph import Graph, plot
import pandas as pd
from proj.controllers import default


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


def get_vertices(df, seq_df_colname='Sequence'):
    df['act seq'] = df[seq_df_colname].apply(lambda x: x.split(' '))
    verts = {i: act for i, act in enumerate(df['act seq'].explode().dropna().drop_duplicates().sort_values())}
    vertices = {i: rotulo(i) for i in verts.keys()}
    #print(vertices, verts)
    vertices[get_key('ST', verts)] = 'ST'
    vertices[get_key('END1', verts)] = 'END1'
    vertices[get_key('END2', verts)] = 'END2'
    vertices[get_key('END3', verts)] = 'END3'
    return vertices, verts


def get_edges(df, verts, vertices):
    df['transitions'] = df['act seq'].apply(lambda x: [(x[i - 1], x[i]) for i in range(1, len(x))])
    labels = list(df['transitions'].explode().dropna().drop_duplicates())
    edges_ids = [(get_key(i, verts), get_key(j, verts)) for i, j in labels]
    edges_labels = [(vertices[get_key(i, verts)], vertices[get_key(j, verts)]) for i, j in labels]

    return edges_labels, edges_ids


def order_edges(edges_ids, vertices, edges_labels):
    edges_ids.insert(0, (get_key('ST', vertices), edges_ids[0][0]))
    edges_ids.append((edges_ids[-1][1], get_key('END', vertices)))
    edges_labels.insert(0, ('ST', edges_labels[0][0]))
    edges_labels.append((edges_labels[-1][1], 'END'))


colors = ['#6c0303']  # bordô do PET
edges_colors = ['#ff0077', '#007bff', '#ff8c00', '#00d43f']  # rosa, azul, amarelo, verde


def get_graph(vertices, edges):
    g = Graph(directed=True)
    g.add_vertices(vertices.keys())
    g.vs["label"] = list(vertices.values())
    g.vs["color"] = ['#001c57' if v.find('ST') == -1 and v.find('END') == -1 else 'black' for v in vertices.values()]
    g.es["color"] = ['black']
    g.add_edges(edges)
    layout = g.layout_reingold_tilford(root=[0])
    return g


def get_diffs(result, g_id1, g_id2, verts, vertices):
    def get_group_edges(g_id):
        group = result[result['cluster'] == g_id]
        edges_labels, _ = get_edges(group, verts, vertices)
        return edges_labels

    edges_i = get_group_edges(g_id1)
    edges_j = get_group_edges(g_id2)
    diff1 = list(set(edges_i) - set(edges_j))  # transicoes que tem no i e nao tem no j
    # diff2 = list(set(edges_j) - set(edges_i))  # transicoes que tem no j e nao tem no i
    return diff1


def find_end_graph(edges_ids, vertices):
    cnt_end = 1
    cnt_st = 1
    for edg in edges_ids:
        if edg[1] not in [arst[0] for arst in edges_ids]:
            vertices[edg[1]] = 'END' + str(cnt_end) if cnt_end > 1 else 'END'
            cnt_end += 1
        if edg[0] not in [arst[1] for arst in edges_ids]:
            vertices[edg[0]] = 'ST' + str(cnt_st) if cnt_st > 1 else 'ST'
            cnt_st += 1



def get_vert_ativ(vertices, edges_ids):
    return [v for v in vertices.keys() if v not in [v for edg in edges_ids if edg[0] == v or edg[1] == v]]


def view_config(g, vertices, edges_ids):
    def sizes(op1, op2, op3):
        vertsin = get_vert_ativ(vertices, edges_ids)
        return [op1 if v.find('ST') != -1 or v.find('END') != -1 and get_key(v, vertices) not in vertsin
                else op2 if get_key(v, vertices) not in vertsin else op3 for v in vertices.values()]

    vshape = ["circle" if edge.find('ST') != -1 or edge.find('END') != -1 else "rectangle" for edge in vertices.values()]
    layout = g.layout_reingold_tilford(root=[edges_ids[0][0]])

    return sizes(30, 25, 0), sizes(10, 15, 0), vshape, layout  # sizev, sizel, vshape, layoutgraph


def createimgtrans(c1, c2, nome):
    result = default.pdirectory[default.datafilter['arq']].copy()
    #result['Sequence'] = result['Sequence'].apply(lambda x: 'Start_Process ' + x + ' End_Process')
    vertices, verts = get_vertices(result)

    # recebendo as diferenças entre o cluster c1 e o cluster c2. Lista do que tem em c1 que não tem em c2
    diffes = get_diffs(result, int(c1), int(c2), verts, vertices)

    _, edlog_ids = get_edges(result, verts, vertices)
    edges_labels, edges_ids = get_edges(result[result.cluster == int(c1)], verts, vertices)
    #find_end_graph(edges_ids, vertices)
    # order_edges(edges_ids, vertices, edges_labels)
    ord_edges = list(set(edlog_ids) - set(edges_ids)) + edges_ids
    g = get_graph(vertices, list(set(ord_edges) - set(edges_ids)) + edges_ids)
    g.es['color'] = ['#ff0000' if edge.tuple in [(get_key(i, vertices), get_key(j, vertices)) for i, j in
                                                 diffes] else 'white' if edge.tuple not in edges_ids else '#a1a1a1' for
                     edge in g.es]
    edwitdh = [3 if edge.tuple in [(get_key(i, vertices), get_key(j, vertices)) for i, j in
                                                 diffes] else 0 if edge.tuple not in edges_ids else 2 for
                     edge in g.es]

    # setando configurações de visualização
    sizev, sizel, shapev, layout = view_config(g, vertices, edges_ids)
    vsub = {vertices[k]: verts[k] for k in vertices.keys()}
    plot(g, layout=layout, vertex_shape=shapev, vertex_label_color="white", vertex_size=sizev, edge_width=edwitdh, margin=60,
         vertex_label_size=sizel, bbox=(600, 540), target='proj/static/graphs/' + nome + '.png')

    return vsub


def get_diff_cluster(vertices, edges_ids, edges_ids2):
    dif1 = get_vert_ativ(vertices, edges_ids)  # nao tem no C1
    dif2 = get_vert_ativ(vertices, edges_ids2)  # nao tem no C2
    return [i for i in dif2 if i not in dif1 and vertices[i] != 'ST' and vertices[i].find('END') == -1]


def createimgativs(c1, c2, nome):
    result = default.pdirectory[default.datafilter['arq']].copy()
    #result['Sequence'] = result['Sequence'].apply(lambda x: 'Start_Process ' + x + ' End_Process')
    vertices, verts = get_vertices(result)
    _, edlog_ids = get_edges(result, verts, vertices)

    edges_labels, edges_ids = get_edges(result[result.cluster == int(c1)], verts, vertices)
    _, edges_ids2 = get_edges(result[result.cluster == int(c2)], verts, vertices)
    # order_edges(edges_ids, vertices, edges_labels)
    #find_end_graph(edges_ids, vertices)
    g = get_graph(vertices, list(set(edlog_ids) - set(edges_ids)) + edges_ids)
    g.es['color'] = ['white' if edge.tuple not in edges_ids else 'black' for edge in g.es]

    diffclus = get_diff_cluster(vertices, edges_ids, edges_ids2) # procura atividades que tem em C2, mas não tem em C1
    atcolor = ['black' if vertices[n].find('ST') != -1 or vertices[n].find('END') != -1 else '#f0a202' if n in diffclus and nome == "g1"
               else '#f27cc9' if n in diffclus and nome == "g2" else '#001c57' for n in vertices.keys()]

    lcolor = ['black' if n in get_diff_cluster(vertices, edges_ids, edges_ids2) else 'white' for n in vertices.keys()]
    sizev, sizel, shapev, layout = view_config(g, vertices, edges_ids)
    vsub = {vertices[k]: verts[k] for k in vertices.keys()}
    diffclus = [vertices[k] for k in diffclus]
    print(diffclus)
    plot(g, layout=layout, vertex_shape=shapev, vertex_label_color=lcolor, vertex_size=sizev, edge_width=2, margin=50,
         vertex_label_size=sizel, vertex_color=atcolor, bbox=(600, 540), keep_aspect_ratio=False, target='proj/static/graphs/' + nome + '.png')

    return vsub, diffclus
