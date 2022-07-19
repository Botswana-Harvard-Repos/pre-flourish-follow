from django.contrib.admin import AdminSite as DjangoAdminSite


class AdminSite(DjangoAdminSite):
    site_title = 'Pre Flourish Follow'
    site_header = 'Pre Flourish Follow'
    index_title = 'Pre Flourish Follow'
    site_url = '/administration/'
    enable_nav_sidebar = False

pre_flourish_follow_admin = AdminSite(name='pre_flourish_follow_admin')
