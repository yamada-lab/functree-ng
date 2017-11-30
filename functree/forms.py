import wtforms, flask_wtf, flask_wtf.file
from functree import models


class BasicMappingForm(flask_wtf.FlaskForm):
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired(),
    ])
    color_file = flask_wtf.file.FileField('Color file')
    target = wtforms.SelectField('Database', choices=[])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.DataRequired(),
        wtforms.validators.Length(max=50)
    ])
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")', default=True)
    submit = wtforms.SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(BasicMappingForm, self).__init__(*args, **kwargs)
        targets = models.Tree.objects.aggregate(
            {'$group': {'_id': '$source'}}
        )
        self.target.choices = [(target['_id'],) * 2 for target in targets]


class ModuleCoverageForm(flask_wtf.FlaskForm):
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired(),
    ])
    color_file = flask_wtf.file.FileField('Color file')
    target = wtforms.SelectField('Database', choices=[])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.DataRequired(),
        wtforms.validators.Length(max=50)
    ])
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")', default=True)
    submit = wtforms.SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(ModuleCoverageForm, self).__init__(*args, **kwargs)
        targets = models.Definition.objects.aggregate(
            {'$group': {'_id': '$source'}}
        )
        self.target.choices = [(target['_id'],) * 2 for target in targets]


class DirectMappingForm(flask_wtf.FlaskForm):
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired(),
    ])
    color_file = flask_wtf.file.FileField('Color file')
    target = wtforms.SelectField('Database', choices=[])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.DataRequired(),
        wtforms.validators.Length(max=50)
    ])
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")', default=True)
    submit = wtforms.SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(DirectMappingForm, self).__init__(*args, **kwargs)
        targets = models.Tree.objects.aggregate(
            {'$group': {'_id': '$source'}}
        )
        self.target.choices = [(target['_id'],) * 2 for target in targets]


class JSONUploadForm(flask_wtf.FlaskForm):
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired(),
    ])
    target = wtforms.SelectField('Database', choices=[])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.DataRequired(),
        wtforms.validators.Length(max=50)
    ])
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")', default=True)
    submit = wtforms.SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(JSONUploadForm, self).__init__(*args, **kwargs)
        targets = models.Tree.objects.aggregate(
            {'$group': {'_id': '$source'}}
        )
        self.target.choices = [(target['_id'],) * 2 for target in targets]
