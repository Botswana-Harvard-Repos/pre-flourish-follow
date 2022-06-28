from django.apps import apps as django_apps
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

from edc_constants.constants import YES, NONE

from ..models.worklist import PreFlourishWorkList
from .home_visit_models import PreFlourishInPersonLog, PreFlourishInPersonContactAttempt
from .call_models import PreFlourishLogEntry
from .booking import PreFlourishBooking


@receiver(post_save, weak=False, sender=PreFlourishLogEntry,
          dispatch_uid="cal_log_entry_on_post_save")
def cal_log_entry_on_post_save(sender, instance, using, raw, **kwargs):
    if not raw:
        # Update worklist
        try:
            work_list = PreFlourishWorkList.objects.get(
                study_maternal_identifier=instance.study_maternal_identifier)
        except PreFlourishWorkList.DoesNotExist:
            pass
        else:
            if 'none_of_the_above' not in instance.phone_num_success and instance.phone_num_success:
                work_list.is_called = True
                work_list.called_datetime = instance.call_datetime
                work_list.user_modified=instance.user_modified
                work_list.save()
        
        # Create or update a booking
        SubjectLocator = django_apps.get_model(
            'flourish_caregiver.caregiverlocator')
        if instance.appt == YES:
            try:
                locator = SubjectLocator.objects.filter(
                    study_maternal_identifier=instance.study_maternal_identifier).latest('report_datetime')
            except SubjectLocator.DoesNotExist:
                return None
            else:
                try:
                    booking = PreFlourishBooking.objects.get(
                        study_maternal_identifier=instance.study_maternal_identifier)
                except PreFlourishBooking.DoesNotExist:
                    PreFlourishBooking.objects.create(
                        study_maternal_identifier=instance.study_maternal_identifier,
                        first_name=locator.first_name,
                        last_name=locator.last_name,
                        booking_date=instance.appt_date,
                        appt_type=instance.appt_type)
                else:
                    booking.booking_date = instance.appt_date
                    booking.appt_type = instance.appt_type
                    booking.save()
        
        # Add user to Recruiters group
        try:
            recruiters_group = Group.objects.get(name='Recruiters')
        except Group.DoesNotExist:
            raise ValidationError('Recruiters group must exist.')
        else:
            try:
                user = User.objects.get(username=instance.user_created)
            except User.DoesNotExist:
                raise ValueError(f'The user {instance.user_created}, does not exist.')
            else:
                if not User.objects.filter(username=instance.user_created,
                                       groups__name='Recruiters').exists():
                    recruiters_group.user_set.add(user)


@receiver(post_save, weak=False, sender=PreFlourishWorkList,
          dispatch_uid="worklist_on_post_save")
def worklist_on_post_save(sender, instance, using, raw, **kwargs):
    if not raw:
        try:
            PreFlourishInPersonLog.objects.get(
                study_maternal_identifier=instance.study_maternal_identifier)
        except PreFlourishInPersonLog.DoesNotExist:
            PreFlourishInPersonLog.objects.create(
                worklist=instance,
                study_maternal_identifier=instance.study_maternal_identifier)

        # Add user to assignable group
        app_config = django_apps.get_app_config('pre_flourish_follow')
        try:
            assignable_users_group = Group.objects.get(name=app_config.assignable_users_group)
        except Group.DoesNotExist:
            raise ValidationError('assignable users group must exist.')
        else:
            try:
                user = User.objects.get(username=instance.user_created)
            except User.DoesNotExist:
                raise ValueError(f'The user {instance.user_created}, does not exist.')
            else:
                if not User.objects.filter(username=instance.user_created,
                                       groups__name=app_config.assignable_users_group).exists():
                    assignable_users_group.user_set.add(user)


@receiver(post_save, weak=False, sender=PreFlourishInPersonContactAttempt,
          dispatch_uid="in_person_contact_attempt_on_post_save")
def in_person_contact_attempt_on_post_save(sender, instance, using, raw, **kwargs):
    if not raw:
        try:
            work_list = PreFlourishWorkList.objects.get(
                study_maternal_identifier=instance.study_maternal_identifier)
        except PreFlourishWorkList.DoesNotExist:
            pass
        else:
            if 'none_of_the_above' not in instance.successful_location:
                work_list.visited = True
                work_list.user_modified=instance.user_modified
                work_list.save()
