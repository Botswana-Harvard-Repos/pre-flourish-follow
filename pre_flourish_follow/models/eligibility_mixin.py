from django.db import models
from edc_constants.choices import YES_NO

from pre_flourish.choices import YES_NO_THINKING


class EligibilityMixin(models.Model):
    """Mixin for eligibility questions."""
    willing_consent = models.CharField(
        verbose_name="Are you willing to consent for your child HIV test?",
        max_length=20,
        blank=True,
        null=True,
        help_text='If no, participant is not eligible.',
        choices=YES_NO_THINKING)

    has_child = models.CharField(
        verbose_name="Do you have a child aged between 7 and 17.5 years?",
        max_length=3,
        blank=True,
        null=True,
        help_text='If no, participant is not eligible.',
        choices=YES_NO)

    caregiver_age = models.CharField(
        verbose_name="Are you older than 18?",
        max_length=3,
        blank=True,
        null=True,
        help_text='If no, participant is not eligible.',
        choices=YES_NO)

    caregiver_omang = models.CharField(
        verbose_name="Do you have an OMANG?",
        max_length=3,
        blank=True,
        null=True,
        help_text='If no, participant is not eligible.',
        choices=YES_NO)

    willing_assent = models.CharField(
        verbose_name="Is your child willing to assent?",
        max_length=3,
        blank=True,
        null=True,
        help_text='If no, participant is not eligible.',
        choices=YES_NO)

    study_interest = models.CharField(
        verbose_name="Are you interested in participating in the study?",
        max_length=3,
        blank=True,
        null=True,
        help_text='If no, participant is not eligible.',
        choices=YES_NO)

    class Meta:
        abstract = True
