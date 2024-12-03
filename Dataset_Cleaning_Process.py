# -*- coding: utf-8 -*-
"""babi.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/13Wspd_HFGJdtp2ZXO47_eUWismbupKHL

#Data Utuh
"""

import numpy as np
import pandas as pd
import re

#klo ada yang error skip aja
#kasi nama kolom
df = pd.read_csv('recipes_82k.csv')

#liat kolom
df.info()

#hapus kolom kategori (banyak yg null soale)
df = df.drop(columns=['category'])

#hapus cuisine
df = df.drop(columns=['cuisine'])

#cek lg bro hbs dihapus
df.head()

#hapus data yang tagsnya null
df=df[df['tags'].notnull()]

#hapus data yang servingnya null
df=df[df['serves'].notnull()]

#hapus data yang gak punya ingredients
df=df[df['ingredients']!="[]"]

#hapus data yang prep timenya 0 menit
df=df[df['prep_time']!="0 minutes"]

#hapus yang gak punya preptime
df=df[df['prep_time'].notnull()]

#replace di servers yang ada kata servings nya, simpen integernya aja
df['serves'] = df['serves'].str.extract(r'(\d+)') #manfaatin regex, cuman ambil digit aja

#isi data yang serves nya null jadi 1
df['serves'] = df['serves'].fillna(1)

df.head()

df.info()

#daftar tags yang dimau
labels=['gluten free','dairy free','keto recipes','vegetarian',
        'low carb','paleo','high fiber','dairy recipes','low sodium',
        'low-cholesterol','low-fat','nut recipes','egg','low-calorie',
        'diabetes-friendly']

#buat semua values yang di tags jadi lowercase
df['tags'] = df['tags'].str.lower()

#buat pattern pake regex
#pake tanda or biar bisa syaratnya join salah satu aja
pattern = '|'.join([f'{label}' for label in labels])

#buat ngembaliin semua value tags yang ditemukan di regex, not only the first one
#jd yg gak ada di tags bakal diapus
df['tags'] = df['tags'].str.findall(pattern)

#hapus value yang tagsnya kosong
df=df[df['tags']!="[]"]

#ubah smua ingredients jd lowercase
df['ingredients']=df['ingredients'].str.lower()

df.head()

df.info()

df['cooking_method'] = df['cooking_method'].astype(str)
df['cooking_method']=df['cooking_method'].replace("[]","")

#hapus yang ""
df = df[df['cooking_method'] != ""]

print(type(df['tags'].iloc[0])) #jadi iterate aja trs yg kosong di drop

#hapus row yg 'tags' nya kosong atau []
df = df[df['tags'].apply(lambda x: len(x) > 0)]

df.info()

#regex buat jam & menit
pattern_hours = r"(\d+)H" #match digit sblm H
pattern_minutes = r"(\d+)M" #match digit sblm M

#convert the ISO 8601 format -> minutes
def update_tag(tag):
    print(f"Original tag: {tag}")
    minutes = 0

    #hapus 'P0Y0M0D' & 'S'
    tag_clean = re.sub(r'd+M\d+D', '', tag)

    print(f"Cleaned tag: {tag_clean}")

    #cari 'hours'
    match_hours = re.search(pattern_hours, tag_clean)
    match_minutes = re.search(pattern_minutes, tag_clean)

    if match_hours:
        #convert hours -> minutes
        hours = int(match_hours.group(1))  #ambil digit sblm 'H'
        minutes += hours * 60

    if match_minutes:
        #klo nemu menit, tambahan ke total menit
        minutes += int(match_minutes.group(1))  #ambil digit sblm 'M'

    #return angkanya
    #kalo ga nemu apa2, return original tag
    return f"{minutes} minutes" if minutes > 0 else tag

#balikin ke row 'prep_time'
df['prep_time'] = df['prep_time'].apply(update_tag)

df['serves']=df['serves'].astype(str)
df['serves']=df['serves'].replace("0","1")

df.head(10)

#cara convert ke csv
# df.to_csv('menghapus kesialan list.csv', index=False)

df.drop(8, inplace=True)
df.head(10)

df.iloc[14371]

"""# SPLIT INGREDIENTS -> QUANTITY, NAME, INGREDIENTS"""

