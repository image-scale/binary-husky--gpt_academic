# Plugin class template

class GptAcademicPluginTemplate:
    def __init__(self):
        pass

    def define_arg_selection_menu(self):
        raise NotImplementedError

    def execute(self, *args, **kwargs):
        raise NotImplementedError

class ArgProperty:
    def __init__(self, title=None, options=None, default_value=None, description=None, type=None):
        self.title = title
        self.options = options
        self.default_value = default_value
        self.description = description
        self.type = type

    def model_dump_json(self):
        raise NotImplementedError
