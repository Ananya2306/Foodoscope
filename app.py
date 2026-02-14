import streamlit as st
from utils.helpers import split_ingredients
from logic.recipe_search import analyze_recipe

st.title("🍳 AlgoMinds ACDSS")
st.subheader("Smart Recipe Decision Support System")

recipe_name = st.text_input("Enter Recipe Name")
ingredient_input = st.text_input(
    "Enter your ingredients (comma separated)"
)

if st.button("Analyze"):

    user_ingredients = split_ingredients(ingredient_input)
    result = analyze_recipe(recipe_name, user_ingredients)

    if not result:
        st.error("Recipe not found.")
    else:
        st.success(f"Recipe: {result['recipe_title']}")
        st.metric("Match %", result["match_percent"])
        st.metric("Confidence Score", result["confidence"])
        st.write("### Missing Ingredients")
        st.write(result["missing"])
        st.write("### Suggested Substitutes")
        st.write(result["substitutions"])
        st.info(result["explanation"])