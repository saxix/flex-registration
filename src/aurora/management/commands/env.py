import os

from django.core.management import BaseCommand


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--no-mandatory", action="store_false", dest="mandatory", default=True, help="Do not dump mandatory"
        )
        parser.add_argument(
            "--no-optional", action="store_false", dest="optional", default=True, help="Do not dump optional"
        )
        parser.add_argument("--no-values", action="store_false", dest="values", default=True, help="Do not dump values")
        parser.add_argument(
            "--comment-optional", action="store_true", dest="comment", default=False, help="Comment optional"
        )
        parser.add_argument("--current", action="store_true", dest="current", default=False, help="Dump current values")
        parser.add_argument("--vars", action="store_true", dest="vars", default=False, help="Dump current values")
        parser.add_argument(
            "--defaults", action="store_true", dest="defaults", default=False, help="Dump default values"
        )
        parser.add_argument(
            "--no-empty", action="store_true", dest="no_empty", default=False, help="Do not dump empty values"
        )

    def handle(self, *args, **options):
        from aurora.config import env, MANDATORY, OPTIONS, SmartEnv

        if options["defaults"]:
            EE = type("SmartEnv", (SmartEnv,), {"ENVIRON": {}})
            ee = EE(**MANDATORY, **OPTIONS)

        environment = {}
        if options["mandatory"]:
            environment.update(**MANDATORY)
        if options["optional"]:
            environment.update(**OPTIONS)
        for k, v in sorted(environment.items()):
            if options["defaults"]:
                value = ee(k)
            elif options["vars"]:
                value = "${%s}" % k
            elif options["current"]:
                value = os.environ.get(k, "")
            elif options["values"]:
                value = env(k)
            else:
                value = ""
            if value or not options["no_empty"]:
                if options["comment"] and k in OPTIONS.keys():
                    self.stdout.write(f"#{k}={value}")
                else:
                    self.stdout.write(f"{k}={value}")
