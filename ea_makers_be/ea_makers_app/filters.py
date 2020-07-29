import rest_framework_filters as filters

from ea_makers_be.ea_makers_app.models import Transaction


class TransactionFilter(filters.FilterSet):
    class Meta:
        model = Transaction
        fields = {
            'type': ['exact']
        }
