from decimal import Decimal
from rest_framework import serializers
from ..models import Provider, Barrel, Invoice, InvoiceLine

class BarrelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Barrel
        fields = ["id", "provider", "number", "oil_type", "liters", "billed"]


class ProviderSerializer(serializers.ModelSerializer):

    billed_barrels = serializers.SerializerMethodField()
    barrels_to_bill = serializers.SerializerMethodField()

    barrel_ids = serializers.PrimaryKeyRelatedField(
        source="barrels",
        many=True,
        read_only=True
    )

    class Meta:
        model = Provider
        fields = ["id", "name", "address", "tax_id","barrel_ids", "billed_barrels", "barrels_to_bill"]
        fields = ["id", "name", "address", "tax_id","liters_to_bill", "billed_barrels", "barrels_to_bill"]
    
    def get_billed_barrels(self, obj: Provider):
        barrels = obj.barrels.filter(billed=True)
        return BarrelSerializer(barrels, many=True).data

    def get_barrels_to_bill(self, obj: Provider):
        barrels = obj.barrels.filter(billed=False)
        return BarrelSerializer(barrels, many=True).data

class InvoiceLineNestedSerializer(serializers.ModelSerializer):
    # Requirement: return invoice lines WITHOUT the barrel object included.
    # We expose barrel_id only (not nested barrel details).
    barrel_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = InvoiceLine
        fields = ["id", "barrel_id", "liters", "description", "unit_price"]


class InvoiceLineCreateSerializer(serializers.Serializer):
    barrel = serializers.PrimaryKeyRelatedField(queryset=Barrel.objects.all())
    liters = serializers.IntegerField(min_value=1)
    description = serializers.CharField(max_length=255)
    unit_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    def create(self, validated_data: dict) -> InvoiceLine:
        invoice = self.context["invoice"]
        return invoice.add_line_for_barrel(
            barrel=validated_data["barrel"],
            liters=validated_data["liters"],
            unit_price_per_liter=validated_data["unit_price"],
            description=validated_data["description"],
        )


class InvoiceSerializer(serializers.ModelSerializer):
    lines = InvoiceLineNestedSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = ["id", "invoice_no", "issued_on", "lines", "total_amount"]
   
    def get_total_amount(self, obj: Invoice) -> Decimal:
        total = sum(line.liters * line.unit_price for line in obj.lines.all())
        return total
