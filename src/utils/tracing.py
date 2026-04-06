import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, SpanExporter

logger = logging.getLogger("mcp-yahoo-stock")

class LogSpanExporter(SpanExporter):
    """Custom exporter that writes spans directly to our file logger."""
    def export(self, spans):
        for span in spans:
            logger.info(f"TRACE: {span.name} | Duration: {(span.end_time - span.start_time) / 1e9:.3f}s")

# Configure Tracer
provider = TracerProvider()
processor = BatchSpanProcessor(LogSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("mcp-yahoo-stock")