#HAPUS SMUA YANG ADA DI DALAM KURUNG PAKE REGEX
df['ingredients'] = df['ingredients'].str.replace(r'\s*\([^)]*\)', '', regex=True)

import re
import ast

def extract_ingredients(ingredients_list):
    if isinstance(ingredients_list, str):  #cek apakah list e berbentuk string
        try:
            ingredients_list = ast.literal_eval(ingredients_list)
        except (ValueError, SyntaxError):
          #buat yg isi stringnya bkn list
          return [{'quantity': None, 'unit': None, 'name': ingredients_list}]

    labels = [
    'tablespoon', 'tablespoons', 'cup', 'cloves', 'large', 'medium', 'lbs', 'small',
    'teaspoon', 'teaspoons', 'cups', 'tsp', 'tbsp', 'sheets', 'pounds',
    'ounce', 'ounces', 'ounches', 'carton', 'oz', 'pound', 'clove', 'gram', 'kg',
    'inch', 'lb', 'g', 'liter', 'liters', 'milliliter', 'milliliters', 'fluid ounce',
    'fl oz', 'gallon', 'gallons', 'quart', 'quarts', 'pint', 'pints', 'cup', 'cups',
    'slice', 'slices', 'packet', 'packets', 'jar', 'jars', 'box', 'boxes', 'bag',
    'bags', 'can', 'cans', 'bottle', 'bottles', 'stick', 'sticks', 'piece', 'pieces',
    'pinch', 'pinches', 'dash', 'dashes', 'drop', 'drops', 'grain', 'grains', 'mg',
    'milligram', 'microgram', 'micrograms', 'teaspoonful', 'tablespoonful', 'quart',
    'quart', 'oz', 'pint', 'block', 'blocks', 'sheet', 'sheets', 'clove', 'head',
    'heads', 'bunch', 'bunches', 'pound', 'pounds', 'can', 'cans', 'container', 'containers',
    'carton', 'cartons', 'tube', 'tubes', 'packet', 'packets', 'bag', 'bags', 'cupboard', 'cupboards'
    ]

    updated_ingredients = []
    for ingredient in ingredients_list:
        #search unitnya
        potential_units = [word for word in re.findall(r"(?i)\b\w+\b", ingredient) if word.lower() in labels]

        if potential_units:
            #join semua unit yg ditemukan
            unit = ' '.join(potential_units)

            #cari index first unit di ingredient
            first_unit_index = ingredient.find(potential_units[0])

            #extract quantity sblm first unit itu
            quantity = ingredient[:first_unit_index].strip()

            #extract semua setelah the last unit
            name_start_index = ingredient.index(potential_units[-1]) + len(potential_units[-1])
            name = ingredient[name_start_index:].strip()
        else:
            quantity = None
            unit = None
            name = ingredient

        updated_ingredients.append({
            "quantity": quantity,
            "unit": unit,
            "name": name
        })

    return updated_ingredients

df['updated_ingredients'] = df['ingredients'].apply(lambda x: extract_ingredients(x))

import pandas as pd
import ast

def word_to_num(word):
    word = word.lower()
    words = word.replace('-', ' ').replace(' and ', ' ').split()

    units = {
        'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9,
        'ten': 10, 'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15, 'sixteen': 16,
        'seventeen': 17, 'eighteen': 18, 'nineteen': 19
    }
    tens = {
        'twenty': 20, 'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70, 'eighty': 80, 'ninety': 90
    }
    scales = {'hundred': 100, 'thousand': 1000, 'million': 1000000, 'billion': 1000000000}

    current_num = 0
    result = 0

    for w in words:
        if w in units:
            current_num += units[w]
        elif w in tens:
            current_num += tens[w]
        elif w in scales:
            result += current_num * scales[w]
            current_num = 0
        else:
            return None #invalid

    return result + current_num

def convert_quantity(quantity):
    if quantity is None:
        return None

    words = quantity.split()
    new_quantity = []
    for word in words:
        #convert quantity yg bentuknya string, bkn angka
        #cek apa ada yg bkn angka --> cek jg desimal & pecahan
        if not word.replace('.', '', 1).isdigit() and not word.replace('/', '', 1).isdigit():
            num = word_to_num(word)
            if num is not None:
              #convert jdi int & add '*'
                new_quantity.append(str(int(num)) + '*')
            else:
                new_quantity.append(word)
        else:
            new_quantity.append(word)  #simpen kata awal

    return ' '.join(new_quantity)

