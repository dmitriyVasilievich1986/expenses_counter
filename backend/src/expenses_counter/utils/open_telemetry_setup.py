"""OpenTelemetry setup for the FastAPI application."""

__all__ = ("setup_open_telemetry",)

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from expenses_counter.config import AppConfig


def setup_open_telemetry(app: FastAPI, app_config: AppConfig | None = None) -> None:
    """Set up OpenTelemetry tracing for a FastAPI application.

    This function configures the tracer provider with resource attributes,
    adds span processors for console and/or OTLP exporting based on the
    provided application settings, and instruments the FastAPI app for tracing.

    Args:
        app (FastAPI): The FastAPI application instance to be instrumented.
        app_config (AppConfig | None): Optional application settings to configure OpenTelemetry.
            If not provided, the settings will be fetched using AppConfig.get_or_create().

    Returns:
        None

    """
    config = app_config or AppConfig.get_or_create()

    resource = Resource.create({"service.name": config.info.name})

    tracer_provider = TracerProvider(resource=resource)

    if config.services.open_telemetry.enable_console:
        console_exporter = ConsoleSpanExporter()
        tracer_provider.add_span_processor(BatchSpanProcessor(console_exporter))

    if config.services.open_telemetry.endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=config.services.open_telemetry.endpoint, insecure=True)
        tracer_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    trace.set_tracer_provider(tracer_provider)
    FastAPIInstrumentor.instrument_app(app)
