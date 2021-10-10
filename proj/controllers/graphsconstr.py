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
    verts = {i: act for i, act in enumerate(df['act seq'].explode().dropna().drop_duplicates())}
    print(verts)
    vertices = {i: rotulo(i) for i in verts.keys()}

    vertices[get_key('Start_Process', verts)] = 'ST'
    vertices[get_key('End_Process', verts)] = 'END'
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
    g.vs["color"] = ['#001c57' if v != 'ST' and v != 'END' else 'black' for v in vertices.values()]
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


def get_vert_ativ(vertices, edges_ids):
    return [v for v in vertices.keys() if v not in [v for edg in edges_ids if edg[0] == v or edg[1] == v]]


def view_config(g, vertices, edges_ids):
    def sizes(op1, op2, op3):
        return [op1 if v == get_key('ST', vertices) or v == get_key('END', vertices)
                else op2 if v not in get_vert_ativ(vertices, edges_ids) else op3 for v in vertices.keys()]

    vshape = ["circle" if edge == 'ST' or edge == 'END' else "rectangle" for edge in vertices.values()]
    laylist = list(g.layout_reingold_tilford(root=get_key('ST', vertices)))
    laylist[get_key('END', vertices)][0] = 0.0
    laylist[get_key('END', vertices)][1] += 1.0
    print(laylist)
    layout = laylist
    # (17, 3), (3, 4), (4, 7), (7, 5), (5, 10), (10, 9), (9, 2), (2, 1), (1, 1), (1, 2), (2, 9), (9, 10), (10, 11), (11, 16), (16, 6), (3, 5), (5, 4), (4, 8)

    return sizes(30, 25, 0), sizes(10, 15, 0), vshape, layout  # sizev, sizel, vshape, layoutgraph


def createimgtrans(c1, c2, nome):
    result = default.pdirectory[default.datafilter['arq']].copy()
    result['Sequence'] = result['Sequence'].apply(lambda x: 'Start_Process ' + x + ' End_Process')
    vertices, verts = get_vertices(result)

    # recebendo as diferenças entre o cluster c1 e o cluster c2. Lista do que tem em c1 que não tem em c2
    diffes = [(get_key(i, vertices), get_key(j, vertices)) for i, j in
              get_diffs(result, int(c1), int(c2), verts, vertices)]

    _, edlog_ids = get_edges(result, verts, vertices)
    edges_labels, edges_ids = get_edges(result[result.cluster == int(c1)], verts, vertices)

    # order_edges(edges_ids, vertices, edges_labels)
    ord_edges = list(set(edlog_ids) - set(edges_ids) - set(diffes)) + list(set(edges_ids) - set(diffes)) + diffes

    g = get_graph(vertices, ord_edges)

    # 'green' if edge.tuple[1] == get_key('END', vertices) else
    g.es['color'] = ['#ff0000' if edge.tuple in diffes else '#a1a1a1' if edge.tuple in edges_ids else 'white' for
                     edge in g.es]
    edwitdh = [3 if edge.tuple in diffes else 0 if edge.tuple not in edges_ids else 2 for edge in g.es]

    # setando configurações de visualização
    sizev, sizel, shapev, layout = view_config(g, vertices, edges_ids)
    vsub = {vertices[k]: verts[k] for k in vertices.keys()}


    g.vs[get_key('END', vertices)]["coordinates"] = (3, 4)
    plot(g, layout=layout, vertex_shape=shapev, vertex_label_color="white", vertex_size=sizev, edge_width=edwitdh,
         margin=[30, 30, 30, 30],
         vertex_label_size=sizel, bbox=(600, 540), target='proj/static/graphs/' + nome + '.png')

    return vsub


def get_diff_cluster(vertices, edges_ids, edges_ids2):
    dif1 = get_vert_ativ(vertices, edges_ids)  # nao tem no C1
    dif2 = get_vert_ativ(vertices, edges_ids2)  # nao tem no C2
    return [i for i in dif2 if i not in dif1 and vertices[i] != 'ST' and vertices[i] != 'END']


def createimgativs(c1, c2, nome):
    result = default.pdirectory[default.datafilter['arq']].copy()
    result['Sequence'] = result['Sequence'].apply(lambda x: 'Start_Process ' + x + ' End_Process')
    vertices, verts = get_vertices(result)
    _, edlog_ids = get_edges(result, verts, vertices)

    edges_labels, edges_ids = get_edges(result[result.cluster == int(c1)], verts, vertices)
    _, edges_ids2 = get_edges(result[result.cluster == int(c2)], verts, vertices)
    # order_edges(edges_ids, vertices, edges_labels)
    g = get_graph(vertices, list(set(edlog_ids) - set(edges_ids)) + edges_ids)
    g.es['color'] = ['white' if edge.tuple not in [(get_key(i, vertices), get_key(j, vertices)) for i, j in
                                                   edges_labels] else 'black' for edge in g.es]

    diffclus = get_diff_cluster(vertices, edges_ids, edges_ids2)  # procura atividades que tem em C2, mas não tem em C1
    print(diffclus)
    atcolor = ['black' if vertices[n] == 'ST' or vertices[n] == 'END' else '#f0a202' if n in diffclus and nome == "g1"
    else '#f27cc9' if n in diffclus and nome == "g2" else '#001c57' for n in vertices.keys()]

    lcolor = ['black' if n in get_diff_cluster(vertices, edges_ids, edges_ids2) else 'white' for n in vertices.keys()]
    sizev, sizel, shapev, layout = view_config(g, vertices, edges_ids)
    vsub = {vertices[k]: verts[k] for k in vertices.keys()}
    diffclus = [vertices[k] for k in diffclus]
    plot(g, layout=layout, vertex_shape=shapev, vertex_label_color=lcolor, vertex_size=sizev, edge_width=2,
         margin=[30, 30, 30, 30], vertex_label_size=sizel, vertex_color=atcolor, bbox=(600, 540), keep_aspect_ratio=False,
         target='proj/static/graphs/' + nome + '.png')

    return vsub, diffclus
