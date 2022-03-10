from django import forms


class SelectField(forms.ChoiceField):
    def _get_choices(self):
        return self._choices

    def _set_choices(self, value):
        if value:
            try:
                value = value[0][0]
                from smart_register.core.models import OptionSet

                options = OptionSet.objects.get(name=value)
                value = []
                if options.separator:
                    for line in options.data.split("\n"):
                        value.append(line.split(options.separator))
                else:
                    for line in options.data.split("\n"):
                        value.append([line.lower(), line])
            except OptionSet.DoesNotExist:
                raise ValueError(f"OptionSet '{value}' does not exists")
        self._choices = self.widget.choices = value

    choices = property(_get_choices, _set_choices)
