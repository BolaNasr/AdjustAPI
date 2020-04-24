from .models import Metric
from rest_framework import routers, serializers


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)
        fields_str = self.context["request"].query_params.get("fields")

        if fields_str:
            fields_str = fields_str.split(",")
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields_str)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class MetricSerialiser(DynamicFieldsModelSerializer, serializers.HyperlinkedModelSerializer):
    cpi = serializers.SerializerMethodField("getCPI")
    clicks = serializers.SerializerMethodField("getclick")
    impressions = serializers.SerializerMethodField("getimpressions")
    revenue = serializers.SerializerMethodField("getrevenue")

    def getCPI(self, metric):
        if type(metric) == dict:
            return metric["cpi"]
        return metric.cpi

    def getclick(self, metric):
        if type(metric) == dict:
            if metric.get("clicks_sum"):
                return metric.get("clicks_sum")
        elif hasattr(metric, "clicks_sum"):
            return metric.clicks_sum
        elif hasattr(metric, "clicks"):
            return metric.clicks
        return ""

    def getimpressions(self, metric):
        if type(metric) == dict:
            if metric.get("impressions_sum"):
                return metric.get("impressions_sum")
        elif hasattr(metric, "impressions_sum"):
            return metric.impressions_sum
        elif hasattr(metric, "impressions"):
            return metric.impressions
        return ""

    def getrevenue(self, metric):
        if type(metric) == dict:
            if metric.get("revenue_sum"):
                return metric.get("revenue_sum")
        elif hasattr(metric, "revenue_sum"):
            return metric.revenue_sum
        elif hasattr(metric, "revenue"):
            return metric.revenue
        return ""

    class Meta:
        model = Metric
        fields = (
            "country",
            "date",
            "os",
            "channel",
            "impressions",
            "clicks",
            "revenue",
            "cpi",
            "spend",
            "installs",
        )

