import json
from datetime import datetime


class AgentTraceParser:
    def __init__(self, trace_path: str):
        self.trace_path = trace_path
        self.in_tokens = 0
        self.out_tokens = 0
        self.steps = 0
        self.tool_calls = 0
        self.tool_errors = 0
        self.time_taken = 0

    def parse_trace(self):
        time_start = None
        time_end = None
        with open(self.trace_path, "r") as f:
            for line in f:
                entry = json.loads(line)
                cur_time = entry.get("timestamp")
                cur_time = datetime.strptime(cur_time, "%Y-%m-%d %H:%M:%S.%f")
                if time_start is None or cur_time < time_start:
                    time_start = cur_time
                if time_end is None or cur_time > time_end:
                    time_end = cur_time

                if entry.get("event") == "tool_start":
                    self.tool_calls += 1
                # TODO: there are some validation errors from MCP, also handle this
                elif entry.get("event") == "tool_error":
                    self.tool_errors += 1
                elif entry.get("event") == "llm_end":
                    self.steps += 1
                    usage_metadata = entry.get("usage_metadata", {})
                    self.in_tokens += usage_metadata.get("input_tokens", 0)
                    self.out_tokens += usage_metadata.get("output_tokens", 0)

        self.time_taken = (time_end - time_start).total_seconds() if time_start and time_end else 0
        return {
            "in_tokens": self.in_tokens,
            "out_tokens": self.out_tokens,
            "steps": self.steps,
            "tool_calls": self.tool_calls,
            "tool_errors": self.tool_errors,
            "time_taken": self.time_taken,
        }


if __name__ == "__main__":
    parser = AgentTraceParser(
        "/home/ubuntu/codes/LLM4NetLab/results/frr_down_localization/20251112210748_gpt-oss:20b_conversation.log"
    )
    res = parser.parse_trace()
    print(res)
