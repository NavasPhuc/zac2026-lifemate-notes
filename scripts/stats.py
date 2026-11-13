import json
from collections import Counter

# 1. Đọc tập train
with open("train/train.jsonl", encoding="utf-8") as f:
    data = [json.loads(line) for line in f if line.strip()]

# 2. Đọc catalog để biết tool nào là "read" hay "write"
with open("train/train_tools_catalog.json", encoding="utf-8") as f:
    catalog = json.load(f)
kind = {}
for app in catalog["apps"]:
    for tool in app["tools"]:
        kind[tool["name"]] = tool["kind"]

# 3. Các "bộ đếm"
so_lenh = Counter()      # đáp án có bao nhiêu lệnh -> bao nhiêu mẫu
dem_tool = Counter()     # mỗi tool xuất hiện bao nhiêu lần
dem_loai = Counter()     # read / write / meta
so_app = []              # số app cài sẵn của từng mẫu
create_co_list = 0       # alarm.create có kèm alarm.list
create_khong_list = 0    # alarm.create không kèm alarm.list

for d in data:
    calls = d["label"]["tool_calls"]
    names = [c["name"] for c in calls]
    so_lenh[len(calls)] += 1
    so_app.append(len(d["context"]["installed_apps"]))
    for n in names:
        dem_tool[n] += 1
        dem_loai[kind.get(n, "khong-ro")] += 1
    if "alarm.create" in names:
        if "alarm.list" in names:
            create_co_list += 1
        else:
            create_khong_list += 1

# 4. In kết quả
N = len(data)
print("Tổng số mẫu:", N)
print()
print("Số lệnh trong đáp án -> số mẫu:")
for k in sorted(so_lenh):
    print(f"   {k} lệnh: {so_lenh[k]} mẫu")
print()
print("Loại lệnh trong đáp án:", dict(dem_loai))
print(f"Số app cài sẵn mỗi mẫu: nhỏ nhất {min(so_app)}, "
      f"lớn nhất {max(so_app)}, trung bình {sum(so_app)/N:.1f}")
print()
print("15 tool hay gặp nhất:")
for ten, so in dem_tool.most_common(15):
    print(f"   {so:5d}  {ten}")
print()
print("Mẫu có alarm.create: có alarm.list đi kèm =", create_co_list,
      "| không có =", create_khong_list)

