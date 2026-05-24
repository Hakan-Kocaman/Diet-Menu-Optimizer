import os
output_dir = os.path.join(os.path.dirname(__file__), '..', 'results')
os.makedirs(output_dir, exist_ok=True)

import numpy as np
import pandas as pd

from pymoo.optimize import minimize
from pymoo.core.problem import ElementwiseProblem
from pymoo.core.callback import Callback
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
import visualize


# --- Callback to track F history during optimization ---
class FHistoryCallback(Callback):
    def __init__(self):
        super().__init__()
        self.F_history = []

    def notify(self, algorithm):
        F = algorithm.opt.get("F")
        if F is not None and len(F) > 0:
            self.F_history.append(F.copy())
        else:
            self.F_history.append(None)


# ---- Problem Definition and Optimization ----
class DietProblem(ElementwiseProblem):
    def __init__(self, user_id, diversity=True):
        super().__init__(n_var=405, n_obj=3, xl=0, xu=405)
        self.foods = food_list
        self.nutrients = nutrient_list
        self.food_nutrients = food_nutrient_list
        self.diversity = diversity
        self.dri = get_dri(user_id)
        self.preferences = get_user_preferences(user_id)

    def _evaluate(self, X, out, *args, **kwargs):
        menu, totals = decode(X, self.foods, self.nutrients, self.food_nutrients, self.dri, self.diversity)
        values, info = fitness(menu, totals, self.foods, self.preferences, self.dri)
        out["F"] = values


# -------NON-VEGAN - USER 1 ----------------------------------------------------------------------------------------------------------------------------------------
problem_u1 = DietProblem(user_id=1)

