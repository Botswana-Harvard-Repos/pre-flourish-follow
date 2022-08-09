import datetime
from django.core.exceptions import ValidationError
from django.test import TestCase, SimpleTestCase, tag
from edc_base.utils import get_utcnow
from edc_constants.constants import YES, NOT_APPLICABLE

from ..form_validations import LogEntryFormValidator
from .models import CaregiverLocator
from model_mommy import mommy


class TestPreFlourishLogEntryValidatorForm(SimpleTestCase):

    def setUp(self):
        # CaregiverLocator.objects.create(
        #     study_maternal_identifier='123-4',
        #     screening_identifier='12',
        #     locator_date=get_utcnow().date(),
        #     may_call=YES,
        #     subject_cell='71234567',
        #     subject_phone='74720123')
        
        call = mommy.make_recipe('pre_flourish_follow.preflourishcall')
        
        log = mommy.make_recipe('pre_flourish_follow.preflourishlog', call=call)

        self.options = {
            # 'subject_identifier': '',
            # 'screening_identifier': None,
            # 'study_maternal_identifier': '066-17300005-1',
            'log': log,
            'prev_study': 'BCCP',
            'call_datetime': datetime.datetime(2022, 8, 4, 7, 23, 6),
            'phone_num_type': ['subject_cell'],
            'phone_num_success': ['subject_cell'],
            'cell_contact_fail': NOT_APPLICABLE,
            'alt_cell_contact_fail': NOT_APPLICABLE,
            'tel_contact_fail': NOT_APPLICABLE,
            'alt_tel_contact_fail': NOT_APPLICABLE,
            'work_contact_fail': NOT_APPLICABLE,
            'cell_alt_contact_fail': NOT_APPLICABLE,
            'tel_alt_contact_fail': NOT_APPLICABLE,
            'cell_resp_person_fail': NOT_APPLICABLE,
            'tel_resp_person_fail': NOT_APPLICABLE,
            'has_biological_child': 'No',
            'has_biological_child': YES,
            'appt': 'Yes',
            'appt_type': 'consenting',
            'other_appt_type': None,
            'appt_reason_unwilling_other': None,
            'appt_date': datetime.date(2022, 8, 4),
            'appt_grading': 'firm',
            'appt_location': 'clinic',
            'appt_location_other': None,
            'delivered': False,
            'may_call': 'Yes',
            'home_visit': NOT_APPLICABLE,
            'home_visit_other': None,
            'final_contact': 'No'}
    
    @tag('success')
    def test_contact_success_valid(self):
        """
        Checks form saves successfully with all necessary field
        values completed.
        """
        form_validator = LogEntryFormValidator(cleaned_data=self.options)
        try:
            form_validator.validate()
        except ValidationError as e:
            self.fail(f'ValidationError unexpectedly raised. Got{e}')