def kalikan_quantity(quantity):
    if quantity and '*' in quantity:
        try:
            #pisahin angka sebelum dan sesudah '*'
            angka1, angka2 = quantity.split('*')
            angka1 = float(angka1) #ubah ke numerik
            angka2 = float(angka2) #ubah ke numerik
            hasil = angka1 * angka2
            return str(int(hasil)) #ubah kembali ke string, dalam bentuk int
        except ValueError:
            return quantity  #klo error, return quantity asli
    else:
        return quantity  #return quantity asli klo gaada '*'

#iterasi tiap row di dataframe
for index, row in df.iterrows():
    #akses kolom 'updated_ingredients'
    updated_ingredients = row['updated_ingredients']

    #iterasi list di dlm kolom 'updated_ingredients'
    for i, ingredient in enumerate(updated_ingredients):
        #akses nilai 'quantity' dari tiap dictionary
        quantity = ingredient['quantity']

        #kalo ada tanda '-' di quantity, ambil teks sebelum tanda '-' & update nilai di dataframe
        if quantity and '-' in quantity:
            quantity = quantity.split('-')[0].strip()
            df.at[index, 'updated_ingredients'][i]['quantity'] = quantity
        if quantity and 'about' in quantity:
            quantity = quantity.split('about')[0].strip()
            df.at[index, 'updated_ingredients'][i]['quantity'] = quantity

        #ubah number in natural language jadi angka int & tambahin '*'
        df.at[index, 'updated_ingredients'][i]['quantity'] = convert_quantity(quantity)
df.head(10)

for index, row in df.iterrows():
    #akses kolom 'updated_ingredients'
    updated_ingredients = row['updated_ingredients']

    for i, ingredient in enumerate(updated_ingredients):
        #akses nilai 'quantity' dari tiap dictionary
        quantity = ingredient['quantity']

        #ubah number in natural language jadi angka int & tambahin '*'
        df.at[index, 'updated_ingredients'][i]['quantity'] = convert_quantity(quantity)
df.head(10)

def extract_garlic_info(ingredient):
    quantity = ingredient['quantity']
    if quantity and 'garlic' in quantity.lower():
        words = quantity.lower().split()
        for i, word in enumerate(words):
            if word == 'garlic':
                if i > 0:
                    try:
                        qty = convert_quantity(words[i-1]) #convert kata sblm jadi angka
                        ingredient['quantity'] = qty
                        ingredient['name'] = 'garlic'
                        break #klo udh nemu garlic, stop
                    except:
                        pass
    return ingredient

for index, row in df.iterrows():
    #akses kolom 'updated_ingredients'
    updated_ingredients = row['updated_ingredients']

    #iterasi pada list di dlm kolom 'updated_ingredients'
    for i, ingredient in enumerate(updated_ingredients):
        #ambil info garlic
        df.at[index, 'updated_ingredients'][i] = extract_garlic_info(ingredient)
df.head(10)

for index, row in df.iterrows():
    #akses kolom 'updated_ingredients'
    updated_ingredients = row['updated_ingredients']

    for i, ingredient in enumerate(updated_ingredients):
        #akses nilai 'quantity' dari setiap dictionary
        quantity = ingredient['quantity']
        #kaliin angka kalo ada tanda '*'
        quantity = kalikan_quantity(quantity)
        df.at[index, 'updated_ingredients'][i]['quantity'] = quantity
df.head(5)

print(type(df['updated_ingredients'][0]))

df.iloc[20]

def convert_fraction_to_float(fraction):
    #cek apakah pecahannya itu string
    if not isinstance(fraction, str):
        return fraction  #klo ga, return original form nya

    #cek apakah pecahane mix sama number (misal '16 1/2')
    if re.match(r'^\d+\s\d+/\d+$', fraction):
        #split number & pecahannya
        whole, frac = fraction.split()
        numerator, denominator = frac.split('/')
        #convert jdi float
        return float(whole) + (float(numerator) / float(denominator))

    #cek apakah pecahane, pecahan biasa (misal '1/2')
    elif re.match(r'^\d+/\d+$', fraction):
        numerator, denominator = fraction.split('/')
        return float(numerator) / float(denominator)

    #klo bkn pecahan return original form
    try:
        return float(fraction)
    except ValueError:
        return fraction

