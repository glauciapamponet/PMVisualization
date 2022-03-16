# arquivo responsável pela consetrução da view da ferramenta em flask.
# possui apenas uma view onde se realiza o armazenamento do arquivo .csv,
# a chamada dos métodos responsáveis pela filtragem dos dados e geração
# da visualização na ferramenta.

from flask import render_template, request, redirect
from proj.controllers import graphsconstr as gc
from proj.controllers import dashb as dsb
from proj import app
from proj.models.diretorio import FileChoice, ExibitionFilter, FilterColect
import pandas as pd

app.config['SECRET_KEY'] = 'giovanna-e-um-cinco'
FILEALLOWED = ['.csv']
datafilter = {'arq': 'No file chosen', 'cbxlist': []}
pdirectory = []
vsub = {}


# montagem das atividadades mostradas na área de Activities List
def get_act(v):
    abrev, name = gc.get_vertices(pdirectory[0].copy())
    v = {abrev[i]: name[i] for i in name.keys()}


# checagem da extensão que está sendo carregada na ferramenta. A única extensão
# permitida na lista FILEALLOWED é .csv
def checkxtension(datas):
    return [files.filename for files in datas if files.filename[-4:] not in FILEALLOWED]


# coleta da lista de clusters do .csv carregado
def listcluster():
    return list(set(pdirectory[0]['cluster']))


# view da ferramenta
@app.route("/", methods=["GET", "POST"])
def test():
    umcsv = FileChoice()
    filterchoice = ExibitionFilter()
    colect = FilterColect()
    umcsv.filename = datafilter['arq']
    if umcsv.validate_on_submit():
        if len(checkxtension(umcsv.entry.data)) > 0:
            print("ONLY CSV")  # não é csv, tem que mandar mensagem de erro
            return redirect(request.url)
        else:
            if len(umcsv.entry.data) > 0:
                pdirectory.clear()
                for file in umcsv.entry.data:
                    pdirectory.append(pd.read_csv(file))
                    datafilter['arq'] = str(file.filename)
                datafilter['cbxlist'] = listcluster()
                colect = FilterColect()  # upagem de novo file zera o objeto
                umcsv.filename = datafilter['arq']
                colect.vsub, colect.datalog = dsb.get_datalog()
            filterchoice.updatecombo(datafilter['cbxlist'])
    if filterchoice.validate_on_submit() and len(datafilter['arq']) > 0:
        colect.get_act(pdirectory[0])
        colect.empty_diffs()
        colect.imageboost = False
        try:
            colect.c1 = [int(val) for val in set(filterchoice.combobx.data)]
            colect.c2 = [int(val) for val in set(filterchoice.combobx2.data)]
        except:
            colect.c1 = [val for val in set(filterchoice.combobx.data)]
            colect.c2 = [val for val in set(filterchoice.combobx2.data)]
        if not (any(item in colect.c1 for item in colect.c2)):
            try:
                dsb.get_metrics(colect, colect.c1, 0)
                dsb.get_metrics(colect, colect.c2, 1)
            except Exception as e:
                print("Erro: ", e)
            if filterchoice.checkbxgraph.data:  # exibindo grafos
                colect.imageboost = True
                if filterchoice.radialcircle.data == 'activ':  # exibindo atividades
                    try:
                        colect.diffclus['g1'] = gc.createimgativs(colect.c1, colect.c2, "g1")
                        colect.diffclus['g2'] = gc.createimgativs(colect.c2, colect.c1, "g2")
                    except Exception as e:
                        print("OLHA O ERRO: ", e)
                        colect.imageboost = False
                else:  # exibindo transições
                    try:
                        gc.createimgtrans(colect.c1, colect.c2, "g1")
                        gc.createimgtrans(colect.c2, colect.c1, "g2")
                    except Exception as e:
                        print("OLHA O ERRO: ", e)
                        colect.imageboost = False
            if filterchoice.checkbxother.data:  # exibindo other
                colect.graphothers = True
                try:
                    dsb.choice_view(colect, filterchoice.radialcircle.data)
                except Exception as e:
                    print("ERRO: ", e)
                    colect.graphothers = False
            filterchoice.updatecombo(datafilter['cbxlist'])  # para combobox que nao está funcionando
        else:
            colect.clean_data()
        _, colect.datalog = dsb.get_datalog()
    else:
        print(filterchoice.errors)
        if len(datafilter['arq']) == 0: umcsv.filename = 'No file chosen'

    return render_template("page.html", umcsv=umcsv, filterchoice=filterchoice, colect=colect, c1=str(colect.c1)[1:-1],
                           c2=str(colect.c2)[1:-1])
