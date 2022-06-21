from edc_call_manager.model_caller import ModelCaller, DAILY
from edc_call_manager.decorators import register
from flourish_caregiver.models import CaregiverLocator


from ..models import PreFlourishCall, PreFlourishLog, PreFlourishLogEntry, PreFlourishWorkList


@register(PreFlourishWorkList)
class PreFlourishWorkListFollowUpModelCaller(ModelCaller):
    call_model = PreFlourishCall
    log_model = PreFlourishLog
    log_entry_model = PreFlourishLogEntry
    locator_model = (CaregiverLocator, 'subject_identifier')
#     consent_model = (SubjectConsent, 'subject_identifier')
    alternative_locator_filter = 'study_maternal_identifier'
    interval = DAILY