for index, row in df.iterrows():
    #akses row 'updated_ingredients'
    updated_ingredients = row['updated_ingredients']

    #iterasi setiap item di row itu
    for i, ingredient in enumerate(updated_ingredients):
        #akses 'quantity' di tiap dictionary
        quantity = ingredient['quantity']

        #convert jdi float
        updated_ingredients[i]['quantity'] = convert_fraction_to_float(quantity)

    #update
    df.at[index, 'updated_ingredients'] = updated_ingredients

# print(df.head(10))

df['updated_ingredients'].iloc[20125]

#hapus nama ingredients yang kotor >> hapus or sama things after comma
def clean_name_field(ingredient):
    #akses 'name' dari dictionary di kolom 'ingredient'
    name = ingredient.get('name', '')

    #hapus or
    #strip() buat hapus spasi di blkg / depan
    name = re.sub(r'\bor\b', '', name).strip()

    #hapus from
    name = re.sub(r'\bfrom\b', '', name).strip()

    #hapus semua stelah koma pertama & hapus komanya jg
    name = re.sub(r',.*$', '', name).strip()

    #hapus extra space di dalam
    name = re.sub(r'\s+', ' ', name)

    ingredient['name'] = name
    return ingredient

for index, row in df.iterrows():
    updated_ingredients = row['updated_ingredients']

    for i, ingredient in enumerate(updated_ingredients):
        updated_ingredients[i] = clean_name_field(ingredient)

    df.at[index, 'updated_ingredients'] = updated_ingredients

print(df.head(10))

df['updated_ingredients'].iloc[20125]

#kalo quantity '', replace sama '1.0'
df['updated_ingredients'] = df['updated_ingredients'].apply(lambda x: [{'quantity': 1.0, 'unit': item['unit'], 'name': item['name']} if item['quantity'] == '' else item for item in x])

df['updated_ingredients'].iloc[20125]

def update_quantity_from_name(ingredient):
    #akses name
    name = ingredient.get('name', '')

    #cek apakah huruf pertama dari name itu angka
    match = re.match(r'(\d+)\s+(.*)', name)

    if match:
        #split quantity & name
        quantity = float(match.group(1)) #convert ke float
        rest_of_name = match.group(2)

        ingredient['quantity'] = quantity

        ingredient['name'] = rest_of_name.strip()

    return ingredient

for index, row in df.iterrows():
    updated_ingredients = row['updated_ingredients']

    for i, ingredient in enumerate(updated_ingredients):
        updated_ingredients[i] = update_quantity_from_name(ingredient)

    df.at[index, 'updated_ingredients'] = updated_ingredients

df['updated_ingredients'].iloc[5]

#biar gampang buat konversinya, kita pake p inflect HAHA >> buat ubah unitnya jadi singular huwe
!pip install inflect

import inflect

p = inflect.engine()

for index, row in df.iterrows():
    updated_ingredients = row['updated_ingredients']

    for i, ingredient in enumerate(updated_ingredients):
        #klo name nya plural, convert jdi singular
        if(ingredient['unit'] is not None):
            singular_name = p.singular_noun(ingredient['unit'])
            if singular_name:
              updated_ingredients[i]['unit'] = singular_name
        else:
            updated_ingredients[i]['unit'] = ingredient['unit']

    df.at[index, 'updated_ingredients'] = updated_ingredients

df['updated_ingredients'].iloc[20125]

def remove_rows_with_invalid_quantity(df):
    def valid_quantities(ingredients):
        return all(
            isinstance(ingredient.get('quantity'), float) or ingredient.get('quantity') is None
            for ingredient in ingredients
        )

    return df[df['updated_ingredients'].apply(valid_quantities)]

#hapus baris yg quantity ga valid
df = remove_rows_with_invalid_quantity(df)

df.head(50)

#df.to_csv('kinclong.csv',index=False)
df.to_csv('dataset kinclong(tikom).csv', sep=';', index=False)

import pandas as pd
import json
import random
from datetime import datetime, timedelta

#simpen name & id
ingredient_dict = {}

id_counter = 1

for index, row in df.iterrows():
    updated_ingredients = row['updated_ingredients']
    for ingredient in updated_ingredients:
        if ingredient['name'] not in ingredient_dict:
            ingredient_dict[ingredient['name']] = id_counter
            id_counter += 1

