from time import sleep, time

import requests
import sys


class COLORS:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    SUCCESS = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    MARK = "\xE2\x9C\x94"
    MARK1 = "\u2713"
    MARK2 = "\u2714\u274c"
    MARK3 = "\N{check mark}"
    MARK4 = "✓"
    PY = "\U0001F40D"
    CHECK = "\N{BALLOT BOX WITH CHECK}"
    UNCHECK = "\N{BALLOT BOX}"


if __name__ == "__main__":
    if len(sys.argv) == 1:
        urls = ["https://register.unicef.org/"]
    else:
        urls = sys.argv[1:]
    rnd = time()
    latest_ref = None
    latest_ver = None
    while True:
        for url in urls:
            ret = requests.get(f"{url}?{rnd}")
            ver = ret.headers.get("X-Aurora-Version", "N/A")
            ref = ret.headers.get("X-Azure-Ref", "N/A")
            if ver != latest_ver:
                marker = COLORS.WARNING
            else:
                marker = COLORS.RESET
            print(
                f"{marker}{url} {ret.status_code} "
                f"{latest_ver} - "
                f"{ret.headers.get('X-Aurora-Build', 'N/A')} - "
                f"{ret.headers.get('X-Aurora-Time', 'N/A')} - "
                f"{ret.headers.get('X-Azure-Ref', 'N/A')[:20]}{COLORS.RESET}"
            )
            latest_ref = ref
            latest_ver = ver

        sleep(1)
