def version_description(request):
    with open('./version.txt') as f:
        VERSION_DESCRIPTION = f.read().strip()
    context_extras = {}
    context_extras['VERSION_DESCRIPTION'] = VERSION_DESCRIPTION

    return context_extras
