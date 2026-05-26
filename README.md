# Multi-Objective Diet Optimization Problem (MODP)

**FSMVU Faculty of Engineering – Computer Engineering**
BLM20364E / BLM22332E – Heuristic Optimization Algorithms | Term Project, 2026

---

## Overview

This project implements a personalized daily meal planning system modeled as a **Multi-Objective Multidimensional Knapsack Problem (MOMKP)**. It recommends optimal breakfast and lunch/dinner menus from a database of 405 prepared food items by simultaneously optimizing:

- **Maximizing** user food preference
- **Minimizing** total meal cost
- **Minimizing** meal preparation time

Four state-of-the-art Multi-Objective Evolutionary Algorithms (MOEAs) are implemented and compared: **NSGA-II**, **SPEA2**, **SMS-EMOA**, and **NSGA-III**.

---

## Authors

| Student ID     | Name                  |
|----------------|-----------------------|
| 2321021003     | Hakan Kocaman         |
| 2321021019     | Ahmet Uğurlu          |
| 2221221048     | Ahmet Mesut Yolcu     |
| 2121221022     | Muhammed Eren Koçkan  |
| Ç2025201009    | Hazal Beşire Turhan   |

**Supervisor:** Dr. Öğr. Cumali Türkmen

---

## Requirements

- **Python 3.14**
- **pymoo**

Install all dependencies:

```bash
pip install -r requirements.txt
```

### `requirements.txt`

```
pymoo
mysql-connector-python
numpy
matplotlib
pandas
```

---

## Database Setup

The project uses a **MySQL** database. Import the provided SQL dump before running:

```bash
mysql -u root -p diet_menu_optimizer < mysql.sql
```

Database connection details (configured in the project):

```python
host     = "localhost"
user     = "root"
password = "heuristic"
database = "diet_menu_optimizer"
```

### Schema Overview

| Table          | Key Columns                                              | Purpose                                          |
|----------------|----------------------------------------------------------|--------------------------------------------------|
| `foods`        | id, name, foodGroupId, cost, preference, preparingTime, cookingTime, co2 | Main food item list with objective values |
| `user_foods`   | userId, foodId, preference                               | Per-user preference ratings                      |
| `food_nutrients` | foodId, nutrientId, value                              | Nutritional content per food item                |
| `nutrients`    | id, name, unit                                           | Nutrient names and units                         |
| `dri`          | userId, nutrientId, RLL, RUL                             | Daily intake lower/upper bounds per user         |
| `food_group`   | id, name                                                 | 18 food groups for diversity calculation         |

---

## Running the Project

```bash
python src/main.py
```

---

## Project Structure

```
.
.
├── src/
│   ├── chromosome.py
│   ├── db.py
│   ├── fitness.py
│   ├── main.py
│   └── visualize.py
├── results/
│   ├── # plot.pngs
│   └── # .csvs
├── diet.sql
├── requirements.txt
└── README.md

```

---

## Problem Formulation

The optimization problem is defined as:

```
Minimize/Maximize:
  f1(x) = Σ xᵢ · preferenceᵢ        → MAX
  f2(x) = Σ xᵢ · costᵢ               → MIN
  f3(x) = Σ xᵢ · (prepTime + cookTime)ᵢ → MIN
  f4(x) = Σ xᵢ · co2ᵢ                → MIN

Subject to:
  RLL_j ≤ Σ xᵢ · nutrient(j,i) ≤ RUL_j    for j = 1..5
  xᵢ ∈ {0,1},   n = 405 food items
```

### Nutritional Constraints (DRI-based)

| # | Nutrient                   | Unit |
|---|----------------------------|------|
| C1 | Energy                    | kcal |
| C2 | Protein                   | g    |
| C3 | Carbohydrate              | g    |
| C4 | Fiber (Fiber_total_dietary) | g  |
| C5 | Sodium (Na)               | mg   |

Bounds include a ±10–15% tolerance:
- Upper bound: `effective_RUL = RUL × 1.15`
- Lower bound: `effective_RLL = RLL × 0.90`
- Breakfast split: `RLL_b = RLL × 0.35`, `RUL_b = RUL × 0.35`

### Penalty Function

```
For each nutrient j = 1..5, with menu total vⱼ:

  viol_low_j  = max(0, RLL_j − vⱼ) / (RUL_j − RLL_j)
  viol_high_j = max(0, vⱼ − RUL_j) / (RUL_j − RLL_j)

  R = 0.7 × Σ viol_low_j + 0.3 × Σ viol_high_j

  penalized_fitness = objective_value − λ × R
  (λ = penalty weight, start with λ = 1.0)
```

Food items with preference score `-1` are strictly forbidden and receive a very large penalty.

---

## Chromosome Representation

Chromosomes are permutations of food item indices split into two sections:

```
[ 12, 47, 3, 91, ... | 201, 88, 344, 77, ... ]
  ←── 94 breakfast foods ──→ ←── 311 lunch+dinner foods ──→
```

---

## Algorithms

| Algorithm  | Type            | Key Mechanism                                           |
|------------|-----------------|---------------------------------------------------------|
| NSGA-II    | Pareto-based    | Non-dominated sorting + Crowding distance               |
| SPEA2      | Pareto + Archive| Strength fitness + k-NN density + Archive truncation    |
| SMS-EMOA   | Indicator-based | Hypervolume contribution selection                      |
| NSGA-III   | Reference-point | Structured reference points on hyperplane               |

---

## User Profiles

| User | Profile        | Restriction                          |
|------|----------------|--------------------------------------|
| User 1 | Non-vegetarian | Fewer dietary restrictions         |
| User 2 | Vegetarian     | Meat-based items forbidden (pref = -1) |

---

## Experiments

| # | Experiment           | Description                                                  |
|---|----------------------|--------------------------------------------------------------|
| 1 | User comparison      | Run for both User 1 and User 2 — compare Pareto fronts      |
| 2 | Algorithm comparison | Run ≥ 2 algorithms with same parameters — compare results   |
| 3 | Diversity impact     | Run with and without diversity mechanism — compare menu variety |

---

## Evaluation Metrics

| Criterion             | Metric                                              |
|-----------------------|-----------------------------------------------------|
| Constraint compliance | How many of 5 nutrients are within DRI bounds?      |
| Preference quality    | Total preference score of selected foods            |
| Diversity             | Number of distinct food groups in the menu          |
| Objective values      | Cost / time / CO₂ depending on chosen objectives   |

Hypervolume reference point: worst observed value across all runs + 10% margin. All algorithms share the same reference point for comparability.