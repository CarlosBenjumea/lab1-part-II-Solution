import django_filters
from ..models import Invoice, Provider


class InvoiceFilter(django_filters.FilterSet):
    invoice_no = django_filters.CharFilter(lookup_expr="icontains")
    issued_on = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Invoice
        fields = ["invoice_no", "issued_on"]


class ProviderFilter(django_filters.FilterSet):
    has_barrels_to_bill = django_filters.BooleanFilter(
        method="filter_has_barrels_to_bill"
    )

    def filter_has_barrels_to_bill(self, queryset, name, value):
        if not value:
            return queryset

        return queryset.filter(barrels__billed=False).distinct()

    class Meta:
        model = Provider
        fields = ["has_barrels_to_bill"]
