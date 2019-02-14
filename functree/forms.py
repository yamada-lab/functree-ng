import wtforms, flask_wtf, flask_wtf.file
from functree import models

def get_targets():
    '''
    Returns the db targets with KEGG at the top 
    '''
    targets = models.Tree.objects.only('source', 'description')
    targets_choices = [(target['source'], target['source'] + ": " + target['description'])  for target in targets]
    return list(filter(lambda x: x[0] == "KEGG", targets_choices)) +  list(filter(lambda x: x[0] != "KEGG", targets_choices))

class MappingForm(flask_wtf.FlaskForm):
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired()
    ])
    color_file = flask_wtf.file.FileField('Color file (Optional)')
    target = wtforms.SelectField('Database', choices=[])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.Length(max=50)
    ])

    distribute = wtforms.BooleanField('Divide ortholog abundance by its incidence on each layer', default=False)
    modulecoverage = wtforms.BooleanField('Compute module coverage', default=True)
    private = wtforms.BooleanField('Keep the result private (Hide from "List of Profiles")', default=True)
    submit = wtforms.SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(MappingForm, self).__init__(*args, **kwargs)
        self.target.choices = get_targets()

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
        self.target.choices = get_targets()
        
class UploadForm(flask_wtf.FlaskForm):
    input_file = flask_wtf.file.FileField('Input file', validators=[
        flask_wtf.file.FileRequired()
    ])
    target = wtforms.TextField('Database', validators=[
        wtforms.validators.Length(max=50)
    ])
    description = wtforms.TextField('Description', validators=[
        wtforms.validators.Length(max=50)
    ])

    private = wtforms.BooleanField('Keep the reference private (Hide from "List of Trees")', default=True)
    submit = wtforms.SubmitField('Submit')

    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
