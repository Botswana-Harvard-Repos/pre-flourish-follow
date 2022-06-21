from django.conf import settings

from edc_model_wrapper import ModelWrapper


class BookingModelWrapper(ModelWrapper):

    model = 'pre_flourish_follow.preflourishbooking'
    querystring_attrs = ['subject_cell']
    next_url_attrs = ['subject_cell']
    next_url_name = settings.DASHBOARD_URL_NAMES.get(
        'pre_flourish_follow_booking_listboard_url')
