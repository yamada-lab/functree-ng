from functree import models

class DefinitionService():
    def has_definition(source):
        '''
        For now even if several definitions are found True is returned
        '''
        has_definition = False
        if models.Definition.objects.filter(source=source).count() > 0:
            has_definition = True
        return has_definition