"""
Module for configuring OpenTelemetry in a Django application.
"""

import os
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.django import DjangoInstrumentor

from opentelemetry.instrumentation.requests import RequestsInstrumentor


resource = Resource.create(attributes={
    "service.name": os.environ.get("OTEL_SERVICE_NAME", "drf-api"),
})

provider = TracerProvider(resource=resource)
trace.set_tracer_provider(provider)

otlp_exporter = OTLPSpanExporter(
    endpoint=os.environ.get(
        "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
    insecure=True,
)

span_processor = BatchSpanProcessor(otlp_exporter)
provider.add_span_processor(span_processor)

DjangoInstrumentor().instrument()
RequestsInstrumentor().instrument()
