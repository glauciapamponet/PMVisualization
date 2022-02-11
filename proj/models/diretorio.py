from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SelectMultipleField, RadioField, BooleanField, SubmitField
from proj.controllers import graphsconstr as gc
from flask_wtf.file import FileAllowed


class FileChoice(FlaskForm):
    entry = MultipleFileField('CSVfile', validators=[FileAllowed(['csv', 'CSVs only!'])], render_kw={'multiple': True})
    filename = 'No file chosen'

    def chose_file(self, name):
        self.filename = name


class NonValidatingSelectMultipleField(SelectMultipleField):
    """
    Attempt to make an open ended select multiple field that can accept dynamic
    choices added by the browser.
    """
    def pre_validate(self, form):
        pass


class ExibitionFilter(FlaskForm):
    combobx = NonValidatingSelectMultipleField('Clusters', choices=[('-1', 'choose')], validate_choice=False)
    combobx2 = NonValidatingSelectMultipleField('Clusters', choices=[('-1', 'choose')], validate_choice=False)
    checkbxgraph = BooleanField("Graphs")
    checkbxother = BooleanField("Heatmaps")
    radialcircle = RadioField('Label', choices=[('activ', 'Activities'), ('trans', 'Transitions')])
    submit = SubmitField('OK')

    def updatecombo(self, clusterlist):
        self.combobx.choices = [(i, i) for i in clusterlist]
        self.combobx2.choices = [(i, i) for i in clusterlist]


class FilterColect():
    def __init__(self):
        self.graphothers = False
        self.imgboost = False
        self.c1 = []
        self.c2 = []
        self.diffclus = {'g1': [], 'g2': []}
        self.vsub = {}
        self.activ = [{'min': 0, 'avg': 0, 'max': 0}, {'min': 0, 'avg': 0, 'max': 0}]
        self.varCount = [0, 0]
        self.evt = [{'min': 0, 'avg': 0, 'max': 0}, {'min': 0, 'avg': 0, 'max': 0}]
        self.totalCases = [0, 0]
        self.totalEvnts = [0, 0]
        self.heatmaps = [None, None]

    def clean_data(self):
        self.graphothers = False
        self.imgboost = False
        self.c1 = []
        self.c2 = []
        self.diffclus = {'g1': [], 'g2': []}
        self.activ = [{'min': 0, 'avg': 0, 'max': 0}, {'min': 0, 'avg': 0, 'max': 0}]
        self.varCount = [0, 0]
        self.evt = [{'min': 0, 'avg': 0, 'max': 0}, {'min': 0, 'avg': 0, 'max': 0}]
        self.totalCases = [0, 0]
        self.totalEvnts = [0, 0]
        self.heatmaps = [None, None]

    def get_activs(self):
        return self.vsub

    def get_act(self, df):
        abrev, name = gc.get_vertices(df.copy())
        self.vsub = {abrev[i]: name[i] for i in name.keys()}

    def empty_diffs(self):
        self.diffclus['g1'] = []
        self.diffclus['g2'] = []
