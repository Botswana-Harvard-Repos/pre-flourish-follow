from django.apps import apps as django_apps
from django.conf import settings
from django.contrib import admin
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django_revision.modeladmin_mixin import ModelAdminRevisionMixin
from edc_base.sites.admin import ModelAdminSiteMixin
from edc_constants.constants import YES
from edc_model_admin import audit_fieldset_tuple
from edc_model_admin import ModelAdminAuditFieldsMixin, ModelAdminFormAutoNumberMixin, \
    ModelAdminFormInstructionsMixin, ModelAdminInstitutionMixin, \
    ModelAdminNextUrlRedirectMixin, ModelAdminReadOnlyMixin, \
    ModelAdminRedirectOnDeleteMixin
from edc_model_admin import ModelAdminBasicMixin
from edc_model_admin.changelist_buttons import ModelAdminChangelistModelButtonMixin
from edc_model_admin.model_admin_next_url_redirect_mixin import \
    ModelAdminNextUrlRedirectError

from .admin_site import pre_flourish_follow_admin
from .exportaction_mixin import ExportActionMixin
from .forms import (BookingForm, InPersonContactAttemptForm, LogEntryForm, WorkListForm)
from .models import (PreFlourishBooking, PreFlourishCall,
                     PreFlourishInPersonContactAttempt, PreFlourishInPersonLog,
                     PreFlourishLog, PreFlourishLogEntry, PreFlourishWorkList)


class ModelAdminMixin(ModelAdminNextUrlRedirectMixin,
                      ModelAdminFormInstructionsMixin,
                      ModelAdminFormAutoNumberMixin, ModelAdminRevisionMixin,
                      ModelAdminAuditFieldsMixin, ModelAdminReadOnlyMixin,
                      ModelAdminInstitutionMixin,
                      ModelAdminRedirectOnDeleteMixin,
                      ModelAdminSiteMixin,
                      ExportActionMixin):
    list_per_page = 10
    date_hierarchy = 'modified'
    empty_value_display = '-'


@admin.register(PreFlourishBooking, site=pre_flourish_follow_admin)
class BookingAdmin(ModelAdminMixin, admin.ModelAdmin):
    form = BookingForm

    fieldsets = (
        (None, {
            'fields': (
                'study_maternal_identifier',
                'first_name',
                'last_name',
                'booking_date',
                'appt_type',)}),
        audit_fieldset_tuple)

    list_display = ('first_name', 'last_name',)


@admin.register(PreFlourishWorkList, site=pre_flourish_follow_admin)
class WorkListAdmin(ModelAdminMixin, admin.ModelAdmin):
    form = WorkListForm

    fieldsets = (
        (None, {
            'fields': (
                'subject_identifier',
                'study_maternal_identifier',
                'report_datetime',
                'prev_study',
                'is_called',
                'called_datetime',
                'visited',)}),
        audit_fieldset_tuple)

    instructions = ['Complete this form once per day.']

    list_display = (
        'subject_identifier', 'study_maternal_identifier', 'prev_study', 'is_called')


class ModelAdminCallMixin(ModelAdminChangelistModelButtonMixin, ModelAdminBasicMixin):
    date_hierarchy = 'modified'

    mixin_fields = (
        'call_attempts',
        'call_status',
        'call_outcome',
    )

    mixin_radio_fields = {'call_status': admin.VERTICAL}

    list_display_pos = None
    mixin_list_display = (
        'subject_identifier',
        'call_attempts',
        'call_outcome',
        'scheduled',
        'label',
        'first_name',
        'initials',
        'user_created',
    )

    mixin_list_filter = (
        'call_status',
        'call_attempts',
        'modified',
        'hostname_created',
        'user_created',
    )

    mixin_readonly_fields = (
        'call_attempts',
    )

    mixin_search_fields = ('subject_identifier', 'initials', 'label')


@admin.register(PreFlourishCall, site=pre_flourish_follow_admin)
class CallAdmin(ModelAdminMixin, ModelAdminCallMixin, admin.ModelAdmin):
    pass


