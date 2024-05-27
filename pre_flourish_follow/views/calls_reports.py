from datetime import timedelta

from django.apps import apps as django_apps
from django.db.models import Avg, Count, ExpressionWrapper, F, Max, Q
from django.db.models.functions import TruncDay
from django.forms import DurationField
from django.views.generic import TemplateView
from edc_base import get_utcnow
from edc_base.view_mixins import EdcBaseViewMixin
from edc_constants.constants import NO, OTHER, YES
from edc_navbar import NavbarViewMixin


class CallsReports(EdcBaseViewMixin, NavbarViewMixin, TemplateView):
    template_name = 'pre_flourish_follow/calls_reports.html'
    navbar_name = 'pre_flourish_follow'
    navbar_selected_item = 'calls_reports'

    calls_model = 'pre_flourish_follow.preflourishcall'
    log_model = 'pre_flourish_follow.preflourishlog'
    log_entry_model = 'pre_flourish_follow.preflourishlogentry'
    worklist_model = 'pre_flourish_follow.preflourishworklist'

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'report_data': self.report_data,
            'contact_attempts_report': self.generate_contact_attempts_report,
            'appointment_scheduling_report': self.generate_appointment_scheduling_report,
            'participant_demographics_report':
                self.generate_participant_demographics_report,
            'final_contact_report': self.generate_final_contact_report,
            'contact_attempts': self.get_contact_attempts_data,
            'assignments_report': self.generate_assignments_report,
            'activity_over_time_report': self.generate_activity_over_time_report,
            'subject_follow_up_status_report':
                self.generate_subject_follow_up_status_report,
            'maternal_follow_up_status_report':
                self.generate_maternal_follow_up_status_report,
            'overdue_assignments_report': self.generate_overdue_assignments_report,
            'user_performance_report': self.generate_user_performance_report,
            'eligibility_report': self.generate_eligibility_report,
        })
        return context

    @property
    def report_data(self):
        report_data = []

        for log_entry in self.all_log_entries:
            report_data.append({
                'subject_identifier': log_entry.subject_identifier,
                'screening_identifier': log_entry.screening_identifier,
                'study_maternal_identifier': log_entry.study_maternal_identifier,
                'prev_study': log_entry.prev_study,
                'call_datetime': log_entry.call_datetime,
                'phone_num_type': log_entry.phone_num_type,
                'phone_num_success': log_entry.phone_num_success,
                'has_biological_child': log_entry.has_biological_child,
                'appt': log_entry.appt,
                'appt_type': log_entry.appt_type,
                'appt_date': log_entry.appt_date,
                'appt_grading': log_entry.appt_grading,
                'appt_location': log_entry.appt_location,
                'delivered': log_entry.delivered,
                'may_call': log_entry.may_call,
                'home_visit': log_entry.home_visit,
                'final_contact': log_entry.final_contact,
            })

        return report_data

    @property
    def generate_contact_attempts_report(self):
        total_attempts = self.log_entry_model_cls.objects.count()
        successful_attempts = self.log_entry_model_cls.objects.filter(
            phone_num_success__isnull=False).count()
        unsuccessful_reasons = self.log_entry_model_cls.objects.values(
            'cell_contact_fail').annotate(count=Count('cell_contact_fail')).order_by(
            '-count')
        return {
            'total_attempts': total_attempts,
            'successful_attempts': successful_attempts,
            'unsuccessful_reasons': list(unsuccessful_reasons)
        }

    @property
    def generate_appointment_scheduling_report(self):
        willing_to_schedule = self.log_entry_model_cls.objects.filter(
            appt__in=[YES]).count()
        unwilling_to_schedule = self.log_entry_model_cls.objects.filter(
            appt__in=[NO]).count()
        reasons_unwilling = self.log_entry_model_cls.objects.values(
            'appt_reason_unwilling__name').annotate(
            count=Count('appt_reason_unwilling')).order_by('-count')
        upcoming_appointments = self.log_entry_model_cls.objects.filter(
            appt_date__gte=get_utcnow()).values('appt_date', 'appt_type')
        return {
            'willing_to_schedule': willing_to_schedule,
            'unwilling_to_schedule': unwilling_to_schedule,
            'reasons_unwilling': list(reasons_unwilling),
            'upcoming_appointments': list(upcoming_appointments)
        }

    @property
    def generate_participant_demographics_report(self):
        by_maternal_identifier = self.log_entry_model_cls.objects.values(
            'study_maternal_identifier').annotate(
            count=Count('study_maternal_identifier')).order_by('-count')
        by_prev_study = self.log_entry_model_cls.objects.values('prev_study').annotate(
            count=Count('prev_study')).order_by('-count')
        with_children = self.log_entry_model_cls.objects.filter(
            has_biological_child=YES).count()
        return {
            'by_maternal_identifier': list(by_maternal_identifier),
            'by_prev_study': list(by_prev_study),
            'with_children': with_children
        }

    @property
    def generate_final_contact_report(self):
        final_contact_made = self.log_entry_model_cls.objects.filter(
            final_contact=YES).count()
        available_for_contact = self.log_entry_model_cls.objects.filter(
            final_contact=NO).count()
        return {
            'final_contact_made': final_contact_made,
            'available_for_contact': available_for_contact
        }

    @property
    def get_contact_attempts_data(self):
        successful_calls = self.log_entry_model_cls.objects.filter(
            phone_num_success__isnull=False).count()
        failed_calls = self.log_entry_model_cls.objects.exclude(
            phone_num_success__isnull=False).count()

        screening_appointments = self.log_entry_model_cls.objects.filter(
            appt_type='screening').count()
        re_call_appointments = self.log_entry_model_cls.objects.filter(
            appt_type='re_call').count()

        return {
            'successful_calls': successful_calls,
            'failed_calls': failed_calls,
            'screening_appointments': screening_appointments,
            're_call_appointments': re_call_appointments,
        }

    @property
    def generate_assignments_report(self):
        return self.worklist_model_cls.objects.values('assigned').annotate(
            total=Count('id'),
            total_called=Count('is_called', filter=Q(is_called=True)),
            total_visited=Count('visited', filter=Q(visited=True)),
            total_consented=Count('consented', filter=Q(consented=True))
        )

    @property
    def generate_activity_over_time_report(self):
        return self.worklist_model_cls.objects.annotate(
            date=TruncDay('report_datetime')
        ).values('date').annotate(
            total=Count('id'),
            total_called=Count('is_called', filter=Q(is_called=True)),
            total_visited=Count('visited', filter=Q(visited=True)),
            total_consented=Count('consented', filter=Q(consented=True))
        )

    @property
    def generate_subject_follow_up_status_report(self):
        return self.worklist_model_cls.objects.values('subject_identifier').annotate(
            last_report_datetime=Max('report_datetime'),
            is_called=Max('is_called'),
            last_called_datetime=Max('called_datetime'),
            visited=Max('visited'),
            consented=Max('consented')
        )

    @property
    def generate_maternal_follow_up_status_report(self):
        return self.worklist_model_cls.objects.values(
            'study_maternal_identifier').annotate(
            last_report_datetime=Max('report_datetime'),
            is_called=Max('is_called'),
            last_called_datetime=Max('called_datetime'),
            visited=Max('visited'),
            consented=Max('consented')
        )

    @property
    def generate_overdue_assignments_report(self):
        overdue_threshold = timedelta(days=30)
        return self.worklist_model_cls.objects.filter(
            date_assigned__lte=get_utcnow() - overdue_threshold,
            visited=False
        ).annotate(
            days_overdue=ExpressionWrapper(get_utcnow() - F('date_assigned'),
                                           output_field=DurationField())
        )

    @property
    def generate_user_performance_report(self):
        return self.worklist_model_cls.objects.exclude(
            date_assigned__isnull=True
        ).annotate(
            time_to_call=ExpressionWrapper(F('called_datetime') - F('date_assigned'),
                                           output_field=DurationField())
        ).values('assigned').annotate(
            average_time_to_call=Avg('time_to_call')
        )

    @property
    def generate_eligibility_report(self):
        eligible_with_child = self.log_entry_model_cls.objects.filter(
            has_biological_child=YES).count()
        ineligible_no_child = self.log_entry_model_cls.objects.filter(
            has_biological_child=NO).count()

        willing_to_schedule = self.log_entry_model_cls.objects.filter(appt=YES).count()
        not_willing_to_schedule = self.log_entry_model_cls.objects.filter(
            appt=NO).count()
        still_thinking_to_schedule = self.log_entry_model_cls.objects.filter(
            appt='thinking').count()

        screening_appointments = self.log_entry_model_cls.objects.filter(
            appt_type='Screening').count()
        recall_appointments = self.log_entry_model_cls.objects.filter(
            appt_type='Re-call').count()
        other_appointments = self.log_entry_model_cls.objects.filter(
            appt_type=OTHER).count()

        return {
            'eligible_with_child': eligible_with_child,
            'ineligible_no_child': ineligible_no_child,
            'willing_to_schedule': willing_to_schedule,
            'not_willing_to_schedule': not_willing_to_schedule,
            'still_thinking_to_schedule': still_thinking_to_schedule,
            'screening_appointments': screening_appointments,
            'recall_appointments': recall_appointments,
            'other_appointments': other_appointments,
        }
