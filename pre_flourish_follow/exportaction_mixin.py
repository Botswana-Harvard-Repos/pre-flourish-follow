from django.apps import apps as django_apps
from django.db.models import ForeignKey, ManyToManyField, ManyToOneRel, OneToOneField
from django.utils.translation import ugettext_lazy as _

from flourish_export.admin_export_helper import AdminExportHelper


class ExportActionMixin(AdminExportHelper):

    def export_as_csv(self, request, queryset):

        records = []

        for obj in queryset:
            data = obj.__dict__.copy()
            study_maternal_identifier = getattr(obj, 'study_maternal_identifier', None)
            for field in self.get_model_fields:
                if isinstance(field, ManyToManyField):
                    data.update(self.m2m_data_dict(obj, field))
                    continue
                if isinstance(field, (ForeignKey, OneToOneField,)):
                    continue
                if isinstance(field, ManyToOneRel):
                    data.update(self.inline_data_dict(obj, field))
                    continue
                if field.choices:
                    data[field.name] = getattr(obj, f'get_{field.name}_display')()
                    phone_fields = ['phone_num_type', 'phone_num_success']
                    if field.name in phone_fields:
                        numbers = self.phone_choices(study_maternal_identifier)
                        selected_numbers = []
                        if numbers:
                            for number in numbers:
                                selected_numbers.append(number[1])
                        data[field.name] = ', '.join(selected_numbers)

            locator_obj = self.locator_obj(study_maternal_identifier)
            if locator_obj:
                data['screening_identifier'] = locator_obj.screening_identifier
                data['subject_identifier'] = locator_obj.subject_identifier

            data = self.remove_exclude_fields(data)
            data = self.fix_date_formats(data)
            records.append(data)

        response = self.write_to_excel(records)
        return response

    export_as_csv.short_description = _(
        'Export selected %(verbose_name_plural)s')

    actions = [export_as_csv]

    def previous_bhp_study(self, study_maternal_identifier=None):
        dataset_cls = django_apps.get_model('flourish_caregiver.maternaldataset')
        if study_maternal_identifier:
            try:
                dataset_obj = dataset_cls.objects.get(
                    study_maternal_identifier=study_maternal_identifier)
            except dataset_cls.DoesNotExist:
                return None
            else:
                return dataset_obj.protocol

    def locator_obj(self, study_identifier):
        caregiver_locator_cls = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        try:
            locator_obj = caregiver_locator_cls.objects.filter(
                study_maternal_identifier=study_identifier).latest('report_datetime')
        except caregiver_locator_cls.DoesNotExist:
            return None
        else:
            return locator_obj

    def phone_choices(self, study_identifier):
        caregiver_locator_cls = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
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

        locator_obj = self.locator_obj(study_identifier)

        if locator_obj:
            phone_choices = ()
            for field_attr in field_attrs:
                value = getattr(locator_obj, field_attr)
                if value:
                    field_name = field_attr.replace('_', ' ')
                    value = f'{value} {field_name.title()}'
                    phone_choices += ((field_attr, value),)
            return phone_choices