cb = FHistoryCallback()
algorithm = NSGA2(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u1_n2 = minimize(problem_u1, algorithm, ('n_gen', 200), verbose=True, callback=cb)
u1_n2_history = cb.F_history
print("NSGA2:", len(result_u1_n2.F), "solution")

cb = FHistoryCallback()
algorithm = SPEA2(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u1_s2 = minimize(problem_u1, algorithm, ('n_gen', 200), verbose=True, callback=cb)
u1_s2_history = cb.F_history
print("SPEA2:", len(result_u1_s2.F), "solution")

cb = FHistoryCallback()
algorithm = SMSEMOA(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u1_sms = minimize(problem_u1, algorithm, ('n_gen', 200), verbose=True, callback=cb)
u1_sms_history = cb.F_history
print("SMSEMOA:", len(result_u1_sms.F), "solution")

cb = FHistoryCallback()
algorithm = NSGA3(ref_dirs=ref_dirs, pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u1_n3 = minimize(problem_u1, algorithm, ('n_gen', 200), verbose=True, callback=cb)
u1_n3_history = cb.F_history
print("NSGA3:", len(result_u1_n3.F), "solution")
# ----------------------------------------------------------------------------------------------------------------------------------------------------------

# -------VEGAN - USER 2 ----------------------------------------------------------------------------------------------------------------------------------------
problem_u2 = DietProblem(user_id=2)

# User 2 NSGA2
cb = FHistoryCallback()
algorithm = NSGA2(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u2_n2 = minimize(problem_u2, algorithm, ('n_gen', 200), verbose=True, callback=cb)
u2_n2_history = cb.F_history
print("NSGA2:", len(result_u2_n2.F), "solution")

# User 2 SPEA2
cb = FHistoryCallback()
algorithm = SPEA2(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u2_s2 = minimize(problem_u2, algorithm, ('n_gen', 200), verbose=True, callback=cb)
u2_s2_history = cb.F_history
print("SPEA2:", len(result_u2_s2.F), "solution")

# User 2 SMSEMOA
cb = FHistoryCallback()
algorithm = SMSEMOA(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u2_sms = minimize(problem_u2, algorithm, ('n_gen', 200), verbose=True, callback=cb)
u2_sms_history = cb.F_history
print("SMSEMOA:", len(result_u2_sms.F), "solution")

# User 2 NSGA3
cb = FHistoryCallback()
algorithm = NSGA3(ref_dirs=ref_dirs, pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u2_n3 = minimize(problem_u2, algorithm, ('n_gen', 200), verbose=True, callback=cb)
u2_n3_history = cb.F_history
print("NSGA3:", len(result_u2_n3.F), "solution")

# --------------------------------------------------------------------------------------------------------------------------------------------------------------

# --- Compute Hypervolume (Reference point for all 4 algorithms) ---
all_F = np.vstack([
    result_u1_n2.F, result_u1_s2.F, result_u1_n3.F, result_u1_sms.F,
    result_u2_n2.F, result_u2_s2.F, result_u2_n3.F, result_u2_sms.F,
])
ref_point = np.max(all_F, axis=0) * 1.1

hv = HV(ref_point=ref_point)
hv_dict = {
    "u1_NSGA2":   hv(result_u1_n2.F),
    "u1_SPEA2":   hv(result_u1_s2.F),
    "u1_SMSEMOA": hv(result_u1_sms.F),
    "u1_NSGA3":   hv(result_u1_n3.F),
    "u2_NSGA2":   hv(result_u2_n2.F),
    "u2_SPEA2":   hv(result_u2_s2.F),
    "u2_SMSEMOA": hv(result_u2_sms.F),
    "u2_NSGA3":   hv(result_u2_n3.F),
}

for key, val in hv_dict.items():
    print(f"{key} Hypervolume : {val}")


# --- Save results to CSV ---
pd.DataFrame(result_u1_n2.F,  columns=["preference", "cost", "prepTime"]).to_csv(os.path.join(output_dir, "nsga-2_u1.csv"),   index=False)
pd.DataFrame(result_u1_s2.F,  columns=["preference", "cost", "prepTime"]).to_csv(os.path.join(output_dir, "spea-2_u1.csv"),   index=False)
pd.DataFrame(result_u1_sms.F, columns=["preference", "cost", "prepTime"]).to_csv(os.path.join(output_dir, "smsemoa_u1.csv"),  index=False)
pd.DataFrame(result_u1_n3.F,  columns=["preference", "cost", "prepTime"]).to_csv(os.path.join(output_dir, "nsga-3_u1.csv"),   index=False)

pd.DataFrame(result_u2_n2.F,  columns=["preference", "cost", "prepTime"]).to_csv(os.path.join(output_dir, "nsga-2_u2.csv"),   index=False)
pd.DataFrame(result_u2_s2.F,  columns=["preference", "cost", "prepTime"]).to_csv(os.path.join(output_dir, "spea-2_u2.csv"),   index=False)
pd.DataFrame(result_u2_sms.F, columns=["preference", "cost", "prepTime"]).to_csv(os.path.join(output_dir, "smsemoa_u2.csv"),  index=False)
pd.DataFrame(result_u2_n3.F,  columns=["preference", "cost", "prepTime"]).to_csv(os.path.join(output_dir, "nsga-3_u2.csv"),   index=False)

# --- Diversity Comparison (NSGA2 with vs without diversity) ---
problem_u1_nodiv = DietProblem(user_id=1, diversity=False)

cb = FHistoryCallback()
algorithm = NSGA2(pop_size=100, sampling=PermutationRandomSampling(), crossover=OrderCrossover(), mutation=InversionMutation(), eliminate_duplicates=True)
result_u1_n2_nodiv = minimize(problem_u1_nodiv, algorithm, ('n_gen', 200), verbose=True, callback=cb)
print("NSGA2 (no diversity):", len(result_u1_n2_nodiv.F), "solution")


# --- Visualization ---

visualize.run_all(
    results_u1=[result_u1_n2, result_u1_s2, result_u1_sms, result_u1_n3],
    results_u2=[result_u2_n2, result_u2_s2, result_u2_sms, result_u2_n3],
    histories_u1=[u1_n2_history, u1_s2_history, u1_sms_history, u1_n3_history],
    histories_u2=[u2_n2_history, u2_s2_history, u2_sms_history, u2_n3_history],
    ref_point=ref_point,
    hv_dict=hv_dict,
    decode_fn=decode,
    foods=problem_u1.foods,
    nutrients=problem_u1.nutrients,
    food_nutrients=problem_u1.food_nutrients,
    dri_u1=problem_u1.dri,
    dri_u2=problem_u2.dri,
    results_nodiv=result_u1_n2_nodiv
)