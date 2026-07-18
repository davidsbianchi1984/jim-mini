"""JIM-mini / Guardian — Networked Responsive Personal Guidance System.

A standalone personal-guidance product (patent app 19/038,196): it monitors a
user's biometric and contextual signals, detects known conditions, delivers
guidance, and escalates on critical events.

JIM-mini runs entirely on its own. When configured with a QRME endpoint it can
additionally run *in tandem* — delegating guidance for a condition to a QRME
specialist synthetic profile — but it never imports QRME code; the two products
interoperate only over HTTP.
"""

__version__ = "0.1.0"
