# subscriber-hook
to run
uv run uvicorn main:app --reload --workers 1

Functional (top 3)
- At-least-once delivery with idempotency per (event_id, endpoint).
- Retry with exponential backoff + jitter, with outcome rules: 2xx=success; 5xx/timeout/429=retry (honor Retry-After); most 4xx=terminal.
- 202 ACK after enqueue (don’t block on delivery); DLQ after max_attempts (or TTL).

Non-functional (top 3)
- Low-latency intake: quick enqueue + strict request timeout.
- Isolation & fairness: small per-endpoint concurrency cap (+ a global cap) so one bad subscriber can’t starve others.
- Observability: counters (enqueued/sent/success/retry/DLQ) and structured logs with event_id, endpoint, attempt, next_due.


Entities
EventRequest: event_id, type, correlation_id, payload
EventResponse: event_id, status, correlation_id, message?

SubscriberConfig: event_type -> subscriber_urls[]
heap_event: (due_time, event_id, subscriber_url, attempt, correlation_id, payload)

dedup-inflight and delivered: (eventid+subscriber_url)




Classification
- 200 -> success (remove)
- 5xx/timeout/connection/429 -> retryable (honor retry-after if present)
- Most 4xx -> Terminal (recordd + DLQ)
- Backoff: exponetial + jitter, with caps 

Request timeouts 3s
Max attempt: 4
base backoff: 0.5
Jitter: full/randomized
dedupe TTL: 24 hrs
429: honor after Retry


POST /events flow 
Receive {event_id, event_type, payload}.
Validate quickly → 400 for missing fields, wrong content-type, or payload too large (add a modest size cap).
Lookup subscribers for event_type. Decide now: if none, either 202 no-op (log “no subscribers”) or 422; just be consistent.
Expand to deliveries: for each subscriber config create a delivery tuple (event_id, endpoint, attempt=1, due_time=now, max_attempts, timeout, backoff params) and push to the min-heap.
ACK 202 only after enqueuing all tuples. (Optionally return a correlation id and “enqueued=K”.)



Worker pops item.
If due_time not reached → push back, sleep until soonest due.
Per-endpoint cap reached? → push back with a short delay.
Already delivered? → drop as no-op (count it).
Already in-flight? → push back briefly (avoid double-send).
Mark (event_id, endpoint) in-flight; send with timeout.
Classify:
2xx → clear in-flight; mark delivered (TTL); success counters.
4xx (terminal) or attempts exhausted → clear in-flight; DLQ; failure counters.
429/5xx/timeout and attempts remain → clear in-flight; compute next due_time (or use Retry-After); re-enqueue; retry counters.




