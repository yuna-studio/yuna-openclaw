---
name: firestore-logger
description: "Log agent events to Firestore"
metadata:
  openclaw:
    emoji: "🔥"
    events: ["agent", "tool", "message"]
    install:
      - id: local
        kind: local
        path: .
---

# Firestore Logger Hook

Logs agent events to Firestore `chat_logs` collection.
