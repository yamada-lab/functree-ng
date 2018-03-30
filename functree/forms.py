import wtforms, flask_wtf, flask_wtf.file
from functree import models


class MappingForm(flask_wtf.FlaskForm):
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired()
    ])
    color_file = flask_wtf.file.FileField('Color file (Optional)')
    target = wtforms.SelectField('Database', choices=[])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.Length(max=50)
    ])

    modulecoverage = wtforms.BooleanField('Compute module coverage', default=True)
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")', default=True)
    submit = wtforms.SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(MappingForm, self).__init__(*args, **kwargs)
        targets = models.Tree.objects.aggregate(
            {'$group': {'_id': '$source'}}
        )
        self.target.choices = [(target['_id'],) * 2 for target in targets]

class ComparisonForm(flask_wtf.FlaskForm):
    input_file1 = flask_wtf.file.FileField('Input file #1', validators=[
        flask_wtf.file.FileRequired()
    ])
    input_file2 = flask_wtf.file.FileField('Input file #2', validators=[
        flask_wtf.file.FileRequired()
    ])
    color_file = flask_wtf.file.FileField('Color file (Optional)')
    target = wtforms.SelectField('Database', choices=[])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.Length(max=50)
    ])
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")', default=True)
    submit = wtforms.SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ComparisonForm, self).__init__(*args, **kwargs)
        targets = models.Definition.objects.aggregate(
            {'$group': {'_id': '$source'}}
        )
        self.target.choices = [(target['_id'],) * 2 for target in targets]


class DisplayForm(flask_wtf.FlaskForm):
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired()
    ])
    color_file = flask_wtf.file.FileField('Color file (Optional)')
    target = wtforms.SelectField('Database', choices=[])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.Length(max=50)
    ])
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")', default=True)
    submit = wtforms.SubmitField('Submit')
 
    def __init__(self, *args, **kwargs):
        super(DisplayForm, self).__init__(*args, **kwargs)
        targets = models.Tree.objects.aggregate(
            {'$group': {'_id': '$source'}}
        )
        self.target.choices = [(target['_id'],) * 2 for target in targets]
