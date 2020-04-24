from django.shortcuts import render
from .Serializers import MetricSerialiser
from .models import Metric
from django.db.models import Sum, FloatField, F
from rest_framework import viewsets


class Filter_by:
    def __init__(self, start_date, end_date, country, os, channel):
        self.date_from = start_date
        self.date_to = end_date
        self.country = country
        self.os = os
        self.channel = channel


# Create your views here.
class MetricViewSet(viewsets.ModelViewSet):
    serializer_class = MetricSerialiser

    def filter_metrics(self, filter_by, metrics):

        # Filter by date
        if filter_by.date_from is not None and filter_by.date_to is not None:
            metrics = metrics.filter(date__range=[filter_by.date_from, filter_by.date_to])
        elif filter_by.date_from is not None:
            metrics = metrics.filter(date__gte=filter_by.date_from)
        elif filter_by.date_to is not None:
            metrics = metrics.filter(date__lte=filter_by.date_to)

        # Filter by country

        if filter_by.country is not None:

            metrics = metrics.filter(country=filter_by.country.upper())

        # Filter by os
        if filter_by.os is not None:
            metrics = metrics.filter(os=filter_by.os)

        # Filter by channel
        if filter_by.channel is not None:
            metrics = metrics.filter(channel=filter_by.channel)

        return metrics

    def get_queryset(self):
        """
        get dataset after filters
        """

        # get all rquery params and set None if doesn't exist
        metrics = Metric.objects.all()
        date_from = self.request.query_params.get("date_from", None)
        date_to = self.request.query_params.get("date_to", None)
        country = self.request.query_params.get("country", None)
        os = self.request.query_params.get("os", None)
        channel = self.request.query_params.get("channel", None)
        sum_fields = self.request.query_params.get("sums", None)
        group_by = self.request.query_params.get("group_by", None)
        sort_value = self.request.query_params.get("sort_value", None)
        sort_direction = self.request.query_params.get("sort_direction", None)
        filter_by = Filter_by(date_from, date_to, country, os, channel)

        # filter by date, country, os, channel
        metrics_after_filter = self.filter_metrics(filter_by, metrics)

        # group_by filter
        if group_by is not None:
            group_by = group_by.split(",")
            metrics_after_filter = metrics_after_filter.values(*set(group_by))

        # sum filter
        if sum_fields is not None:
            sum_fields = sum_fields.split(",")

            for field_name in set(sum_fields):
                if field_name != "installs" or field_name != "spend":
                    metrics_after_filter = metrics_after_filter.annotate(**{field_name + "_sum": Sum((field_name))})

        # get cpi of all data
        metrics_after_filter = self.cpi_get(metrics_after_filter)
        # sum filter
        if sort_value is not None:
            if sort_direction == "desc":
                metrics_after_filter = metrics_after_filter.order_by("-" + sort_value)
            else:
                metrics_after_filter = metrics_after_filter.order_by(sort_value)

        # print query to check if query correct or not
        print(metrics_after_filter.query)

        return metrics_after_filter

    def cpi_get(self, metrics):
        # calculate CPI (cost per install) which is calculated as cpi = spend / installs
        return metrics.annotate(
            spend_sum=Sum("spend", output_field=FloatField()), installs_sum=Sum("installs", output_field=FloatField()),
        ).annotate(cpi=F("spend_sum") / F("installs_sum"))
