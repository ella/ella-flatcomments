def show_reversed(request):
    reverse = False
    # TODO: maybe also pass in the content_type to makethe decision
    if 'reverse' in request.GET:
        reverse = bool(request.GET['reverse'])
    return reverse
