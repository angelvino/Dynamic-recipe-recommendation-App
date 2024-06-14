import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Label
from PIL import Image, ImageTk

# Connect to the SQLite database
conn = sqlite3.connect('tamilnadu_snacks.db')
cursor = conn.cursor()

# Create tables
cursor.execute('''
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    instructions TEXT NOT NULL,
    nutrition TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS ingredients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    image_url TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS recipe_ingredients (
    recipe_id INTEGER,
    ingredient_id INTEGER,
    quantity TEXT,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id INTEGER,
    FOREIGN KEY (recipe_id) REFERENCES recipes(id)
)
''')

# Insert sample data into recipes
recipes = [
    ("Murukku", "1. Mix rice flour and urad dal flour.\n2. Add sesame seeds, ajwain, and salt.\n3. Add water and knead into a dough.\n4. Use a murukku press to shape the dough.\n5. Deep fry until golden brown.", "Calories: 200 per piece"),
    ("Adai", "1. Soak rice and lentils separately for 2 hours.\n2. Grind with red chilies, fennel, and ginger.\n3. Add salt, chopped onions, and curry leaves.\n4. Heat a tawa and pour a ladle of batter.\n5. Cook until golden brown on both sides.", "Calories: 150 per piece"),
    ("Sundal", "1. Soak chickpeas overnight.\n2. Pressure cook until soft.\n3. Heat oil, add mustard seeds, and let it splutter.\n4. Add urad dal, dried red chilies, and curry leaves.\n5. Add cooked chickpeas, salt, and grated coconut. Mix well.", "Calories: 120 per serving")
    # Add up to 20 recipes here
]

cursor.executemany('''
INSERT INTO recipes (name, instructions, nutrition) VALUES (?, ?, ?)
''', recipes)

# Insert sample data into ingredients
ingredients = [
    ("Rice Flour", "D:\\python\\recipes\\rice_flour.jpeg"),
    ("Urad Dal Flour", "D:\\python\\recipes\\urad_daal.jpeg"),
    ("Sesame Seeds", "D:\\python\\recipes\\sesame.jpeg"),
    ("Ajwain", "D:\\python\\recipes\\ajwain.jpeg"),
    ("Chickpeas", "D:\\python\\recipes\\chick_peas.jpeg"),
    ("Red Chilies", "D:\\python\\recipes\\red_chillies.jpeg"),
    ("Coconut", "D:\\python\\recipes\\cocunut.jpeg"),
    ("Ginger", "D:\\python\\recipes\\ginger.jpeg"),
    ("Fennel", "D:\\python\\recipes\\fennel.jpeg")
    # Add up to 20 ingredients here
]

cursor.executemany('''
INSERT INTO ingredients (name, image_url) VALUES (?, ?)
''', ingredients)

# Insert sample data into recipe_ingredients
recipe_ingredients = [
    (1, 1, "2 cups"),
    (1, 2, "1 cup"),
    (1, 3, "1 tbsp"),
    (1, 4, "1 tsp"),
    (2, 1, "1 cup"),
    (2, 2, "1 cup"),
    (2, 6, "2-3"),
    (2, 9, "1 tsp"),
    (2, 8, "1 inch"),
    (3, 5, "1 cup"),
    (3, 7, "2 tbsp"),
    (3, 3, "1 tsp")
]

cursor.executemany('''
INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity) VALUES (?, ?, ?)
''', recipe_ingredients)

# Commit the changes
conn.commit()

