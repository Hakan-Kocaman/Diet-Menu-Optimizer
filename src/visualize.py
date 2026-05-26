import os
import numpy as np
import matplotlib.pyplot as plt
from pymoo.indicators.hv import HV

output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(output_dir, exist_ok=True)

ALGO_LABELS  = ["NSGA-2", "SPEA-2", "SMS-EMOA", "NSGA-3"]
USER_LABELS  = ["User-1 (Non-Vegan)", "User-2 (Vegan)"]
OBJ_LABELS   = ["Preference", "Cost", "Prep Time"]
COLORS       = ["red", "blue", "green", "yellow"]


# --- Pareto Front – 3-D scatter plot ---

def plot_pareto_3d(results_u1, results_u2):
    fig = plt.figure(figsize=(16, 6))
    fig.suptitle("Pareto Fronts – 3-D Objective Space", fontsize=14, fontweight="bold")

    for uid, results in enumerate([results_u1, results_u2]):
        ax = fig.add_subplot(1, 2, uid + 1, projection="3d")
        ax.set_title(USER_LABELS[uid], fontsize=11)
        for i, (res, label, color) in enumerate(zip(results, ALGO_LABELS, COLORS)):
            F = res.F
            ax.scatter(F[:, 0], F[:, 1], F[:, 2],
                       label=label, color=color, s=20, alpha=0.8)
        ax.set_xlabel(OBJ_LABELS[0], fontsize=8)
        ax.set_ylabel(OBJ_LABELS[1], fontsize=8)
        ax.set_zlabel(OBJ_LABELS[2], fontsize=8)
        ax.legend(fontsize=7)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "pareto_3d.png"), dpi=150)
    plt.show()
    plt.close()
    print("Saved: pareto_3d.png")


# --- Convergence Curve – HV vs Generation ---

def plot_convergence(histories_u1, histories_u2, ref_point):
    hv_calc = HV(ref_point=ref_point)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=False)
    fig.suptitle("Convergence – Hypervolume per Generation", fontsize=14, fontweight="bold")

    for uid, (ax, histories) in enumerate(zip(axes, [histories_u1, histories_u2])):
        ax.set_title(USER_LABELS[uid], fontsize=11)
        for history, label, color in zip(histories, ALGO_LABELS, COLORS):
            hv_vals = []
            for F in history:
                if F is not None and len(F) > 0:
                    try:
                        hv_vals.append(hv_calc(F))
                    except Exception:
                        hv_vals.append(np.nan)
                else:
                    hv_vals.append(np.nan)
            ax.plot(hv_vals, label=label, color=color, linewidth=1.8)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Hypervolume")
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "convergence.png"), dpi=150)
    plt.show()
    plt.close()
    print("Saved: convergence.png")


# --- 3. HV Bar Chart ---

def plot_hv_bar(hv_dict):
    """
    hv_dict : {"u1_NSGA2": value, "u1_SPEA2": value, ...}  (8 entries)
    """
    labels = list(hv_dict.keys())
    values = list(hv_dict.values())
    bar_colors = (COLORS * 2)[:len(labels)]

    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(labels, values, color=bar_colors, edgecolor="white", linewidth=0.8)
    ax.set_title("Hypervolume Comparison", fontsize=13, fontweight="bold")
    ax.set_ylabel("Hypervolume")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=30, ha="right", fontsize=9)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.01,
                f"{val:.4f}", ha="center", va="bottom", fontsize=8)

    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "hv_bar.png"), dpi=150)
    plt.show()
    plt.close()
    print("Saved: hv_bar.png")

# --- Diversity Karşılaştırması ---

def plot_diversity_comparison(result_with, result_without, decode_fn, foods, nutrients, food_nutrients, dri):
    def avg_groups(result):
        counts = []
        for x in result.X:
            menu, _ = decode_fn(x, foods, nutrients, food_nutrients, dri)
            g = len({foods[f]["foodGroupId"] for f in menu if f in foods})
            counts.append(g)
        return np.mean(counts), np.min(counts), np.max(counts)

    avg_w, min_w, max_w = avg_groups(result_with)
    avg_wo, min_wo, max_wo = avg_groups(result_without)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    fig.suptitle("Diversity Mechanism – With vs Without", fontsize=14, fontweight="bold")

    # ── Sol: Pareto front overlay (2D: preference vs cost)
    ax = axes[0]
    ax.scatter(result_with.F[:, 0],    result_with.F[:, 1],    color=COLORS[0], s=25, alpha=0.8, label="With Diversity")
    ax.scatter(result_without.F[:, 0], result_without.F[:, 1], color=COLORS[1], s=25, alpha=0.8, label="Without Diversity")
    ax.set_xlabel("Preference")
    ax.set_ylabel("Cost")
    ax.set_title("Pareto Front (Preference vs Cost)")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # ── Sağ: Group sayısı bar chart
    ax2 = axes[1]
    labels = ["With Diversity", "Without Diversity"]
    avgs   = [avg_w, avg_wo]
    mins   = [min_w, min_wo]
    maxs   = [max_w, max_wo]
    bars   = ax2.bar(labels, avgs, color=[COLORS[0], COLORS[1]], edgecolor="white", width=0.4)

    # min-max hata çubukları
    yerr_low  = [avgs[i] - mins[i] for i in range(2)]
    yerr_high = [maxs[i] - avgs[i] for i in range(2)]
    ax2.errorbar(labels, avgs, yerr=[yerr_low, yerr_high], fmt="none", color="black", capsize=6)

    for bar, val in zip(bars, avgs):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
                 f"avg: {val:.1f}", ha="center", fontsize=10)

    ax2.axhline(y=4, color="red", linestyle="--", linewidth=1.2, label="min_groups = 8")
    ax2.set_ylabel("Distinct Food Groups per Menu")
    ax2.set_title("Food Group Diversity")
    ax2.legend()
    ax2.grid(axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "diversity_comparison.png"), dpi=150)
    plt.show()
    plt.close()
    print("Saved: diversity_comparison.png")

