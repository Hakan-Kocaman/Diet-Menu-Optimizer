import numpy as np
import pandas as pd

from pymoo.optimize import minimize
from pymoo.core.problem import Problem
from pymoo.indicators.hv import HV

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.spea2 import SPEA2

from db import food_list, nutrient_list, food_nutrient_list, get_dri, get_user_preferences
from chromosome import decode
from fitness import fitness


class DietProblem(Problem):
    def __init__(self, user_id):
        super().__init__(n_var=405, n_obj=3, xl=0, xu=405)
        self.foods = food_list
        self.nutrients = nutrient_list
        self.food_nutrients = food_nutrient_list
        self.dri = get_dri(user_id)
        self.preferences = get_user_preferences(user_id)

    def _evaluate(self, X, out, *args, **kwargs):
        objectives = []
        for x in X:
            menu, totals = decode(x, self.foods, self.nutrients, self.food_nutrients, self.dri)
            values, info = fitness(menu, totals, self.foods, self.preferences, self.dri)
            objectives.append(values)

        out["F"] = np.array(objectives)


# ── USER 1 ──────────────────────────────────────────
problem_u1 = DietProblem(user_id=1)

result_u1_n = minimize(problem_u1, NSGA2(pop_size=100), ('n_gen', 200), verbose=True)
print("NSGA-II bitti:", len(result_u1_n.F), "çözüm")

result_u1_s = minimize(problem_u1, SPEA2(pop_size=100), ('n_gen', 200), verbose=True)
print("SPEA2 bitti:", len(result_u1_s.F), "çözüm")

# ── VEGAN - USER 2 ──────────────────────────────────────────
problem_u2 = DietProblem(user_id=2)

result_u2_n = minimize(problem_u2, NSGA2(pop_size=100), ('n_gen', 200), verbose=True)
print("NSGA-II bitti:", len(result_u2_n.F), "çözüm")

result_u2_s = minimize(problem_u2, SPEA2(pop_size=100), ('n_gen', 200), verbose=True)
print("SPEA2 bitti:", len(result_u2_s.F), "çözüm")

# ── KARŞILAŞTIRMA - REFERANS NOKTASI ──────────────────────────────────
all_F = np.vstack([result_u1_n.F, result_u1_s.F, result_u2_n.F])
ref_point = np.max(all_F, axis=0) * 1.1

# ── KARŞILAŞTIRMA - HYPERVOLUME ─────────────────────────────────────
hv = HV(ref_point=ref_point)
print("u1_NSGA-II Hypervolume :", hv(result_u1_n.F))
print("u1_SPEA2   Hypervolume :", hv(result_u1_s.F))
print("u2_NSGA-II Hypervolume :", hv(result_u2_n.F))
print("u2_SPEA2   Hypervolume :", hv(result_u2_s.F))

# ── SONUÇLARI - CSV KAYDET ──────────────────────────────────────
pd.DataFrame(result_u1_n.F, columns=["preference","cost","prepTime"]).to_csv("pareto_u1_n.csv", index=False)
pd.DataFrame(result_u1_s.F, columns=["preference","cost","prepTime"]).to_csv("pareto_u1_s.csv", index=False)
pd.DataFrame(result_u2_n.F, columns=["preference","cost","prepTime"]).to_csv("pareto_u2_n.csv", index=False)
pd.DataFrame(result_u2_s.F, columns=["preference","cost","prepTime"]).to_csv("pareto_u2_s.csv", index=False)