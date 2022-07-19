from django.conf import settings
from edc_model_wrapper import ModelWrapper


class LogEntryModelWrapper(ModelWrapper):

    model = 'pre_flourish_follow.preflourishlogentry'
    querystring_attrs = ['log', 'study_maternal_identifier', 'prev_study']
    next_url_attrs = ['log', 'study_maternal_identifier', 'prev_study']
    next_url_name = settings.DASHBOARD_URL_NAMES.get('pre_flourish_follow_listboard_url')

    @property
    def log(self):
        return self.object.log
    
    @property
    def prev_study(self):
        return "BCCP"