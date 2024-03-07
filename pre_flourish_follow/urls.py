from django.urls import path
from django.views.generic.base import RedirectView
from edc_dashboard import UrlConfig

from .admin_site import pre_flourish_follow_admin
from .views import (AppointmentListboardView, BookingListboardView, BookListboardView,
                    CallsReports, HomeView, ListboardView)

app_name = 'pre_flourish_follow'

subject_identifier = '066\-[0-9\-]+'
screening_identifier = '[A-Z0-9]{8}'
subject_cell = '7[0-9]{7}'

urlpatterns = [
    path('admin/', pre_flourish_follow_admin.urls),
    path('home', HomeView.as_view(), name='home_url'),
    path('calls_reports', CallsReports.as_view(), name='calls_reports_url'),
    path('', RedirectView.as_view(url='admin/'), name='admin_url'),
]

flourish_follow_listboard_url_config = UrlConfig(
    url_name='pre_flourish_follow_listboard_url',
    view_class=ListboardView,
    label='pre_flourish_follow_listboard',
    identifier_label='subject_identifier',
    identifier_pattern=screening_identifier)

flourish_follow_appt_listboard_url_config = UrlConfig(
    url_name='pre_flourish_follow_appt_listboard_url',
    view_class=AppointmentListboardView,
    label='pre_flourish_follow_appt_listboard',
    identifier_label='subject_identifier',
    identifier_pattern=screening_identifier)

flourish_follow_booking_listboard_url_config = UrlConfig(
    url_name='pre_flourish_follow_booking_listboard_url',
    view_class=BookingListboardView,
    label='pre_flourish_follow_booking_listboard',
    identifier_label='subject_cell',
    identifier_pattern=subject_cell)

flourish_follow_book_listboard_url_config = UrlConfig(
    url_name='pre_flourish_follow_book_listboard_url',
    view_class=BookListboardView,
    label='pre_flourish_follow_book_listboard',
    identifier_label='subject_cell',
    identifier_pattern=subject_cell)

urlpatterns += flourish_follow_listboard_url_config.listboard_urls
urlpatterns += flourish_follow_appt_listboard_url_config.listboard_urls
urlpatterns += flourish_follow_booking_listboard_url_config.listboard_urls
urlpatterns += flourish_follow_book_listboard_url_config.listboard_urls