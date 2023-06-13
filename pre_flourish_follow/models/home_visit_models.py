from flourish_follow.models import InPersonContactAttempt, InPersonLog


class PreFlourishInPersonLog(InPersonLog):
    """A system model to track an RA\'s attempts to confirm a Plot
    (related).
    """

    class Meta:
        app_label = 'pre_flourish_follow'


class PreFlourishInPersonContactAttempt(InPersonContactAttempt):
    class Meta:
        app_label = 'pre_flourish_follow'
        verbose_name = 'In Person Contact Attempt'
        verbose_name_plural = 'In Person Contact Attempt'
