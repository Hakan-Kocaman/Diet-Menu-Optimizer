import os
output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(output_dir, exist_ok=True)

import numpy as np
import pandas as pd

from pymoo.optimize import minimize
from pymoo.core.problem import ElementwiseProblem 
from pymoo.operators.sampling.rnd import PermutationRandomSampling
from pymoo.operators.crossover.ox import OrderCrossover
from pymoo.operators.mutation.inversion import InversionMutation
from pymoo.indicators.hv import HV
from pymoo.util.ref_dirs import get_reference_directions
ref_dirs = get_reference_directions("das-dennis", 3, n_partitions=12)

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.algorithms.moo.spea2 import SPEA2
from pymoo.algorithms.moo.sms import SMSEMOA
from pymoo.algorithms.moo.nsga3 import NSGA3

from db import food_list, nutrient_list, food_nutrient_list, get_dri, get_user_preferences
from chromosome import decode
from fitness import fitness




class DietProblem(ElementwiseProblem):
    def __init__(self, user_id):
        super().__init__(n_var=405, n_obj=3, xl=0, xu=405)
        self.foods = food_list
        self.nutrients = nutrient_list
        self.food_nutrients = food_nutrient_list
        self.dri = get_dri(user_id)
        self.preferences = get_user_preferences(user_id)

    def _evaluate(self, X, out, *args, **kwargs):
        menu, totals = decode(X, self.foods, self.nutrients, self.food_nutrients, self.dri)
        values, info = fitness(menu, totals, self.foods, self.preferences, self.dri)
        out["F"] = values


# ── NON-VEGAN - USER 1 ──────────────────────────────────────────
problem_u1 = DietProblem(user_id=1)

algorithm= NSGA2(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u1_n2 = minimize(problem_u1, algorithm, ('n_gen', 200), verbose=True)
print("NSGA2:", len(result_u1_n2.F), "solution")

algorithm= SPEA2(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u1_s2 = minimize(problem_u1, algorithm, ('n_gen', 200), verbose=True)
print("SPEA2:", len(result_u1_s2.F), "solution")

algorithm= SMSEMOA(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u1_sms = minimize(problem_u1, algorithm, ('n_gen', 200), verbose=True)
print("SMSEMOA:", len(result_u1_sms.F), "solution")

algorithm= NSGA3(ref_dirs=ref_dirs, pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u1_n3 = minimize(problem_u1, algorithm, ('n_gen', 200), verbose=True)
print("NSGA3:", len(result_u1_n3.F), "solution")

# ── VEGAN - USER 2 ──────────────────────────────────────────
problem_u2 = DietProblem(user_id=2)

algorithm= NSGA2(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u2_n2 = minimize(problem_u2, algorithm, ('n_gen', 200), verbose=True)
print("NSGA2:", len(result_u2_n2.F), "solution")

algorithm= SPEA2(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u2_s2 = minimize(problem_u2, algorithm, ('n_gen', 200), verbose=True)
print("SPEA2:", len(result_u2_s2.F), "solution")

algorithm= SMSEMOA(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u2_sms = minimize(problem_u2, algorithm, ('n_gen', 200), verbose=True)
print("SMSEMOA:", len(result_u2_sms.F), "solution")

algorithm= NSGA3( ref_dirs=ref_dirs, pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u2_n3 = minimize(problem_u2, algorithm, ('n_gen', 200), verbose=True)
print("NSGA3:", len(result_u2_n3.F), "solution")

# ── KARŞILAŞTIRMA - REFERANS NOKTASI ──────────────────────────────────
all_F = np.vstack([result_u1_n2.F, result_u1_s2.F, result_u1_n3.F, result_u1_sms.F, result_u2_n2.F, result_u2_s2.F, result_u2_n3.F, result_u2_sms.F])
ref_point = np.max(all_F, axis=0) * 1.1

# ── KARŞILAŞTIRMA - HYPERVOLUME ─────────────────────────────────────
hv = HV(ref_point=ref_point)
print("u1_NSGA2 Hypervolume :", hv(result_u1_n2.F))
print("u1_SPEA2  Hypervolume :", hv(result_u1_s2.F))
print("u1_SMSEMOA Hypervolume :", hv(result_u1_sms.F))
print("u1_NSGA3 Hypervolume :", hv(result_u1_n3.F))

print("u2_NSGA2 Hypervolume :", hv(result_u2_n2.F))
print("u2_SPEA2   Hypervolume :", hv(result_u2_s2.F))
print("u2_SMSEMOA Hypervolume :", hv(result_u2_sms.F))
print("u2_NSGA3 Hypervolume :", hv(result_u2_n3.F))

# ── SONUÇLARI - CSV KAYDET ──────────────────────────────────────
pd.DataFrame(result_u1_n2.F, columns=["preference","cost","prepTime"]).to_csv(os.path.join(output_dir, "nsga-2_u1.csv"), index=False)
pd.DataFrame(result_u1_s2.F, columns=["preference","cost","prepTime"]).to_csv(os.path.join(output_dir, "spea-2_u1.csv"), index=False)
pd.DataFrame(result_u1_sms.F, columns=["preference","cost","prepTime"]).to_csv(os.path.join(output_dir, "smsemoa_u1.csv"), index=False)
pd.DataFrame(result_u1_n3.F, columns=["preference","cost","prepTime"]).to_csv(os.path.join(output_dir, "nsga-3_u1.csv"), index=False)

pd.DataFrame(result_u2_n2.F, columns=["preference","cost","prepTime"]).to_csv(os.path.join(output_dir, "nsga-2_u2.csv"), index=False)
pd.DataFrame(result_u2_s2.F, columns=["preference","cost","prepTime"]).to_csv(os.path.join(output_dir, "spea-2_u2.csv"), index=False)
pd.DataFrame(result_u2_sms.F, columns=["preference","cost","prepTime"]).to_csv(os.path.join(output_dir, "smsemoa_u2.csv"), index=False)
pd.DataFrame(result_u2_n3.F, columns=["preference","cost","prepTime"]).to_csv(os.path.join(output_dir, "nsga-3_u2.csv"), index=False)

