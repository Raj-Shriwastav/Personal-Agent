# Agent

Not implemented yet. LangGraph is introduced in Phase 6, after the task system works.

Planned graph:

```text
START -> Understand Intent -> Retrieve Context -> Decide Action
                                                     |
                                    +----------------+---------------+
                                    v                                v
                                 Answer                        Execute Tool -> Validate
                                    |                                |
                                    +----------------+---------------+
                                                     v
                                                  Response -> END
```
