from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SelectMultipleField, RadioField, BooleanField, SubmitField, StringField, \
    validators
from flask_wtf.file import FileAllowed, FileRequired


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
    checkbxother = BooleanField("Others")
    radialcircle = RadioField('Label', choices=[('activ', 'Activities'), ('trans', 'Transitions')])
    submit = SubmitField('OK')

    def updatecombo(self, clusterlist):
        self.combobx.choices = [(i, i) for i in clusterlist]
        self.combobx2.choices = [(i, i) for i in clusterlist]


class FilterColect():
    graphothers = False
    imgboost = False
    c1 = []
    c2 = []
    diffclus = {'g1': [], 'g2': []}
    vsub_c1 = {}
    vsub_c2 = {}
    activ = [{'min': 0, 'avg': 0, 'max': 0}, {'min': 0, 'avg': 0, 'max': 0}]
    varCount = [0, 0]
    evt = [{'min': 0, 'avg': 0, 'max': 0}, {'min': 0, 'avg': 0, 'max': 0}]
    totalCases = [0, 0]
    totalEvnts = [0, 0]
    heatmaps = [None, None]



    def empty_diffs(self):
        self.diffclus['g1'] = []
        self.diffclus['g2'] = []
