import json
import os
import re

transcript_path = r"C:\Users\azizn\.gemini\antigravity-ide\brain\3f724571-a08f-46af-8969-4924db01757d\.system_generated\logs\transcript_full.jsonl"

file_contents = {}

with open(transcript_path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            entry = json.loads(line)
        except Exception:
            continue
            
        if entry.get("source") != "MODEL" or entry.get("type") != "PLANNER_RESPONSE":
            continue
            
        # The tool calls are in entry["tool_calls"]
        tool_calls = entry.get("tool_calls", [])
        for call in tool_calls:
            name = call.get("name")
            args = call.get("arguments", {})
            
            # The tool name might be "default_api:write_to_file" or just "write_to_file"
            if "write_to_file" in name:
                target = args.get("TargetFile", "")
                basename = os.path.basename(target)
                if basename.startswith("test_") and basename.endswith(".py"):
                    content = args.get("CodeContent", "")
                    file_contents[basename] = content
                    print(f"Recovered {basename} via write_to_file")
                    
            elif "replace_file_content" in name and "multi" not in name:
                target = args.get("TargetFile", "")
                basename = os.path.basename(target)
                if basename in file_contents:
                    target_content = args.get("TargetContent", "")
                    replacement = args.get("ReplacementContent", "")
                    file_contents[basename] = file_contents[basename].replace(target_content, replacement)
                    print(f"Patched {basename} via replace_file_content")
                        
            elif "multi_replace_file_content" in name:
                target = args.get("TargetFile", "")
                basename = os.path.basename(target)
                if basename in file_contents:
                    chunks = args.get("ReplacementChunks", [])
                    for chunk in chunks:
                        target_content = chunk.get("TargetContent", "")
                        replacement = chunk.get("ReplacementContent", "")
                        file_contents[basename] = file_contents[basename].replace(target_content, replacement)
                    print(f"Patched {basename} via multi_replace_file_content")

for basename, content in file_contents.items():
    out_path = os.path.join(r"c:\Users\azizn\LabCast-AI\labcast-ai-backend\tests", basename)
    with open(out_path, "w", encoding="utf-8") as out_f:
        out_f.write(content)
    print(f"Wrote {out_path}")
