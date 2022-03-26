import hashlib
from google.cloud import translate_v2 as translate


def GoogleTranslationGetText(msg, language_code):
    from .models import Cache
    from . import translate_client, cache_local

    md5 = hashlib.md5((language_code + "__" + msg).encode()).digest()

    result = cache_local.get(md5, None)
    if not result:
        caches: Cache = Cache.objects.filter(md5=md5).defer("source", "language_code", "md5")
        result = msg
        if caches:
            result = caches[0].result
        else:
            if not translate_client:
                translate_client = translate.Client()
            result = translate_client.translate(msg, target_language=language_code)
            result = result["translatedText"]

            # Save cache
            cache = Cache()
            cache.source = msg
            cache.result = result
            cache.language_code = language_code
            cache.save()

        cache_local[md5] = result

    return result