#bikin ingredient list dari ingredient_dict
ingredient_list = [{"ingredient_id": id, "ingredient_name": name} for name, id in ingredient_dict.items()]

categories = [
    {"category_id": 1, "category_name": "gluten free"},
    {"category_id": 2, "category_name": "keto recipes"},
    {"category_id": 3, "category_name": "dairy free"},
    {"category_id": 4, "category_name": "vegetarian"},
    {"category_id": 5, "category_name": "low carb"},
    {"category_id": 6, "category_name": "paleo"},
    {"category_id": 7, "category_name": "high fiber"},
    {"category_id": 8, "category_name": "dairy recipes"},
    {"category_id": 9, "category_name": "low sodium"},
    {"category_id": 10, "category_name": "low-cholesterol"},
    {"category_id": 11, "category_name": "low-fat"},
    {"category_id": 12, "category_name": "nut recipes"},
    {"category_id": 13, "category_name": "egg"},
    {"category_id": 14, "category_name": "low-calorie"},
    {"category_id": 15, "category_name": "diabetes-friendly"}
]

#dummy data
users = [{"user_id": 1, "name": "Alice", "email": "alice@gmail.com","password":"alice",
          "profile_picture":"https://picsum.photos/200"},
           {"user_id": 2, "name": "Bob", "email": "bob@gmail.com","password":"bob",
          "profile_picture":"https://picsum.photos/200"}]

recipes = []
recipe_has_category = []
recipe_has_ingredient = []

#bkin dictionary buat mapping ingredient names ke id nya
ingredient_name_to_id = {ingredient['ingredient_name']: ingredient['ingredient_id'] for ingredient in ingredient_list}

for index, row in df.iterrows():
    recipe_id = index + 1
    recipe = {
        "recipe_id": recipe_id,
        "name_recipe": row["recipe_name"],
        "serves": row["serves"],
        "prep_time": row["prep_time"],
        "image": row["image"],
        "cooking_method": row["cooking_method"],
    }

    for ingredient in row["updated_ingredients"]:
        ingredient_name = ingredient["name"]
        ingredient_id = ingredient_name_to_id.get(ingredient_name.lower())

        if ingredient_id:
            recipe_has_ingredient.append({
                "recipe_id_recipe": recipe_id,
                "ingredient_id_ingredient": ingredient_id,
                "stock": ingredient["quantity"],
                "unit": ingredient["unit"]
            })

    for tag in row["tags"]:
        for category in categories:
            if category["category_name"].lower() in tag.lower():
                recipe_has_category.append({
                    "recipe_id_recipe": recipe_id,
                    "category_id_category": category["category_id"]
                })

    recipes.append(recipe)

#bkin user-ingredient yg bridging sama dummy data
user_has_ingredient = []
for user in users:
    for ingredient in ingredient_list:
        stock = random.randint(1, 10) #random stok
        expiry_date = datetime.today() + timedelta(days=random.randint(1, 30)) #random exp data
        user_has_ingredient.append({
            "user_id_user": user["user_id"],
            "ingredient_id_ingredient": ingredient["ingredient_id"],
            "stock": stock,
            "unit":"gram",
            "ingredients_pic":"https://picsum.photos/200",
            "place":"refrigerator",
            "buy_date": datetime.today().strftime('%Y-%m-%d'),
            "expiry_date": expiry_date.strftime('%Y-%m-%d')
        })

#gabung data jdi JSON
# db_structure = {
#     "recipes": recipes,
#     "ingredients": ingredient_list,
#     "users": users,
#     "categories": categories,
#     "recipe_has_category": recipe_has_category,
#     "recipe_has_ingredient": recipe_has_ingredient,
#     "inventory": user_has_ingredient
# }
db_structure = {
    "recipes": recipes
}

#save jdi JSON
with open('recipes.json', 'w') as json_file:
    json.dump(db_structure, json_file, default=str, indent=4)

print("Data has been saved to 'db-ml-pink.json'.")

df['prep_time'].iloc[3001]

"""#Bersihin Ingredients RIIL MIN"""

import pandas as pd
import re

#PERTAMA HAPUS DULU YANG DI DALAM KURUNG
ds=pd.read_csv('dataset_training.csv')

