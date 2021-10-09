from flask import render_template, url_for, request, redirect
from werkzeug.utils import secure_filename
from proj.controllers import graphsconstr
from proj import app
from proj.models.diretorio import Directory, ExibitionFilter

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
    imageboost = False
    c1 = -1
    c2 = -1
    diffclus = {'g1': [], 'g2':[]}
    vsub_c1 = {}
    vsub_c2 = {}
    umcsv = Directory()
    filterchoice = ExibitionFilter()
    if umcsv.validate_on_submit():
        if len(checkxtension(umcsv.entry.data)) > 0:
            print("TEM QUE SER CSV, GATA")
            return redirect(request.url)
        else:
            if len(umcsv.entry.data) > 0:
                for file in umcsv.entry.data:
                    pdirectory[str(file.filename)] = pd.read_csv(file)
                    datafilter['arq'] = str(file.filename)
                datafilter['cbxlist'] = listcluster(datafilter['arq'])
            filterchoice.updatecombo(datafilter['cbxlist'])

    if filterchoice.validate_on_submit() and len(datafilter['arq']) > 0:
        imageboost = False
        # if filterchoice.checkbxgraph.data:  # exibindo grafos

        c1 = filterchoice.combobx.data
        c2 = filterchoice.combobx2.data
        if c1 != -1 and c2 != -1:
            imageboost = True
            if filterchoice.radialcircle.data == 'activ':  # exibindo atividades
                try:
                    vsub_c1, diffclus['g1'] = graphsconstr.createimgativs(c1, c2, "g1")
                    vsub_c2, diffclus['g2'] = graphsconstr.createimgativs(c2, c1, "g2")
                except Exception as e:
                    print("OLHA O ERRO: ", e)
                    imageboost = False
            else:  # exibindo transições
                try:

                    vsub_c1 = graphsconstr.createimgtrans(c1, c2, "g1")
                    vsub_c2 = graphsconstr.createimgtrans(c2, c1, "g2")
                except Exception as e:
                    print("OLHA O ERRO: ", e)
                    imageboost = False
        filterchoice.updatecombo(datafilter['cbxlist'])
    return render_template("test.html", umcsv=umcsv, filterchoice=filterchoice, imageboost=imageboost,
                           c1=c1, c2=c2, filename=datafilter['arq'], vsub_c1=vsub_c1, vsub_c2=vsub_c2, diffclus=diffclus)