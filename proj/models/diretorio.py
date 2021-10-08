from flask_wtf import FlaskForm
from wtforms import MultipleFileField, SelectField, RadioField, BooleanField, SubmitField
from flask_wtf.file import FileAllowed, FileRequired


class Directory(FlaskForm):
    entry = MultipleFileField('CSVfile', validators=[FileAllowed(['csv', 'CSVs only!'])], render_kw={'multiple': True})


class ExibitionFilter(FlaskForm):
    combobx = SelectField('Clusters', choices=['choose'])
    combobx2 = SelectField('Clusters2', choices=['choose'])
    checkbxgraph = BooleanField("Graphs")
    checkbxother = BooleanField("Others")
    radialcircle = RadioField('Label', choices=[('activ', 'Activities'), ('trans', 'Transitions')])
    submit = SubmitField('OK')

    def updatecombo(self, clusterlist):
        self.combobx.choices = ['choose'] + clusterlist
        self.combobx2.choices = ['choose'] + clusterlist
