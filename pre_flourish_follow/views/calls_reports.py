import pandas as pd
import pytz
import plotly.express as px
from plotly.offline import plot
from django.apps import apps as django_apps
from django.views.generic import TemplateView
from edc_base import get_utcnow
from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import NO, OTHER, YES
from edc_navbar import NavbarViewMixin

from pre_flourish.helper_classes.utils import is_flourish_eligible

tz = pytz.timezone('Africa/Gaborone')


class CallsReports(EdcBaseViewMixin, NavbarViewMixin, TemplateView):
    template_name = 'pre_flourish_follow/calls_reports.html'
    navbar_name = 'pre_flourish_follow'
    navbar_selected_item = 'calls_reports'

    calls_model = 'pre_flourish_follow.preflourishcall'
    log_model = 'pre_flourish_follow.preflourishlog'
    log_entry_model = 'pre_flourish_follow.preflourishlogentry'
    worklist_model = 'pre_flourish_follow.preflourishworklist'
    consent_model = 'pre_flourish.preflourishconsent'
    screening_model = 'pre_flourish.preflourishsubjectscreening'
    flourish_consent_model = 'flourish_caregiver.caregiverchildconsent'
    contact_model = 'pre_flourish.preflourishcontact'

    # Variable for Pre-flourish to Flourish enrolment report
    pf_fl_enrolment = []

    @property
    def calls_model_cls(self):
        return django_apps.get_model(self.calls_model)

    @property
    def log_model_cls(self):
        return django_apps.get_model(self.log_model)

    @property
    def log_entry_model_cls(self):
        return django_apps.get_model(self.log_entry_model)

    @property
    def worklist_model_cls(self):
        return django_apps.get_model(self.worklist_model)

    @property
    def all_log_entries(self):
        return self.log_entry_model_cls.objects.all()

    @property
    def screening_model_cls(self):
        return django_apps.get_model(self.screening_model)

    @property
    def consent_model_cls(self):
        return django_apps.get_model(self.consent_model)

    @property
    def flourish_consent_model_cls(self):
        return django_apps.get_model(self.flourish_consent_model)

    @property
    def contact_model_cls(self):
        return django_apps.get_model(self.contact_model)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'contact_attempts': self.get_contact_attempts_data,
            'eligibility_report': self.generate_eligibility_report,
            'enrolment_report': self.generate_enrolment_report,
            'pf_fl_enrolment_table': self.pf_fl_enrolment_df.to_html(
                classes=['table', 'table-striped'],
                table_id='pf_fl_enrolment_df',
                border=0,
                index=False)
        })
        return context

    @property
    def get_contact_attempts_data(self):
        successful_calls = self.worklist_model_cls.objects.filter(
            is_called=True).count()

        return {
            'successful_calls': successful_calls, }

    def get_latest_model_obj(self, model_cls, query_attr, query_value,
                             order_by):
        latest_obj = model_cls.objects.filter(
            **{f'{query_attr}': query_value}).order_by(f'-{order_by}').first()
        return latest_obj

    @property
    def generate_eligibility_report(self):
        study_maternal_idxs = self.worklist_model_cls.objects.filter(
            is_called=True).values_list(
                'study_maternal_identifier', flat=True)
        eligible_with_child = 0
        ineligible_no_child = 0
        willing_to_schedule = 0
        not_willing_to_schedule = 0
        still_thinking_to_schedule = 0
        screening_appointments = 0
        recall_appointments = 0
        other_appointments = 0
        scheduled_appt = 0
        eligible_pending_fu = 0
        for study_idx in study_maternal_idxs:
            model_obj = self.get_latest_model_obj(
                self.log_entry_model_cls, 'study_maternal_identifier',
                study_idx, 'call_datetime',)
            if getattr(model_obj, 'has_child', None) == YES:
                eligible_with_child += 1
            if getattr(model_obj, 'has_child', None) == NO:
                ineligible_no_child += 1
            if getattr(model_obj, 'appt', None) == YES:
                willing_to_schedule += 1
            if getattr(model_obj, 'appt', None) == NO:
                not_willing_to_schedule += 1
            if getattr(model_obj, 'appt', None) == 'thinking':
                still_thinking_to_schedule += 1
            if getattr(model_obj, 'appt_type', None) == 'screening':
                screening_appointments += 1
            if getattr(model_obj, 'appt_type', None) == 're_call':
                recall_appointments += 1
            if getattr(model_obj, 'appt_type', None) == OTHER:
                other_appointments += 1
            appt_date = getattr(model_obj, 'appt_date', None)
            if appt_date and appt_date >= get_utcnow().date():
                scheduled_appt += 1

            phone_num_success = getattr(
                model_obj, 'phone_num_success', None)
            may_call = getattr(model_obj, 'may_call', None)

            if 'none_of_the_above' in phone_num_success and may_call == YES:
                eligible_pending_fu += 1

        return {
            'eligible_with_child': eligible_with_child,
            'eligible_pending_fu': eligible_pending_fu,
            'ineligible_no_child': ineligible_no_child,
            'willing_to_schedule': willing_to_schedule,
            'not_willing_to_schedule': not_willing_to_schedule,
            'still_thinking_to_schedule': still_thinking_to_schedule,
            'screening_appointments': screening_appointments,
            'recall_appointments': recall_appointments,
            'other_appointments': other_appointments,
            'scheduled_appt': scheduled_appt
        }

    @property
    def generate_enrolment_report(self):
        screened = self.screening_model_cls.objects.count()
        consents = self.consent_model_cls.objects.all()
        child_consents_count = 0
        fl_eligible = 0
        fl_consented = 0
        fl_scheduled_count = 0

        for consent in consents:
            child_consents = consent.preflourishcaregiverchildconsent_set.values_list(
                'subject_identifier', flat=True)
            child_consents = list(set(child_consents))
            child_consents_count += len(child_consents)

            for child_consent in child_consents:
                fl_enrolment_dt = None
                fl_scheduled_dt = None
                pf_enrolment_dt = consent.preflourishcaregiverchildconsent_set.filter(
                    subject_identifier=child_consent).earliest(
                        'consent_datetime').consent_datetime.astimezone(tz).date()
                eligible, _ = is_flourish_eligible(child_consent)
                if eligible:
                    fl_eligible += 1
                fl_consent = self.flourish_consent_model_cls.objects.filter(
                    study_child_identifier=child_consent)
                if fl_consent.exists():
                    fl_consented += 1
                    fl_enrolment_dt = fl_consent.earliest(
                        'consent_datetime').consent_datetime.astimezone(tz).date()

                fl_enrol_scheduled = self.contact_model_cls.objects.filter(
                    subject_identifier=child_consent,
                    appt_date__gte=get_utcnow().date())
                if fl_enrol_scheduled.exists():
                    fl_scheduled_count += 1
                    fl_scheduled_dt = fl_enrol_scheduled.latest(
                        'appt_date').appt_date
                self.pf_fl_enrolment.append(
                    {'subject_identifier': child_consent,
                     'pf_enrolment_dt': pf_enrolment_dt,
                     'fl_enrolment_dt': fl_enrolment_dt,
                     'fl_scheduled_dt': fl_scheduled_dt})

        return {'screened': screened,
                'consented': consents.count(),
                'child_consents_count': child_consents_count,
                'flourish_eligible': fl_eligible,
                'fl_enrol_scheduled': fl_scheduled_count,
                'flourish_consented': fl_consented}

    @property
    def pf_fl_enrolment_df(self):
        df = pd.DataFrame(
            self.pf_fl_enrolment, columns=['subject_identifier', 'pf_enrolment_dt',
                                           'fl_enrolment_dt', 'fl_scheduled_dt'])
        df['fl_enrolment_dt'] = pd.to_datetime(df['fl_enrolment_dt'])
        df['pf_enrolment_dt'] = pd.to_datetime(df['pf_enrolment_dt'])

        df['enrolment_dt_diff'] = (df['fl_enrolment_dt'] - df['pf_enrolment_dt']).dt.days
        return df.fillna('')
