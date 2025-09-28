import os
from openai import OpenAI

client = OpenAI()
MODEL = "gpt-4.1"
MAX_RETRIES = 5


# --- Helper Function for API Calls ---
def get_response(instructions, input, model=MODEL, temperature=0.2):
    """Simple wrapper for OpenAI API calls."""
    try:
        response = client.responses.create(
            model=model,
            instructions=instructions, # system prompt
            input=input, # user prompt
            temperature=temperature # gpt-5 does not support temperature
            # TODO refactor to remove temperature for gpt-5
        )
        return response
    except Exception as e:
        print(f"""Response failed: {e}""")


class RecipeCreatorAgent:
    def __init__(self):
        self.instructions = "You are an innovative and highly skilled chef, "
        "renowned for creating delicious recipes that also meet specific dietary and nutritional targets. "
        "You are good at interpreting user requests and also at refining your creations based on precise feedback."
    
    def create_recipe(self, recipe_request_dict, feedback=None, temperature=1.0):
        # Example user constraints
        '''
        RECIPE_REQUEST = {
            "base_dish": "pasta",
            "constraints": [
                "gluten-free",
                "vegan",
                "under 500 calories per serving",
                "high protein (>15g per serving)",
                "no coconut",
                "taste must be rated 7/10 or higher"
            ]
        }
        '''

        base_dish = recipe_request_dict['base_dish']
        constraints_str = ", ".join(recipe_request_dict['constraints'])
        input = f"Please create a '{base_dish}' recipe that meets ALL of the following constraints: {constraints_str}."
        
        if feedback:
            input += f"\n\nIMPORTANT: Your previous attempt had issues. "
            "Please revise the recipe based on this specific feedback: {feedback}\n"
            "Ensure all original constraints AND this feedback are addressed."
        else:
            input += "\nThis is the first attempt."
            input += "\n\nPlease provide: a creative name for the dish, a list of ingredients (with quantities), "
            "step-by-step instructions, an estimated calorie count per serving, an estimated protein content (grams) per serving, "
            "and a short description of its taste profile."
            
        response = get_response(instructions=self.instructions, input=input, temperature=temperature)
        return response.output_text
    
class NutritionEvaluatorAgent:
    def __init__(self):
        self.instructions = "You are an extremely precise nutrition and dietary compliance evaluator. "
        "Your role is to meticulously assess a given recipe against a specific set of user-defined constraints. "
        "For each constraint, you must clearly state if it 'PASSED' or 'FAILED'. "
        "If a constraint FAILED, you must provide a concise reason and a actionable suggestion for improvement. "
        "You also need to provide an overall taste rating based on the recipe description."
        
    def evaluate_recipe(self, recipe, original_request_dict, critique_debug=False):
        constraints_str = ", ".join(original_request_dict['constraints'])
        input = f"""RECIPE:
        {recipe}
        
        First, make sure that the recipe includes all preparation steps. If preparation steps are missing, write 'Overall Status: FAILED'
        
        Next, please evaluate the RECIPE above against EACH of the following constraints from the original REQUEST: 
        Original Request Constraints: {constraints_str} 
        For each constraint, state the constraint verbatim, then write 'PASSED' or 'FAILED'. 
        If 'FAILED', provide a brief reason and a specific suggestion for fixing it. 
        Example for one constraint: 
        'gluten-free: PASSED'  
        'under 500 calories per serving: FAILED - Estimated 650 calories. Suggest reducing oil by half.'
        After evaluating all constraints, provide a line with 'Taste Rating: [N]/10' based on the recipe description (where N is a number).
        Finally, on a new line, write 'Overall Status: PASSED' if ALL constraints are met (including taste rating of 7 or higher for the constraint 
        'taste must be rated 7/10 or higher') OR 'Overall Status: FAILED' if ANY constraint is not met."""
        
        if critique_debug:
            print("--------------------------")
            print("evaluate_recipe input")
            print(input)
            print()
        
        response = get_response(instructions=self.instructions, input=input)
        return response.output_text
    
def main(recipe_request_dict, recipe_debug=False, critique_debug=False):
    chef = RecipeCreatorAgent()
    critic = NutritionEvaluatorAgent()
    feedback = None
    max_retries_exceeded = True
    
    for retry in range(MAX_RETRIES):
        print(f"Attempt {retry + 1}")
        print("Generating recipe ...")
        recipe = chef.create_recipe(recipe_request_dict, feedback)
        if recipe_debug:
            print("------------------------")
            print("Generated recipe")
            print(recipe)
            print()
        print("Reviewing recipe ...")
        critique = critic.evaluate_recipe(recipe, recipe_request_dict, critique_debug)
        if critique_debug:
            print("------------------------")
            print(recipe)
            print()
            print("Critique of recipe")
            print(critique)
            print()
        
        if 'Overall Status: PASSED' in critique:
            max_retries_exceeded = False
            break
        else:
            feedback = critique
            
    print("-----------------------")
    if max_retries_exceeded:
        print("Too many retries")
    print("FINAL RECIPE")
    print()
    print(recipe)
    
if __name__ == "__main__":
    RECIPE_REQUEST = {
            "base_dish": "pasta",
            "constraints": [
                "gluten-free",
                "vegan",
                "under 500 calories per serving",
                "high protein (>15g per serving)",
                "no coconut",
                "taste must be rated 7/10 or higher"
            ]
        }
    main(RECIPE_REQUEST, False, False)
            
            
            