# --- 5. Sample Menu Table ---

def plot_menu_table(result, decode_fn, foods, nutrients, food_nutrients, dri, n_samples=3, title="Sample Menus", filename="menu_table.png"):
    NUTRIENT_NAMES = {5: "Energy(kcal)", 15: "Protein(g)", 8: "Carb(g)", 4: "Fiber(g)", 17: "Sodium(mg)"}
    NUT_IDS = [5, 15, 8, 4, 17]

    F = result.F
    X = result.X
    n = len(F)
    idx = [0, n // 2, n - 1] if n >= 3 else list(range(n))
    idx = idx[:n_samples]

    rows = []
    col_headers = [" ", "Pref", "Cost", "Time", "Foods (top-5)", "Nutrients vs DRI"]

    for rank, i in enumerate(idx):
        menu, totals = decode_fn(X[i], foods, nutrients, food_nutrients, dri)
        top_foods = "\n".join([foods[f]["name"] for f in menu[:5]]) if menu else "—"

        nut_lines = []
        for nid in NUT_IDS:
            val = totals.get(nid, 0.0)
            rll = dri.get(nid, {}).get("RLL", "?")
            rul = dri.get(nid, {}).get("RUL", "?")
            flag = " ✓" if isinstance(rll, (int, float)) and rll <= val <= rul else " ✗"
            nut_lines.append(f"{NUTRIENT_NAMES[nid]}: {val:.0f} [{rll}–{rul}]{flag}")
        groups = len({foods[f]["foodGroupId"] for f in menu if f in foods})

        rows.append([f"#{rank+1}", f"{F[i,0]:.2f}", f"{F[i,1]:.2f}", f"{F[i,2]:.0f}",
                     top_foods, "\n".join(nut_lines) + f"\nGroups: {groups}"])

    fig, ax = plt.subplots(figsize=(22, 3 + n_samples * 2.2))
    ax.axis("off")
    tbl = ax.table(cellText=rows, colLabels=col_headers, cellLoc="center", loc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(7.5)
    tbl.scale(1, 5.5)

    col_widths = [0.05, 0.08, 0.08, 0.08, 0.30, 0.35]
    for (row, col), cell in tbl.get_celld().items():
        cell.set_width(col_widths[col])
        if col in (4, 5):
            cell.set_text_props(ha="left", wrap=True)

    for col in range(len(col_headers)):
        tbl[0, col].set_facecolor(color="blue")
        tbl[0, col].set_text_props(color="white", fontweight="bold")

    ax.set_title(title, fontsize=12, fontweight="bold", pad=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, filename), dpi=150, bbox_inches="tight")
    plt.show()
    plt.close()
    print("Saved: " + filename)

# --- run plots ---

def run_all(
    results_u1, results_u2,           # each: [nsga2, spea2, sms, nsga3]
    histories_u1, histories_u2,       # each: [nsga2_hist, spea2_hist, sms_hist, nsga3_hist]
    ref_point,                        # (3,) array
    hv_dict,                          # {"u1_NSGA2": hv, ...}
    decode_fn=None,                   # optional, needed for menu table
    foods=None, nutrients=None,
    food_nutrients=None, dri_u1=None , dri_u2=None, results_nodiv=None
    ):
    plot_pareto_3d(results_u1, results_u2)
    plot_convergence(histories_u1, histories_u2, ref_point)
    plot_hv_bar(hv_dict)

    if decode_fn is not None:
        plot_menu_table(
            results_u1[0], decode_fn, foods, nutrients, food_nutrients, dri_u1,
            title="Sample Menus – User-1, NSGA-2", filename="menu_table_u1_nsga2.png"
        )
        plot_menu_table(
            results_u2[0], decode_fn, foods, nutrients, food_nutrients, dri_u2 or dri_u1,
            title="Sample Menus – User-2, NSGA-2", filename="menu_table_u2_nsga2.png"
        )
    if results_nodiv is not None and decode_fn is not None:
        plot_diversity_comparison(
            result_with=results_u1[0],
            result_without=results_nodiv,
            decode_fn=decode_fn,
            foods=foods,
            nutrients=nutrients,
            food_nutrients=food_nutrients,
            dri=dri_u1,
        )
    print("\nAll plots saved to: Diet-Menu-Optimizer/results")

