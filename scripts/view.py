import json
import sys

with open("train/train.jsonl", encoding="utf-8") as f:
    data = [json.loads(line) for line in f if line.strip()]

start = int(sys.argv[1]) if len(sys.argv) > 1 else 0
count = int(sys.argv[2]) if len(sys.argv) > 2 else 5

for item in data[start:start + count]:
    ctx = item["context"]
    print("=" * 70)
    print("ID:", item["id"])
    print("Giờ hiện tại:", ctx["current_time"])
    print("Người nói:", item.get("audio_text"))
    print("Apps cài sẵn:", list(ctx["installed_apps"].keys()))

    hist = item.get("history", [])
    print("Số lượt history:", len(hist))
    for h in hist:
        print("   [history]", json.dumps(h, ensure_ascii=False)[:300])

    print("ĐÁP ÁN:")
    calls = item["label"]["tool_calls"]
    if not calls:
        print("   (rỗng: ngoài phạm vi)")
    for c in calls:
        print("   ", c["name"], json.dumps(c["arguments"], ensure_ascii=False))
