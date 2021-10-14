from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SelectMultipleField, RadioField, BooleanField, SubmitField, StringField, \
    validators
from flask_wtf.file import FileAllowed, FileRequired


class FileChoice(FlaskForm):
    entry = MultipleFileField('CSVfile', validators=[FileAllowed(['csv', 'CSVs only!'])], render_kw={'multiple': True})
    filename = 'No file chosen'

    def chose_file(self, name):
        self.filename = name


# class Directory():


class ExibitionFilter(FlaskForm):
    # combobx = SelectField('Clusters', choices=[('-1', 'choose')])
    # combobx2 = SelectField('Clusters2', choices=[('-1', 'choose')])
    combobx = StringField(u'Comp1', [validators.required(), validators.length(max=15)])
    combobx2 = StringField(u'Comp2', [validators.required(), validators.length(max=15)])
    checkbxgraph = BooleanField("Graphs")
    checkbxother = BooleanField("Others")
    radialcircle = RadioField('Label', choices=[('activ', 'Activities'), ('trans', 'Transitions')])
    submit = SubmitField('OK')

    def updatecombo(self, clusterlist):
        for i in clusterlist:
            self.combobx.choices.append((i, i))
            self.combobx2.choices.append((i, i))


class FilterColect():
    imgboost = False
    c1 = []
    c2 = []
    diffclus = {'g1': [], 'g2': []}
    vsub_c1 = {}
    vsub_c2 = {}

    def empty_diffs(self):
        self.diffclus['g1'] = []
        self.diffclus['g2'] = []
