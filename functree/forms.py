import wtforms, flask_wtf, flask_wtf.file
from functree import app, models


class BasicForm(flask_wtf.FlaskForm):
    _tree_sources = models.Tree.objects.aggregate(
        {'$group': {'_id': '$source'}}
    )
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired(),
    ])
    target = wtforms.SelectField('Database', choices=[
        (tree_source['_id'],) * 2 for tree_source in _tree_sources
    ])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.DataRequired(),
        wtforms.validators.Length(max=50)
    ])
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")')
    submit = wtforms.SubmitField('Submit')


class MCRForm(flask_wtf.FlaskForm):
    _definition_sources = models.Definition.objects.aggregate(
        {'$group': {'_id': '$source'}}
    )
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired(),
    ])
    target = wtforms.SelectField('Database', choices=[
        (definition_source['_id'],) * 2 for definition_source in _definition_sources
    ])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.DataRequired(),
        wtforms.validators.Length(max=50)
    ])
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")')
    submit = wtforms.SubmitField('Submit')


class JSONUploadForm(flask_wtf.FlaskForm):
    _tree_sources = models.Tree.objects.aggregate(
        {'$group': {'_id': '$source'}}
    )
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired(),
    ])
    target = wtforms.SelectField('Database', choices=[
        (tree_source['_id'],) * 2 for tree_source in _tree_sources
    ])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.DataRequired(),
        wtforms.validators.Length(max=50)
    ])
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")')
    submit = wtforms.SubmitField('Submit')