@admin.register(PreFlourishLog, site=pre_flourish_follow_admin)
class LogAdmin(ModelAdminMixin, admin.ModelAdmin):

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PreFlourishLogEntry, site=pre_flourish_follow_admin)
class LogEntryAdmin(ModelAdminMixin, admin.ModelAdmin):
    form = LogEntryForm

    search_fields = ['study_maternal_identifier']

    exclude_fields = [
        '_state', 'user_modified', 'revision', 'device_created', 'device_modified',
        'log_id', 'hostname_created', 'hostname_modified', 'willing_consent',
        'has_biological_child', 'not_interested', 'busy', 'away', 'unavailable',
        'DWTA', 'busy_dwtp', 'doesnt_live_in_area', 'wont_disclose_status_to_child',
        'child_not_lwh', 'doesnt_want_to_join', 'work_constraints', 'fears_joining',
        'partner_refused', 'other_appts', 'fears_stigma', 'child_busy',
        'child_not_interested', 'child_doesnt_live_in_area', 'child_fears_joining',
        'child_other_appts', 'child_fears_stigma', 'child_dead', 'caregiver_unwilling',
        'child_is_unwilling', 'child_age_not_in_range', 'OTHER', 'caregiver_age',
        'caregiver_omang', 'willing_assent', 'study_interest'
    ]

    fieldsets = (
        (None, {
            'fields': ('log',
                       'study_maternal_identifier',
                       'prev_study',
                       'call_datetime',
                       'phone_num_type',
                       'phone_num_success',)
        }),

        ('Subject Cell & Telephones', {
            'fields': ('cell_contact_fail',
                       'alt_cell_contact_fail',
                       'tel_contact_fail',
                       'alt_tel_contact_fail',)
        }),
        ('Subject Work Contact', {
            'fields': ('work_contact_fail',)
        }),
        ('Indirect Contact Cell & Telephone', {
            'fields': ('cell_alt_contact_fail',
                       'tel_alt_contact_fail',)
        }),
        ('Caretaker Cell & Telephone', {
            'fields': ('cell_resp_person_fail',
                       'tel_resp_person_fail')
        }),
        ('Eligibility Criteria', {
            'fields': (
                'has_child',
                'appt',
                'appt_type',
                'other_appt_type',
                'appt_reason_unwilling',
                'appt_reason_unwilling_other',
            )
        }),
        ('Schedule Appointment With Participant', {
            'fields': (
                'appt_date',
                'appt_grading',
                'appt_location',
                'appt_location_other',
                'may_call',
                'home_visit',
                'home_visit_other',
                'final_contact',)
        }), audit_fieldset_tuple)

    radio_fields = {
        'has_biological_child': admin.VERTICAL,
        'appt': admin.VERTICAL,
        'appt_type': admin.VERTICAL,
        'appt_grading': admin.VERTICAL,
        'appt_location': admin.VERTICAL,
        'may_call': admin.VERTICAL,
        'willing_consent': admin.VERTICAL,
        'has_child': admin.VERTICAL,
        'caregiver_age': admin.VERTICAL,
        'caregiver_omang': admin.VERTICAL,
        'willing_assent': admin.VERTICAL,
        'study_interest': admin.VERTICAL,
        'cell_contact_fail': admin.VERTICAL,
        'alt_cell_contact_fail': admin.VERTICAL,
        'tel_contact_fail': admin.VERTICAL,
        'alt_tel_contact_fail': admin.VERTICAL,
        'work_contact_fail': admin.VERTICAL,
        'cell_alt_contact_fail': admin.VERTICAL,
        'tel_alt_contact_fail': admin.VERTICAL,
        'cell_resp_person_fail': admin.VERTICAL,
        'tel_resp_person_fail': admin.VERTICAL,
        'home_visit': admin.VERTICAL,
        'final_contact': admin.VERTICAL, }

    filter_horizontal = ('appt_reason_unwilling',)

    list_display = (
        'study_maternal_identifier', 'prev_study', 'call_datetime',)

    def get_form(self, request, obj=None, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)

        if obj:
            study_maternal_identifier = getattr(obj, 'study_maternal_identifier', '')
        else:
            study_maternal_identifier = request.GET.get('study_maternal_identifier')

        fields = self.get_all_fields(form)

        for idx, field in enumerate(fields):
            custom_value = self.custom_field_label(study_maternal_identifier, field)

            if custom_value:
                form.base_fields[
                    field].label = f'{idx + 1}. Why was the contact to {custom_value} ' \
                                   f'unsuccessful?'
        form.custom_choices = self.phone_choices(study_maternal_identifier)
        return form

    def redirect_url(self, request, obj, post_url_continue=None):
        redirect_url = super().redirect_url(
            request, obj, post_url_continue=post_url_continue)

        if 'none_of_the_above' not in obj.phone_num_success \
                and obj.has_child == YES and obj.appt == YES:

            if request.GET.dict().get('next'):
                url_name = settings.DASHBOARD_URL_NAMES.get(
                    'pre_flourish_caregiver_locator_listboard_url')

            options = {
                'study_maternal_identifier': request.GET.get('study_maternal_identifier',
                                                             None)}

            try:
                redirect_url = reverse(url_name, kwargs=options)
            except NoReverseMatch as e:
                raise ModelAdminNextUrlRedirectError(
                    f'{e}. Got url_name={url_name}, kwargs={options}.')

        return redirect_url

    def custom_field_label(self, study_identifier, field):
        caregiver_locator_cls = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        fields_dict = {
            'cell_contact_fail': 'subject_cell',
            'alt_cell_contact_fail': 'subject_cell_alt',
            'tel_contact_fail': 'subject_phone',
            'alt_tel_contact_fail': 'subject_phone_alt',
            'work_contact_fail': 'subject_work_phone',
            'cell_alt_contact_fail': 'indirect_contact_cell',
            'tel_alt_contact_fail': 'indirect_contact_phone',
            'cell_resp_person_fail': 'caretaker_cell',
            'tel_resp_person_fail': 'caretaker_tel'}

        try:
            locator_obj = caregiver_locator_cls.objects.filter(
                study_maternal_identifier=study_identifier).latest('report_datetime')
        except caregiver_locator_cls.DoesNotExist:
            pass
        else:
            attr_name = fields_dict.get(field, None)
            if attr_name:
                return getattr(locator_obj, attr_name, '')

    def get_all_fields(self, instance):
        """"
        Return names of all available fields from given Form instance.

        :arg instance: Form instance
        :returns list of field names
        :rtype: list
        """

        fields = list(instance.base_fields)

        for field in list(instance.declared_fields):
            if field not in fields:
                fields.append(field)
        return fields

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['log'].queryset = \
            PreFlourishLog.objects.filter(id=request.GET.get('log'))
        return super(LogEntryAdmin, self).render_change_form(
            request, context, *args, **kwargs)


