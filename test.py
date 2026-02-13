from logic.recipe_search import search_recipe_by_title

recipes = search_recipe_by_title("chicken curry")

if not recipes:
    print("No recipes found")
else:
    print("\nRecipes Found:\n")

    for recipe in recipes[:3]:
        print("Title:", recipe["Recipe_title"])
        print("Calories:", recipe["Calories"])
        print("Servings:", recipe["servings"])
        print("Region:", recipe["Region"])
        print("--------------------")
