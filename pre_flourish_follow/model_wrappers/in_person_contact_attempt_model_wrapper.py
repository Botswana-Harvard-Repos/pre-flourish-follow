from django.conf import settings

from edc_model_wrapper.wrappers import ModelWrapper


class InPersonContactAttemptModelWrapper(ModelWrapper):

    model = 'pre_flourish_follow.preflourishinpersoncontactattempt'
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
                                'pre_flourish_follow_listboard_url')
    querystring_attrs = ['in_person_log']
    next_url_attrs = ['in_person_log', 'study_maternal_identifier', 'prev_study']

    @property
    def study_maternal_identifier(self):
        return self.object.study_maternal_identifier

    @property
    def in_person_log(self):
        return self.object.in_person_log.id