@admin.register(PreFlourishInPersonContactAttempt, site=pre_flourish_follow_admin)
class InPersonContactAttemptAdmin(ModelAdminMixin, admin.ModelAdmin):
    form = InPersonContactAttemptForm

    search_fields = ['study_maternal_identifier']

    fieldsets = (
        (None, {
            'fields': ('in_person_log',
                       'study_maternal_identifier',
                       'prev_study',
                       'contact_date',
                       'contact_location',
                       'successful_location',
                       'phy_addr_unsuc',
                       'phy_addr_unsuc_other',
                       'workplace_unsuc',
                       'workplace_unsuc_other',
                       'contact_person_unsuc',
                       'contact_person_unsuc_other',)},
         ),
        audit_fieldset_tuple
    )

    radio_fields = {'phy_addr_unsuc': admin.VERTICAL,
                    'workplace_unsuc': admin.VERTICAL,
                    'contact_person_unsuc': admin.VERTICAL}

    list_display = (
        'study_maternal_identifier', 'prev_study', 'contact_date',)

    def get_form(self, request, obj=None, *args, **kwargs):
        form = super().get_form(request, *args, **kwargs)

        if obj:
            study_maternal_identifier = getattr(obj, 'study_maternal_identifier', '')
        else:
            study_maternal_identifier = request.GET.get('study_maternal_identifier')

        fields = self.get_all_fields(form)

        for idx, field in enumerate(fields):
            custom_value = self.custom_field_label(study_maternal_identifier,
                                                   field)

            if custom_value:
                form.base_fields[field].label = f'{idx + 1}. Why was the in-person ' \
                                                f'visit' \
                                                f' to {custom_value} unsuccessful?'
        form.custom_choices = self.home_visit_choices(study_maternal_identifier)
        return form

    def home_visit_choices(self, study_identifier):
        caregiver_locator_cls = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        field_attrs = [
            'physical_address',
            'subject_work_place',
            'indirect_contact_physical_address']

        try:
            locator_obj = caregiver_locator_cls.objects.filter(
                study_maternal_identifier=study_identifier).latest('report_datetime')
        except caregiver_locator_cls.DoesNotExist:
            pass
        else:
            home_visit_choices = ()
            for field_attr in field_attrs:
                value = getattr(locator_obj, field_attr)
                if value:
                    home_visit_choices += ((field_attr, value),)
            return home_visit_choices

    def custom_field_label(self, study_identifier, field):
        caregiver_locator_cls = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        fields_dict = {
            'phy_addr_unsuc': 'physical_address',
            'workplace_unsuc': 'subject_work_place',
            'contact_person_unsuc': 'indirect_contact_physical_address'}

        try:
            locator_obj = caregiver_locator_cls.objects.filter(
                study_maternal_identifier=study_identifier).latest('report_datetime')
        except caregiver_locator_cls.DoesNotExist:
            pass
        else:
            attr_name = fields_dict.get(field, None)
            if attr_name:
                return getattr(locator_obj, attr_name, '')

    def get_all_fields(self, instance):
        """"
        Return names of all available fields from given Form instance.
        """

        fields = list(instance.base_fields)

        for field in list(instance.declared_fields):
            if field not in fields:
                fields.append(field)
        return fields

    def redirect_url(self, request, obj, post_url_continue=None):
        redirect_url = super().redirect_url(
            request, obj, post_url_continue=post_url_continue)
        if 'none_of_the_above' not in obj.successful_location:
            if request.GET.dict().get('next'):
                url_name = settings.DASHBOARD_URL_NAMES.get(
                    'maternal_dataset_listboard_url')
            options = {'study_maternal_identifier': request.GET.dict().get(
                'study_maternal_identifier')}
            try:
                redirect_url = reverse(url_name, kwargs=options)
            except NoReverseMatch as e:
                raise ModelAdminNextUrlRedirectError(
                    f'{e}. Got url_name={url_name}, kwargs={options}.')
        return redirect_url

    def render_change_form(self, request, context, *args, **kwargs):
        context['adminform'].form.fields['in_person_log'].queryset = \
            PreFlourishInPersonLog.objects.filter(id=request.GET.get('in_person_log'))
        return super().render_change_form(request, context, *args, **kwargs)
