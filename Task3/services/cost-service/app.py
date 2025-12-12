from flask import Flask
import random
import time
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "cost_service"})
    )
)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://simplest-collector:4317",
    insecure=True
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)

@app.route("/")
def get_cost():
    with trace.get_tracer(__name__).start_as_current_span("cost_service"):
        delay = random.randint(1, 500) * 0.001
        time.sleep(delay)
        return str(random.randint(10000, 100000))