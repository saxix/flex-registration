from rest_framework import serializers
from smart_register.core.models import FlexForm, FlexFormField, FormSet, OptionSet, CustomFieldType, Validator


class StrategyClassField(serializers.CharField):
    def to_representation(self, value):
        return f'{value.__module__}.{value.__name__}'


class ValidatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Validator
        exclude = ('id',)


class FlexFormFieldSerializer(serializers.ModelSerializer):
    field_type = StrategyClassField()
    validator = ValidatorSerializer(required=False, allow_null=True)

    class Meta:
        model = FlexFormField
        exclude = ('id', 'flex_form')


class FlexFormFormsetSerializer(serializers.ModelSerializer):
    fields = FlexFormFieldSerializer(many=True)
    base_type = StrategyClassField()
    validator = ValidatorSerializer(required=False, allow_null=True)

    class Meta:
        model = FlexForm
        exclude = ('id',)


class FormSetSerializer(serializers.ModelSerializer):
    flex_form = FlexFormFormsetSerializer()

    class Meta:
        model = FormSet
        exclude = ('id', 'parent')


class FlexFormSerializer(serializers.ModelSerializer):
    fields = FlexFormFieldSerializer(many=True)
    formsets = FormSetSerializer(many=True)
    base_type = StrategyClassField()
    validator = ValidatorSerializer(required=False, allow_null=True)

    class Meta:
        model = FlexForm
        exclude = ('id',)


class OptionSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptionSet
        exclude = ('id',)


class CustomFieldTypeSerializer(serializers.ModelSerializer):
    base_type = StrategyClassField()

    class Meta:
        model = CustomFieldType
        exclude = ('id',)


def dump_form_data(form):
    return {
        "form": FlexFormSerializer(form).data,
        'custom_field_types': CustomFieldTypeSerializer(CustomFieldType.objects.all(), many=True).data,
        'option_sets': OptionSetSerializer(OptionSet.objects.all(), many=True).data
    }

def import_from_data(data):
    form_data = data['form']
    custom_field_types_data = data['custom_field_types']
    option_sets_data = data['option_sets']
    custom_field_serializer = CustomFieldTypeSerializer(data=custom_field_types_data,many=True)
    custom_field_serializer.is_valid(raise_exception=True)
    custom_field_serializer.save()

    option_sets_serializer = OptionSetSerializer(data=option_sets_data,many=True)
    option_sets_serializer.is_valid(raise_exception=True)
    option_sets_serializer.save()

    form_serializer =FlexFormSerializer(data=form_data)
    form_serializer.is_valid(raise_exception=True)



def test_loads():
    import json
    d = json.loads(json.dumps(FlexFormSerializer(FlexForm.objects.first()).data))
    s = FlexFormSerializer(data=d)
    s.is_valid(raise_exception=True)
