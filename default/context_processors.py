from django.conf import settings


def analytics(request):
    return {
        'fathom_analytics_domain': settings.FATHOM_ANALYTICS_DOMAIN,
        'fathom_analytics_id': settings.FATHOM_ANALYTICS_ID,
        'google_analytics_id': settings.GOOGLE_ANALYTICS_ID,
    }
