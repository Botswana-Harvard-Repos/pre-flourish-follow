from django.apps import apps as django_apps
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
        pre_flourish_worklist_cls = django_apps.get_model(
            'pre_flourish_follow.preflourishworklist')

        try:
            maternal_dataset_obj = pre_flourish_worklist_cls.objects.get(
                study_maternal_identifier=self.object.study_maternal_identifier)
        except pre_flourish_worklist_cls.DoesNotExist:
            raise Exception('No pre_flourish_worklist found for '
                            'study maternal identifier {}'.format(
                self.object.study_maternal_identifier))
        else:
            return maternal_dataset_obj.prev_study