# Function to display ingredient images
def show_ingredient_images(ingredient_names):
    top = Toplevel()
    top.title("Ingredient Images")
    
    for name in ingredient_names:
        cursor.execute('SELECT image_url FROM ingredients WHERE LOWER(name) = ?', (name.lower(),))
        result = cursor.fetchone()
        if result:
            image_path = result[0]
            image = Image.open(image_path)
            # Resize image to a larger size for better display
            image = image.resize((300, 300), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            
            label = Label(top, image=photo)
            label.image = photo  # Keep a reference to avoid garbage collection
            label.pack(padx=10, pady=10)

# Function to recommend recipes
def recommend_recipes(available_ingredients):
    available_ingredients = [ingredient.lower() for ingredient in available_ingredients]
    query = '''
    SELECT r.name, r.instructions, r.nutrition
    FROM recipes r
    JOIN recipe_ingredients ri ON r.id = ri.recipe_id
    JOIN ingredients i ON ri.ingredient_id = i.id
    WHERE LOWER(i.name) IN ({})
    GROUP BY r.id
    HAVING COUNT(DISTINCT i.id) = ?
    '''.format(','.join('?' * len(available_ingredients)))
    
    cursor.execute(query, available_ingredients + [len(available_ingredients)])
    results = cursor.fetchall()
    
    if results:
        for row in results:
            messagebox.showinfo("Recipe Recommendation", f"Recipe: {row[0]}\nInstructions: {row[1]}\nNutrition: {row[2]}")
        show_ingredient_images(available_ingredients)
    else:
        messagebox.showinfo("Recipe Recommendation", "No matching recipes found.")

# Function to search for recipes by name
def search_recipe_by_name(name):
    cursor.execute('''
    SELECT r.name, r.instructions, r.nutrition
    FROM recipes r
    WHERE LOWER(r.name) = ?
    ''', (name.lower(),))
    result = cursor.fetchone()
    
    if result:
        messagebox.showinfo("Recipe Search", f"Recipe: {result[0]}\nInstructions: {result[1]}\nNutrition: {result[2]}")
    else:
        messagebox.showinfo("Recipe Search", "Recipe not found.")

# Function to save favorite recipes
def save_favorite_recipe(name):
    cursor.execute('''
    SELECT id
    FROM recipes
    WHERE LOWER(name) = ?
    ''', (name.lower(),))
    result = cursor.fetchone()
    
    if result:
        cursor.execute('''
        INSERT INTO favorites (recipe_id) VALUES (?)
        ''', (result[0],))
        conn.commit()
        messagebox.showinfo("Save Favorite", "Recipe saved to favorites.")
    else:
        messagebox.showinfo("Save Favorite", "Recipe not found.")

# Function to view favorite recipes
def view_favorite_recipes():
    cursor.execute('''
    SELECT r.name, r.instructions, r.nutrition
    FROM favorites f
    JOIN recipes r ON f.recipe_id = r.id
    ''')
    results = cursor.fetchall()
    
    if results:
        for row in results:
            messagebox.showinfo("Favorite Recipes", f"Recipe: {row[0]}\nInstructions: {row[1]}\nNutrition: {row[2]}")
    else:
        messagebox.showinfo("Favorite Recipes", "No favorite recipes found.")

# Tkinter UI
def get_recommendations():
    ingredients = entry.get().split(",")
    recommend_recipes([ingredient.strip() for ingredient in ingredients])

def search_by_name():
    name = simpledialog.askstring("Search Recipe", "Enter recipe name:")
    if name:
        search_recipe_by_name(name)

def save_favorite():
    name = simpledialog.askstring("Save Favorite", "Enter recipe name to save:")
    if name:
        save_favorite_recipe(name)

def view_favorites():
    view_favorite_recipes()

root = tk.Tk()
root.title("Tamil Nadu Snack Recipe App")

entry = tk.Entry(root, width=50)
entry.pack(pady=10)
button1 = tk.Button(root, text="Recommend Recipes", command=get_recommendations)
button1.pack(pady=5)
button2 = tk.Button(root, text="Search Recipe by Name", command=search_by_name)
button2.pack(pady=5)
button3 = tk.Button(root, text="Save Favorite Recipe", command=save_favorite)
button3.pack(pady=5)
button4 = tk.Button(root, text="View Favorite Recipes", command=view_favorites)
button4.pack(pady=5)

root.mainloop()

# Close the database connection
conn.close()