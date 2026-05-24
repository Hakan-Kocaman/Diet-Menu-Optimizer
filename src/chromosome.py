import numpy as np


#BREAKFAST_SIZE  = 94      # ilk 94 > kahvalti
#EPSILON_UPPER   = 1.15    # üst sinir icin %15
#EPSILON_LOWER   = 0.90    # alt sinir icin %10 
#BREAKFAST_RATIO = 0.35    # kahvalti gunluk DRI'nin %35'i

#Veritabanindaki karsiliklari
#NUTRIENT_ENERGY   = 5
#NUTRIENT_PROTEIN  = 15
#NUTRIENT_CARB     = 8
#NUTRIENT_FIBER    = 4
#NUTRIENT_SODIUM   = 17

#Kahvalti parametreleri
#BREAKFAST_NUTRIENTS = [NUTRIENT_ENERGY, NUTRIENT_PROTEIN]
#Ogle/Aksam parametreleri
#ALL_NUTRIENTS = [NUTRIENT_ENERGY, NUTRIENT_PROTEIN,NUTRIENT_CARB, NUTRIENT_FIBER, NUTRIENT_SODIUM]

def decode(x, foods, nutrients, food_nutrients, dri, diversity=True, min_groups=8):

    

    food_id_list=list()
    food_id_list=list(foods.keys())

    #gelen float dizisinin kucukten buyuge siralanmis indeksleri
    index_sorted_x = np.argsort(x)
    
    permutation = []
    
    for i in index_sorted_x:
        food_id=food_id_list[i]
        permutation.append(food_id)

    breakfast_genes    = permutation[:94]   # ilk 94
    lunch_dinner_genes = permutation[94:]   # kalan 311

    #ust sınır: günlük RUL × 1.15 × 0.35
    energy_upper_bound = {}
    protein_upper_bound = {}
    energy_upper_bound  = dri[5]["RUL"]  * 1.15 * 0.35
    protein_upper_bound = dri[15]["RUL"] * 1.15 * 0.35
    
    #alt sınır: günlük RLL × 0.90 × 0.35
    energy_lower_bound = {}
    protein_lower_bound = {}
    energy_lower_bound  = dri[5]["RLL"]  * 0.90 * 0.35
    protein_lower_bound = dri[15]["RLL"] * 0.90 * 0.35
    
    


    breakfast_menu    = []    # seçilen yemekler buraya gidecek
    total_energy_breakfast    = 0.0   # kahvaltıda toplanan enerji
    total_protein_breakfast   = 0.0   # kahvaltıda toplanan protein
    for i in breakfast_genes:
        #atla(5,15 gibi sayılar aranıyor)
        if i not in food_nutrients:
            continue
        
        
        #gerekli makro alindiysa kahvalti sonlandirilir
        if total_energy_breakfast >= energy_lower_bound and total_protein_breakfast >= protein_lower_bound:
            break

        food_energy_breakfast = food_nutrients[i].get(5,0.0)
        food_protein_breakfast = food_nutrients[i].get(15,0.0)

        #yemek eklenirse besin degeri asilicak mi
        #eger ust sinir asiliyorsa o yemegi atla
        if total_energy_breakfast + food_energy_breakfast > energy_upper_bound or total_protein_breakfast + food_protein_breakfast > protein_upper_bound:
            continue
        breakfast_menu.append(i)
        total_energy_breakfast  += food_energy_breakfast
        total_protein_breakfast += food_protein_breakfast


    ########################################################################
    #Aksam ve Ogle
    energy_upper_bound = dri[5]["RUL"]  * 1.15
    protein_upper_bound = dri[15]["RUL"] * 1.15
    carb_upper_bound = dri[8]["RUL"]  * 1.15
    fiber_upper_bound = dri[4]["RUL"]  * 1.15
    sodium_upper_bound = dri[17]["RUL"] * 1.15

    energy_lower_bound  = dri[5]["RLL"]  * 0.90
    protein_lower_bound = dri[15]["RLL"] * 0.90
    carb_lower_bound    = dri[8]["RLL"]  * 0.90
    fiber_lower_bound   = dri[4]["RLL"]  * 0.90
    sodium_lower_bound  = dri[17]["RLL"] * 0.90

    lunch_dinner_menu=[]
    total_energy=total_energy_breakfast
    total_protein=total_protein_breakfast
    total_carb=0.0
    total_fiber=0.0
    total_sodium=0.0

    for i in lunch_dinner_genes:
        
        #atla(5,15 gibi sayılar aranıyor)
        if i not in food_nutrients:
            continue
        
        #tum makrolar alt siniri karsilarsa menu tamamlanir
        if total_energy >= energy_lower_bound and total_protein >= protein_lower_bound and total_carb >= carb_lower_bound and total_fiber >= fiber_lower_bound and total_sodium >= sodium_lower_bound:
            break

        food_energy = food_nutrients[i].get(5,0.0)
        food_protein = food_nutrients[i].get(15,0.0)
        food_carb = food_nutrients[i].get(8,0.0)
        food_fiber = food_nutrients[i].get(4,0.0)
        food_sodium = food_nutrients[i].get(17,0.0)


        #yemek eklenirse besin degeri asilicak mi
        #eger ust sinir asiliyorsa o yemegi atla
        if total_energy + food_energy > energy_upper_bound or total_protein + food_protein > protein_upper_bound or total_carb + food_carb > carb_upper_bound or total_fiber + food_fiber > fiber_upper_bound or total_sodium + food_sodium > sodium_upper_bound:
            continue

        lunch_dinner_menu.append(i)
        total_energy  += food_energy
        total_protein += food_protein
        total_carb    += food_carb
        total_fiber   += food_fiber
        total_sodium  += food_sodium

    menu = breakfast_menu + lunch_dinner_menu

    if diversity:
        present_groups = {foods[f]["foodGroupId"] for f in menu if f in foods}
        if len(present_groups) < min_groups:
            menu_set = set(menu)
            for food_id, food in foods.items():
                if len(present_groups) >= min_groups:
                    break
                gid = food["foodGroupId"]
                if gid not in present_groups and food_id not in menu_set:
                    menu.append(food_id)
                    menu_set.add(food_id)
                    present_groups.add(gid)
    total_nutrients = {
        5: total_energy,
        15: total_protein,
        8: total_carb,
        4: total_fiber,
        17: total_sodium}

    return menu, total_nutrients