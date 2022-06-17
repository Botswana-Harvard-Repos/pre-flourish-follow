from django.apps import apps as django_apps
from django.conf import settings
from django.db.models import Q

from edc_constants.constants import NOT_APPLICABLE
from edc_model_wrapper import ModelWrapper

from ..model_wrappers import InPersonContactAttemptModelWrapper
from ..models import *
from .log_entry_model_wrapper import LogEntryModelWrapper


class WorkListModelWrapper(ModelWrapper):

    model = 'pre_flourish_follow.preflourishworklist'
    querystring_attrs = ['subject_identifier', 'study_maternal_identifier']
    next_url_attrs = ['subject_identifier', 'study_maternal_identifier']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'pre_flourish_follow_listboard_url')

    @property
    def subject_locator(self):
        SubjectLocator = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        if self.object.subject_identifier:
            try:
                locator = SubjectLocator.objects.get(
                    subject_identifier=self.object.subject_identifier)
            except SubjectLocator.DoesNotExist:
                try:
                    locator = SubjectLocator.objects.get(
                        study_maternal_identifier=self.object.study_maternal_identifier)
                except SubjectLocator.DoesNotExist:
                    return None
                else:
                    return locator
            else:
                return locator
        return None

    @property
    def maternal_dataset(self):
        maternal_dataset_cls = django_apps.get_model(
            'flourish_caregiver.maternaldataset')
        try:
            maternal_dataset_obj = maternal_dataset_cls.objects.get(
                study_maternal_identifier=self.study_maternal_identifier)
        except maternal_dataset_cls.DoesNotExist:
            return None
        else:
            return maternal_dataset_obj

    # @property
    # def multiple_births(self):
    #     """Returns value of births if the mother has twins/triplets.
    #     """
    #     if self.maternal_dataset:
    #         child_dataset_cls = django_apps.get_model('flourish_child.childdataset')
    #         children = child_dataset_cls.objects.filter(
    #             study_maternal_identifier=self.maternal_dataset.study_maternal_identifier)
    #         return children.count()
    #     return 0

    @property
    def call_datetime(self):
        return self.object.called_datetime

    @property
    def call(self):
        call = PreFlourishCall.objects.filter(
            subject_identifier=self.object.subject_identifier).order_by('scheduled').last()
        return str(call.id)

    @property
    def call_log(self):
        call = PreFlourishCall.objects.filter(
            subject_identifier=self.object.subject_identifier).order_by('scheduled').last()
        call_log = PreFlourishLog.objects.get(call=call)
        return str(call_log.id)

    @property
    def log_entries(self):
        wrapped_entries = []
        
        #FIXME: Call is empty, was throwing an exception. A check was added, as a temp fix
        
        call = PreFlourishCall.objects.filter(
            subject_identifier=self.object.subject_identifier).order_by('scheduled').last()
        
        if call:
            log_entries = PreFlourishLogEntry.objects.filter(
                log__call__subject_identifier=call.subject_identifier).order_by('-call_datetime')[:3]
            for log_entry in log_entries:
                wrapped_entries.append(
                    LogEntryModelWrapper(log_entry))
        return wrapped_entries

    @property
    def home_visit_log_entries(self):

        wrapped_entries = []
        if hasattr(self.object, 'inpersonlog'):
            in_person_log = getattr(self.object, 'inpersonlog')
            log_entries = PreFlourishInPersonContactAttempt.objects.filter(
                in_person_log=in_person_log)
            for log_entry in log_entries:
                wrapped_entries.append(
                    InPersonContactAttemptModelWrapper(log_entry))

        return wrapped_entries

    @property
    def home_visit_log_entry(self):
        # FIXME: Throws an exception because does not exist for the current object
        if hasattr(self.object, 'inpersonlog'):
            in_person_log = getattr(self.object, 'inpersonlog')
            
            log_entry = PreFlourishInPersonContactAttempt(
                in_person_log=in_person_log,
                prev_study=self.prev_protocol,
                study_maternal_identifier=self.study_maternal_identifier)
            return InPersonContactAttemptModelWrapper(log_entry)

    @property
    def locator_phone_numbers(self):
        """Return all contact numbers on the locator.
        """
        field_attrs = [
            'subject_cell',
            'subject_cell_alt',
            'subject_phone',
            'subject_phone_alt',
            'subject_work_phone',
            'indirect_contact_cell',
            'indirect_contact_phone',
            'caretaker_cell',
            'caretaker_tel']
        if self.subject_locator:
            phone_choices = ()
            for field_attr in field_attrs:
                value = getattr(self.subject_locator, field_attr)
                if value:
                    phone_choices += ((field_attr, value),)
            return phone_choices

    @property
    def call_log_required(self):
        """Return True if the call log is required.
        """
        if self.locator_phone_numbers:
            return True
        return False

    @property
    def perform_home_visit(self):
        """Returns True is an RA took the descretions to do a home visit.
        """
        log_entries = PreFlourishLogEntry.objects.filter(
            study_maternal_identifier=self.object.study_maternal_identifier)
        for log in log_entries:
            if log.home_visit and not log.home_visit == NOT_APPLICABLE:
                return True
        return False

    @property
    def home_visit_required(self):
        check_fields = [
            'cell_contact_fail', 'alt_cell_contact_fail',
            'tel_contact_fail', 'alt_tel_contact_fail',
            'work_contact_fail', 'cell_alt_contact_fail',
            'tel_alt_contact_fail', 'cell_resp_person_fail',
            'tel_resp_person_fail']
        if not self.locator_phone_numbers:
            return True
        elif self.perform_home_visit:
            return True
        else:
            log_entries = PreFlourishLogEntry.objects.filter(
                ~Q(phone_num_success='none_of_the_above'),
                study_maternal_identifier=self.object.study_maternal_identifier)
            log_answers = []
            for log in log_entries:
                for var in check_fields:
                    value = getattr(log, var)
                    log_answers.append(value)
            if 'no_response' in log_answers:
                return False
            elif 'no_response_vm_not_left' in log_answers:
                return False
            elif 'disconnected' in log_answers:
                return True
        return False

    @property
    def log_entry(self):
        log = PreFlourishLog.objects.get(id=self.call_log)

        logentry = PreFlourishLogEntry(
            log=log,
            prev_study=self.prev_protocol,
            study_maternal_identifier=self.study_maternal_identifier)
        return LogEntryModelWrapper(logentry)

    @property
    def subject_consent(self):
        return django_apps.get_model(
            'flourish_caregiver.subjectconsent').objects.filter(
            subject_identifier=self.object.subject_identifier).last()

    @property
    def may_visit_home(self):
        if self.subject_locator:
            return self.subject_locator.may_visit_home
        return None

    @property
    def first_name(self):
        return self.subject_locator.first_name

    @property
    def last_name(self):
        return self.subject_locator.last_name

    @property
    def contacts(self):
        if self.subject_locator:
            return ', '.join([
                self.subject_locator.subject_cell or '',
                self.subject_locator.subject_cell_alt or '',
                self.subject_locator.subject_phone or '',
                self.subject_locator.subject_phone_alt or ''])
        return None

    @property
    def survey_schedule(self):
        return None

    @property
    def prev_protocol(self):
        if self.maternal_dataset:
            return self.maternal_dataset.protocol
        return None