#HAPUS SMUA YANG ADA DI DALAM KURUNG PAKE REGEX
ds['ingredients'] = ds['ingredients'].str.replace(r'\s*\([^)]*\)', '', regex=True)

ds.head()

print(type(ds['ingredients'].iloc[10025]))

def clean_ingredient(item):
    #hapus semua setelah suatu koma di tiap item
    cleaned_item = item.split(',')[0]
    return cleaned_item

def clean_serving_suggestions_and_commas(ingredients_list):
    #clean tiap item di list
    cleaned_list = [clean_ingredient(item) for item in ingredients_list]

    #hapus item yg start with "serving suggestions:"
    cleaned_list = [item for item in cleaned_list if not item.lower().startswith("serving suggestions:")]

    return cleaned_list

#apply function ke tiap item di kolom 'ingredients'
ds['ingredients'] = ds['ingredients'].apply(lambda x: clean_serving_suggestions_and_commas(eval(x)) if isinstance(x, str) else x)

print(ds['ingredients'].iloc[0])

print(ds['ingredients'].iloc[1718])

labels = [
    'chopped', 'diced', 'minced', 'sliced', 'trimmed', 'grated', 'crushed', 'peeled', 'ground',
    'cubed', 'finely', 'coarsely', 'shredded', 'mashed', 'pounded', 'blanched', 'steamed',
    'baked', 'roasted', 'sauteed', 'battered', 'whisked', 'toasted', 'pressed', 'crumbled', 'fresh',
    'seeded', 'and', 'or','from','for','the','pinch','of','to','each'
]

#regex buat detect labels & koma
pattern = re.compile(r'\b(?:' + '|'.join(re.escape(label) for label in labels) + r')\b|,')

def clean_ingredient(ingredient):
    cleaned = pattern.sub('', ingredient)
    #remove spasi
    return ' '.join(cleaned.split()).strip()

def process_ingredients(ingredient_list):
    return [clean_ingredient(ingredient) for ingredient in ingredient_list]

#apply clearning ke kolom 'ingredients'
#asumsi kolom isinya string list, jdi di convert dlu ke list -> clean -> convert balik
ds['ingredients'] = ds['ingredients'].apply(
    lambda x: process_ingredients(eval(x)) if isinstance(x, str) else process_ingredients(x)
)

print(ds['ingredients'].iloc[10025])

#HABIS NI BRU SPLITTING DGN BAIK DAN BENAR
#COBA HAPUSS
labels= [
    'tablespoon', 'tablespoons', 'cup', 'cloves', 'large', 'medium', 'lbs', 'teaspoon',
    'teaspoons', 'cups', 'tsp', 'tbsp', 'sheets', 'pounds', 'pinch', 'small', 'ounce',
    'ounces', 'ounches', 'thin', 'each', 'strips', 'pieces', 'carton', 'oz', 'pound',
    'clove', 'gram', 'kg', 'sliced', 'inch', 'lb', '/', 'of', 'about', 'new', 'plus',
    'diced', 'enough', 'cover eggs', 'can', '-', ':', '%', '*', 'g', 'to', 'whole',
    'fresh', 'chopped', 'cut', 'into', 'optional', 'cans', 'minced', 'peeled','piece',
    'crushed','steam','for','the'

    'ml', 'milliliter', 'milliliters', 'l', 'liter', 'liters',
    'g', 'gram', 'grams', 'kg', 'kilogram', 'kilograms',
    'fl oz', 'fluid ounce', 'fluid ounces',
    'ripe', 'raw', 'cooked', 'boiled', 'steamed', 'roasted',
    'organic', 'non-organic', 'farmed', 'wild',
    'bake', 'fry', 'grill', 'roast', 'steam', 'cook',
    'serve', 'season', 'mix', 'stir', 'combine', 'blend', 'whisk',
    'bring', 'heat', 'drain', 'pour',
    'pack', 'jar', 'can', 'bottle',
    'dash', 'splash', 'shot', 'freshly','trimmed',
    'few', 'some', 'many', 'several', 'all',
    'top', 'bottom', 'side','boneless','for'

    'halved', 'quartered', 'finely', 'coarsely', 'finely chopped',
    'chopped', 'diced', 'sliced', 'minced', 'julienned', 'grated', 'shredded', 'ground',
    'peeled', 'whole', 'sliced', 'thin', 'thick', 'sliced', 'julienned','freshly',

    #hapus angka skalian
    'one','two','three','four','five','six','seven','eight','nine','ten',
    'eleven','twelve','thirteen','fourteen','fifteen','sixteen','seventeen','eighteen','nineteen'
]

