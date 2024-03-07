from django.conf import settings

from edc_navbar import NavbarItem, site_navbars, Navbar

flourish_follow = Navbar(name='pre_flourish_follow')
no_url_namespace = True if settings.APP_NAME == 'pre_flourish_follow' else False

flourish_follow.append_item(
    NavbarItem(name='assignments',
               label='Pre-Flourish Assignments',
               fa_icon='fa-cogs',
               url_name='pre_flourish_follow:home_url'))

flourish_follow.append_item(
    NavbarItem(name='Calls Reports',
               label='Pre-Flourish Calls Reports',
               fa_icon='fa-cogs',
               url_name='pre_flourish_follow:calls_reports_url'))

flourish_follow.append_item(
    NavbarItem(
        name='worklist',
        title='Pre-Flourish Worklist',
        label='Pre-Flourish Worklist',
        fa_icon='fa-user-plus',
        url_name=settings.DASHBOARD_URL_NAMES[
            'pre_flourish_follow_listboard_url'],
        no_url_namespace=no_url_namespace))

flourish_follow.append_item(
    NavbarItem(name='flourish_follow_admin',
               label='Pre-Flourish Follow Admin',
               fa_icon='fa-cogs',
               url_name='pre_flourish_follow:admin_url'))

site_navbars.register(flourish_follow)
