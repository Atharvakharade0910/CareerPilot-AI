# Stateful workflow boundary

Phase 1 executes upload -> document validation -> local extraction -> PostgreSQL transaction -> user review.

Phase 4 will use LangGraph with a PostgreSQL checkpointer and typed CareerAgentState. Resume text and job descriptions are untrusted data, never instructions. Read tools remain account-scoped. Mutating tool calls must record an audit event and validate evidence IDs. Human review is a durable interrupt. Only an explicit, version-bound approval may advance an application to a browser adapter.

No LangGraph graph, embeddings, provider calls or browser actions run in Phase 1.
