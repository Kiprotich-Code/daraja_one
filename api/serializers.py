from rest_framework import serializers


class DarajaC2BCallbackSerializer(serializers.Serializer):
    """Validates Daraja C2B callback payload.
    
    Official fields from Safaricom M-Pesa C2B API:
    https://developer.safaricom.co.ke/docs#c2b-api
    """
    TransactionType = serializers.CharField(required=True)
    TransID = serializers.CharField(required=True)
    TransTime = serializers.CharField(required=True)
    TransAmount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    BusinessShortCode = serializers.CharField(required=True)
    BillRefNumber = serializers.CharField(required=True)
    InvoiceNumber = serializers.CharField(required=False, allow_blank=True)
    MSISDN = serializers.CharField(required=True)
    FirstName = serializers.CharField(required=False, allow_blank=True)
    MiddleName = serializers.CharField(required=False, allow_blank=True)
    LastName = serializers.CharField(required=False, allow_blank=True)
    OrgAccountBalance = serializers.DecimalField(max_digits=15, decimal_places=2, required=False, allow_null=True)

    def validate_TransAmount(self, value):
        if value <= 0:
            raise serializers.ValidationError("TransAmount must be a positive number.")
        return value

    def validate(self, data):
        """Additional cross-field validation."""
        return data
