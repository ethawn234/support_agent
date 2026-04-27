Agent Response: ## Architecture for n8n → Dynatrace Telemetry (Self-Hosted)

### Evaluating Your Assumptions

Your assumption is **partially correct** but CosmosDB as an intermediary is not the best approach here. Th...

--- Response ---
## Architecture for n8n → Dynatrace Telemetry (Self-Hosted)

### Evaluating Your Assumptions

Your assumption is **partially correct** but CosmosDB as an intermediary is not the best approach here. The core problem is correct — you can't stream logs directly — but you have several better options that avoid an unnecessary database hop.

**Why CosmosDB-as-intermediary is suboptimal:**
- Adds cost, latency, and operational overhead
- Dynatrace doesn't natively "pull" from CosmosDB; you'd still need a forwarder/trigger (e.g., Azure Function or Logic App) on top of it
- You've added two hops and two integration surfaces instead of one

---

### Recommended Architecture Patterns (Best to Acceptable)

#### Option 1: OpenTelemetry Export (Best for Traces/Spans)
n8n added native OpenTelemetry support in newer versions (v1.x+). This is a **Community Edition feature** — not enterprise-only — and is the cleanest path.

```
n8n (OTLP export via env vars)
    → OpenTelemetry Collector
        → Dynatrace OTLP endpoint (https://{env}.live.dynatrace.com/api/v2/otlp)
```

Configure n8n with environment variables:
```env
N8N_DIAGNOSTICS_ENABLED=true
OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
OTEL_EXPORTER_OTLP_PROTOCOL=grpc
```

The OTel Collector then forwards to Dynatrace using the `otlphttp` exporter with a Dynatrace API token. This gives you workflow execution traces with timing, errors, and node-level spans.

---

#### Option 2: Dynatrace OneAgent on the Host (Best for Infrastructure Metrics + Logs)
If you're running n8n on a VM or bare-metal container host, install the **Dynatrace OneAgent** on that host. It automatically collects:
- Process-level CPU/memory metrics
- Log files (if n8n writes to a log file path)
- Container metrics (if using Docker)
- No code changes to n8n required

For Docker-based deployments, mount the log path and configure OneAgent log monitoring rules to pick up n8n's log output.

---

#### Option 3: n8n API Polling Service (Best for Execution-Level Business Metrics)
Run a lightweight scheduled poller (cron job, small service, or even another n8n workflow) that:

```
n8n REST API (/api/v1/executions, /api/v1/workflows)
    → Transform/enrich data
        → Dynatrace Log Ingestion API v2
        → Dynatrace Metrics Ingestion API v2
```

Dynatrace's ingest endpoints are simple HTTP POSTs:
- `POST https://{env}.live.dynatrace.com/api/v2/logs/ingest`
- `POST https://{env}.live.dynatrace.com/api/v2/metrics/ingest`

This approach is good for workflow success/failure rates, execution duration as business metrics, and error alerting — without touching n8n's internals.

---

#### Option 4: Error/Completion Hook in Each Workflow (Acceptable but Tedious)
Add an **HTTP Request node** at the end of each n8n workflow (and in a global error workflow) that POSTs directly to Dynatrace's Log or Events API. n8n supports a global **Error Workflow** setting that fires on any execution failure, so you can centralize at least the error path:

```
Any workflow failure → Global Error Workflow → HTTP Request → Dynatrace Events API
```

The downside is success-path telemetry still requires touching each workflow.

---

### When CosmosDB *Would* Make Sense

The CosmosDB-intermediary pattern is justified only if you need:
- A **durable audit log** for compliance (independent of Dynatrace retention)
- **Replay capability** if Dynatrace ingestion is down
- **Multi-consumer** fan-out (feeding both Dynatrace and another system from the same store)

In those cases, the pattern would be:

```
n8n → CosmosDB (via HTTP node or poller)
    → Azure Function (Change Feed trigger)
        → Dynatrace Log/Metrics API
```

But this is an edge case, not the default answer.

---

### Summary Recommendation

| Goal | Best Option |
|---|---|
| Low-effort infrastructure visibility | OneAgent on host |
| Workflow execution traces (distributed tracing) | OpenTelemetry export |
| Business metrics (success rates, durations) | API polling → Dynatrace Metrics API |
| Error alerting | Global Error Workflow → Dynatrace Events API |
| Durable audit + Dynatrace | CosmosDB + Change Feed → Dynatrace |

Start with **OneAgent + OpenTelemetry** — that combination covers the majority of observability needs with the least custom code.
