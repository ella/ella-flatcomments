def show_reversed(request):
    reverse = False
    # TODO: maybe also pass in the content_type to makethe decision
    if 'reverse' in request.GET:
        reverse = bool(request.GET['reverse'])
    return reverse

def disconnect_legacy_signals():
    " Disconnect signals for ell-comments to allow tests and migrations to run. "
    from ella.core.signals import content_published, content_unpublished
    from ella_comments.listing_handlers import publishable_published, publishable_unpublished

    content_published.disconnect(publishable_published)
    content_unpublished.disconnect(publishable_unpublished)
