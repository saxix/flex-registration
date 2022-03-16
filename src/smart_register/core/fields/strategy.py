from strategy_field.fields import StrategyClassField as StrategyClassField_
from strategy_field.utils import fqn


class StrategyClassField(StrategyClassField_):
    def value_to_string(self, obj):
        return fqn(self.value_from_object(obj))
