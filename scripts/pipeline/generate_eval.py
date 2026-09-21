import os
import json

SYSTEM_PROMPT = "You are an elite Workspace Systems Architect. You master the ChaosNexus Anvil MCP. You autonomously discover and leverage capabilities provided by your workspace environment."

CORE_TASKS = [
    {
        "instruction": "Write a Rhai script to simulate writing an audit log. Safely use early returns if the action is empty.",
        "plugin_name": "audit_log",
        "tool_name": "cn_a_audit_log_run",
        "description": "Executes the audit_log Rhai script plugin.",
        "script_body": "fn write_audit_log(action) {\n    if action.is_empty() {\n        return;\n    }\n    write_file_string(\"audit.log\", action + \"\\n\");\n}\n\nwrite_audit_log(\"User logged in\");"
    },
    {
        "instruction": "Write a Rhai script to validate an incoming payload's schema compliance. It should read a payload from JSON and verify it has an 'id' field.",
        "plugin_name": "process_validation",
        "tool_name": "cn_a_process_validation_run",
        "description": "Executes the process_validation Rhai script plugin.",
        "script_body": "fn validate_payload() {\n    let payload_str = read_file_string(\"payload.json\");\n    if payload_str.is_empty() {\n        return;\n    }\n    let payload = parse_json(payload_str);\n    if !payload.contains_key(\"id\") {\n        return;\n    }\n    write_file_string(\"validation.log\", \"Valid\\n\");\n}\n\nvalidate_payload();"
    },
    {
        "instruction": "Write a Rhai script to aggregate some metrics from a SQL table. Sum up the values in the 'count' column.",
        "plugin_name": "metrics_aggregator",
        "tool_name": "cn_a_metrics_aggregator_run",
        "description": "Executes the metrics_aggregator Rhai script plugin.",
        "script_body": "fn run_metrics() {\n    let rows = cn_a__chaosdata_inspect_sql(\"SELECT count FROM system_metrics\");\n    if rows.is_empty() {\n        return;\n    }\n    let total = 0;\n    for row in rows {\n        total += row.count;\n    }\n    write_file_string(\"metrics_out.json\", total.to_string());\n}\n\nrun_metrics();"
    },
    {
        "instruction": "Write a Rhai script to fetch health data from a remote API. Return early if the request fails.",
        "plugin_name": "api_health_checker",
        "tool_name": "cn_a_api_health_checker_run",
        "description": "Executes the api_health_checker Rhai script plugin.",
        "script_body": "fn check_health() {\n    // ==========================================\n    // NARRATIVE EXPLANATION:\n    // We use http_get to fetch the health status and return early on any network failures.\n    // ==========================================\n    let res = http_get(\"https://api.example.com/health\");\n    if type_of(res) != \"()\" {\n        return;\n    }\n    print(\"Health check passed\");\n}\n\ncheck_health();"
    },
    {
        "instruction": "Write a Rhai script to hook into the 'on_user_login' event and log it. Return early if the event data is missing.",
        "plugin_name": "login_logger",
        "tool_name": "cn_a_login_logger_run",
        "description": "Executes the login_logger Rhai script plugin.",
        "script_body": "fn log_login(event_data) {\n    // ==========================================\n    // NARRATIVE EXPLANATION:\n    // We hook an event and make sure the data is valid before proceeding.\n    // ==========================================\n    if event_data.is_empty() {\n        return;\n    }\n    log_info(\"User logged in: \" + event_data);\n}\n\nhook_event(\"on_user_login\", \"log_login\");"
    },
    {
        "instruction": "Write a Rhai script to start a webhook server on port 8080 and route '/ping'. Early return if starting fails.",
        "plugin_name": "webhook_ping",
        "tool_name": "cn_a_webhook_ping_run",
        "description": "Executes the webhook_ping Rhai script plugin.",
        "script_body": "fn ping_route(req) {\n    return \"pong\";\n}\n\nfn init_webhook() {\n    // ==========================================\n    // NARRATIVE EXPLANATION:\n    // Starts a webhook server. If the server fails to bind, we exit gracefully.\n    // ==========================================\n    let srv = start_webhook_server(8080);\n    if type_of(srv) != \"()\" {\n        return;\n    }\n    route_webhook(srv, \"/ping\", \"ping_route\");\n}\n\ninit_webhook();"
    },
    {
        "instruction": "I need to use the 'notify' library for file watching in a plugin, but I don't know the functions. Fetch the documentation for it.",
        "plugin_name": "docs_notify",
        "tool_name": "cn_a_docs_notify_run",
        "description": "Executes the docs_notify Rhai script plugin.",
        "script_body": "fn fetch_notify_docs() {\n    // ==========================================\n    // NARRATIVE EXPLANATION:\n    // We fetch documentation autonomously by leveraging the proxied ChaosNexus Codex capabilities.\n    // ==========================================\n    let docs = cn_a__cn_c_search_docs(#{ library: \"notify\", query: \".*\" });\n    if type_of(docs) != \"()\" {\n        return;\n    }\n    print(docs);\n}\n\nfetch_notify_docs();"
    }
]

def create_core_response(task):
    response = "I will create a plugin with a Rhai script that adheres to DRY principles, uses early returns, and avoids global returns.\n\n```json\n{\n  \"tool\": \"cn_a_create_plugin\",\n  \"arguments\": {\n"
    response += f"    \"plugin_name\": \"{task['plugin_name']}\",\n"
    response += f"    \"tool_name\": \"{task['tool_name']}\",\n"
    response += f"    \"description\": \"{task['description']}\",\n"
    response += f"    \"script_body\": {json.dumps(task['script_body'])}\n"
    response += "  }\n}\n```\nPlease approve this plugin in ChaosNexus Forge."
    return response

def generate_jsonl(file_path, tasks):
    lines = []
    for t in tasks:
        response = create_core_response(t)
        
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": t["instruction"]},
            {"role": "assistant", "content": response}
        ]
        lines.append(json.dumps({"messages": messages}))
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

def generate_alpaca(file_path, tasks):
    items = []
    for t in tasks:
        response = create_core_response(t)
        
        items.append({
            "instruction": t["instruction"],
            "input": "",
            "output": response
        })
        
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)

def main():
    os.makedirs("core", exist_ok=True)
    
    generate_jsonl("core/eval.jsonl", CORE_TASKS)
    generate_alpaca("core/eval_alpaca.json", CORE_TASKS)
    
    print("Successfully generated eval datasets.")

if __name__ == "__main__":
    main()
