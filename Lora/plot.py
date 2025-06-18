import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# 创建画布
fig, ax = plt.subplots(figsize=(10, 6))
ax.set_axis_off()

# 定义节点位置
positions = {
    "Start": (0.1, 0.8),
    "DataPrep": (0.25, 0.8),
    "LoRA": (0.4, 0.8),
    "LoadModel": (0.55, 0.8),
    "ConfigTrain": (0.7, 0.8),
    "Train": (0.85, 0.8),
    "SaveCheckpoint": (0.85, 0.6),
    "Inference": (0.7, 0.4),
    "Eval": (0.55, 0.4),
    "End": (0.4, 0.4),
}

# 绘制节点
for name, (x, y) in positions.items():
    rect = mpatches.FancyBBoxPatch((x - 0.05, y - 0.03), 0.1, 0.06,
                                   boxstyle="round,pad=0.03",
                                   edgecolor="black",
                                   facecolor="#d0f0c0")
    ax.add_patch(rect)
    plt.text(x, y, name, ha='center', va='center')

# 绘制箭头
edges = [
    ("Start", "DataPrep"),
    ("DataPrep", "LoRA"),
    ("LoRA", "LoadModel"),
    ("LoadModel", "ConfigTrain"),
    ("ConfigTrain", "Train"),
    ("Train", "SaveCheckpoint"),
    ("SaveCheckpoint", "Inference"),
    ("Inference", "Eval"),
    ("Eval", "End"),
]

for src, dst in edges:
    x1, y1 = positions[src]
    x2, y2 = positions[dst]
    plt.arrow(x1 + 0.05, y1, x2 - x1 - 0.05, 0, head_width=0.015, length_includes_head=True, color='black')

plt.xlim(0, 1)
plt.ylim(0, 1)
plt.title("Financial Strategy Code Generation Flow")
plt.show()