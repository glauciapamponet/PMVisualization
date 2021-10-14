from flask import render_template, url_for, request, redirect
from proj.controllers import graphsconstr as gc
from proj import app
from proj.models.diretorio import FileChoice, ExibitionFilter, FilterColect
import pandas as pd

app.config['SECRET_KEY'] = 'giovanna-e-um-cinco'
FILEALLOWED = ['.csv']
datafilter = {'arq': 'No file chosen', 'cbxlist': []}
pdirectory = {}


def checkxtension(datas):
    return [files.filename for files in datas if files.filename[-4:] not in FILEALLOWED]


def listcluster(arqname):
    return list(set(pdirectory[arqname]['cluster']))


@app.route("/", methods=["GET", "POST"])
def test():
    umcsv = FileChoice()
    filterchoice = ExibitionFilter()
    colect = FilterColect()
    umcsv.filename = datafilter['arq']
    if umcsv.validate_on_submit():
        print(umcsv.filename)
        if len(checkxtension(umcsv.entry.data)) > 0:
            print("ONLY CSV")
            return redirect(request.url)
        else:
            if len(umcsv.entry.data) > 0:
                for file in umcsv.entry.data:
                    pdirectory[str(file.filename)] = pd.read_csv(file)
                    datafilter['arq'] = str(file.filename)
                datafilter['cbxlist'] = listcluster(datafilter['arq'])
                umcsv.filename = datafilter['arq']
            print(umcsv.filename)
            # filterchoice.updatecombo(datafilter['cbxlist']) # para combobox que não está funcionando
    if filterchoice.validate_on_submit() and len(datafilter['arq']) > 0:
        colect.empty_diffs()
        colect.imageboost = False
        # if filterchoice.checkbxgraph.data:  # exibindo grafos
        colect.c1 = [(val) for val in filterchoice.combobx.data.split(',')]
        colect.c2 = [(val) for val in filterchoice.combobx2.data.split(',')]
        # if -1 in c1 or -1 in c2: # desativar os combos temporariamente
        colect.imageboost = True
        if filterchoice.radialcircle.data == 'activ':  # exibindo atividades
            try:
                colect.vsub_c1, colect.diffclus['g1'] = gc.createimgativs(colect.c1, colect.c2, "g1")
                _, colect.diffclus['g2'] = gc.createimgativs(colect.c2, colect.c1, "g2")
            except Exception as e:
                print("OLHA O ERRO: ", e)
                colect.imageboost = False
        else:  # exibindo transições
            try:
                colect.vsub_c1 = gc.createimgtrans(colect.c1, colect.c2, "g1")
                _ = gc.createimgtrans(colect.c2, colect.c1, "g2")
            except Exception as e:
                print("OLHA O ERRO: ", e)
                colect.imageboost = False
        # filterchoice.updatecombo(datafilter['cbxlist']) # para combobox que nao está funcionando
    else:
        print(filterchoice.errors)
        if len(datafilter['arq']) == 0: umcsv.filename = 'No file chosen'
    return render_template("test.html", umcsv=umcsv, filterchoice=filterchoice, colect=colect, c1=str(colect.c1)[1:-1],
                           c2=str(colect.c2)[1:-1])


#, imageboost=imageboost, c1=str(c1)[1:-1], c2=str(c2)[1:-1], filename=datafilter['arq'], vsub_c1=vsub_c1, vsub_c2=vsub_c2, diffclus=diffclus