import os


def smart(request):
    return {
        "smart": {
            "build_date": os.environ.get("BUILD_DATE", ""),
            "version": os.environ.get("VERSION", ""),
        }
    }
