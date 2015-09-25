import os

from Project.settings import BASE_DIR


def version_description(request):
    with open(os.path.join(BASE_DIR, 'version.txt')) as f:
        VERSION_DESCRIPTION = f.read().strip()
    context_extras = {}
    context_extras['VERSION_DESCRIPTION'] = VERSION_DESCRIPTION

    return context_extras