import pandas as pd
import re

#ini ak taro luar soale klo ditaro dalam dif dee di call trs tiap looping & itu luamaaaa pollllll
label_pattern = re.compile(r'\b(?:' + '|'.join(map(re.escape, labels)) + r')\b')

def clean_ingredient(ingredient, labels):
    #haous text dalem ()
    ingredient = re.sub(r'\(.*?\)', '', ingredient)

    #hapus one, two, dll
    ingredient = re.sub(r'\b\d+(\.\d+)?\b', '', ingredient)

    #hapus label tak diinginkan
    ingredient = label_pattern.sub('', ingredient)

    #hapus punctuation
    ingredient = re.sub(r'[^\w\s]', '', ingredient)

    #hapus ekstra space
    ingredient = re.sub(r'\s+', ' ', ingredient)

    return ingredient.strip()

#apply function ke tiap item di ingredients & hapus yg kosong
ds['ingredients'] = ds['ingredients'].apply(lambda ingredients: [cleaned for ingredient in ingredients if (cleaned := clean_ingredient(ingredient, labels))])

print(ds['ingredients'].iloc[10025])

#ubah semua isinya jadi lowercase lah biar ez waktu diproses >> tengs gemini codenya muach
ds['ingredients'] = ds['ingredients'].apply(lambda ingredients: [ingredient.lower() for ingredient in ingredients])

print(ds['ingredients'].iloc[31467])

#ubah semua yg plural jadi singular buat ngurangin kompleksitas data
!pip install inflect #also available in kotlin

import pandas as pd
import inflect

p = inflect.engine()

def convert_to_singular(ingredient):
    singular_ingredient = [p.singular_noun(word) or word for word in ingredient.split()]
    return ' '.join(singular_ingredient)

#apply fungsi ke tiap row di kolom 'ingredients'
ds['ingredients'] = ds['ingredients'].apply(lambda row: [convert_to_singular(ingredient) for ingredient in row])

print(ds['ingredients'].iloc[1])

numbers = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten']

def remove_number(ingredient):
    pattern = r'\b(?:' + '|'.join(numbers) + r')\b'

    #replace one, two, dll jdi empty string
    return re.sub(pattern, '', ingredient).strip()

#apply fungsi ke tiap row di kolom 'ingredients'
ds['ingredients'] = ds['ingredients'].apply(lambda row: [remove_number(ingredient) for ingredient in row])

print(ds['ingredients'].iloc[310])

ds.to_csv('semoga lancar.csv',index=False)

"""#REVISIAN CLEANING, AMIN LEBIH GAMPANGG"""

import pandas as pd

#PERTAMA HAPUS DULU YANG DI DALAM KURUNG
ds=pd.read_csv('dataset_training.csv')

#HAPUS SMUA YANG ADA DI DALAM KURUNG PAKE REGEX
ds['ingredients'] = ds['ingredients'].str.replace(r'\s*\([^)]*\)', '', regex=True)

ds.head()

import re
#pisah yang ada kata and nya jadi 2 item

def format_ingredients(text):
    #ganti 'and' dengan '","'
    modified_text = re.sub(r'\s*and\s*', '' , '', text)
    return f'"{modified_text}"'

ds['ingredients'] = ds['ingredients'].apply(format_ingredients)

print(ds['ingredients'].iloc[10025])

#regex buat hapus "serving" atau "suggestion"
pattern = r'\b(serving|suggestion)\b'

#filter item yg mengandung pattern
filtered_data = [item for item in ds['ingr'] if not re.search(pattern, item, re.IGNORECASE)]

print(filtered_data)

"""##nanti"""

ds['ingredients']=ds['ingredients'].astype(str)

ds['ingredients']=ds['ingredients'].str.replace('[', '')
ds['ingredients']=ds['ingredients'].str.replace(']', '')

ds['ingredients']=ds['ingredients'].str.replace("'", "")

#kita ubah ke bentuk list biar bisa diiterate >> displit berdasarkan tanda ,
ds['ingredients'] = ds['ingredients'].apply(lambda x: x.split(','))