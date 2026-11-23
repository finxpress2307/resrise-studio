import json
import os

queue_path = "D:/social media/resrise-studio/swarm_queue.json"
with open(queue_path, "r", encoding="utf-8") as f:
    queue = json.load(f)

day_items = [x for x in queue if "day_index" in x]

print(f"Total day items: {len(day_items)}")
for item in day_items:
    print(f"ID: {item['id']} | Day {item['day_index']:02d} | {item['account']:18s} | {item['pillar']} | {item['location']}")
