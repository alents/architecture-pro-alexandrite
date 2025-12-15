from flask import Flask
import random
import time
import requests
from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor

trace.set_tracer_provider(
    TracerProvider(
        resource=Resource.create({SERVICE_NAME: "order_service"})
    )
)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://simplest-collector:4317",  # ✅ Работает через TCP в Docker
    insecure=True
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)
app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def order():
    with trace.get_tracer(__name__).start_as_current_span("order_service"):
        random_order_number = random.randint(1, 500)
        time.sleep(random_order_number*0.001) #задержка
        cost = requests.get("http://cost-service:8080").text
        return {'order_number': str(random_order_number), 'order_cost': cost}