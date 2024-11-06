import requests
import webbrowser
from io import BytesIO
from PIL import Image, ImageTk
from pathlib import Path
from tkinter import Tk, Canvas, Entry, Text, Button, PhotoImage, Label, Toplevel, Scrollbar, Frame

# Constants for recipe image dimensions
RECIPE_IMAGE_WIDTH = 200
RECIPE_IMAGE_HEIGHT = 200
image_url = "" 

class RecipeApp:
    def __init__(self, recipe_app_key):
        self.recipe_app_key = recipe_app_key

        # Main Window
        self.main_window = Tk()
        self.main_window.geometry("747x504")
        self.main_window.configure(bg="#3E2929")
        
        self.canvas = Canvas(
            self.main_window,
            bg="#3E2929",
            height=504,
            width=747,
            bd=0,
            highlightthickness=0,
            relief="ridge"
        )
        self.canvas.place(x=0, y=0)

        # Search text label
        self.canvas.create_text(
            121.0,
            202.0,
            anchor="nw",
            text="Then What do you want?",
            fill="#CC9318",
            font=("Montserrat Bold", 36 * -1)
        )

        # Search entry background and entry field
        self.entry_image_1 = PhotoImage(file=relative_to_assets("entry_1.png"))
        self.entry_bg_1 = self.canvas.create_image(372.0, 281.0, image=self.entry_image_1)
        self.search_entry = Entry(self.main_window, bd=0, bg="#D9D9D9", fg="#000716", highlightthickness=0)
        self.search_entry.place(x=140.0, y=262.0, width=464.0, height=36.0)

        # Search button
        self.button_image_1 = PhotoImage(file=relative_to_assets("button_7.png"))
        self.search_button = Button(
            self.main_window,
            image=self.button_image_1,
            borderwidth=0,
            highlightthickness=0,
            command=self.__run_search_query,
            relief="flat"
        )
        self.search_button.place(x=578.0, y=262.0, width=42.0, height=35.5)

    def __run_search_query(self):
        query = self.search_entry.get()
        recipe = self.__get_recipe(query)

        # Open results in a new window
        if recipe:
            self.__open_results_window(recipe)
        else:
            self.__open_results_window(None, message="No Recipe found for search criteria")

    def __open_results_window(self, recipe, message=""):
        # Create a new result window
        result_window = Toplevel(self.main_window)
        result_window.geometry("1441x800")
        result_window.configure(bg="#3E2929")

        # Create a frame and canvas for scrolling
        frame = Frame(result_window)
        frame.pack(fill="both", expand=True)

        canvas = Canvas(frame, bg="#3E2929", bd=0, highlightthickness=0, relief="ridge")
        canvas.pack(side="left", fill="both", expand=True)

        scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        canvas.config(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas to hold the recipe content
        content_frame = Frame(canvas, bg="#3E2929")
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # Add recipe content to the canvas
        if recipe:
            recipe_image = recipe['image']
            recipe_url = recipe.get('sourceUrl', "")

            # Display recipe image
            self.__show_image(content_frame, recipe_image)

            # Display ingredients and recipe details
            self.__get_ingredients(content_frame, recipe)
            
            # Recipe link button
            def __open_link():
                if recipe_url:
                    webbrowser.open(recipe_url)
            recipe_button = Button(content_frame, text="Recipe Link", highlightbackground="#ea86b6", command=__open_link)
            recipe_button.grid(column=1, row=7, pady=10)
        else:
            # Display message if no recipe is found

            no_recipe_label = Label(content_frame, text=message, bg="#3E2929", fg="white")
            no_recipe_label.grid(column=1, row=4, pady=10)

    # Keep a reference to the image to prevent it from being garbage-collected
            no_recipe_image_label.image = no_recipe_image

            # Display an image if no recipe is found (you can use a placeholder image)
            placeholder_image_url = "https://www.creta-gel.com/page-404.html"  # Replace with your placeholder image URL
            self.__show_image(content_frame, placeholder_image_url)

        # Update the scroll region to enable scrolling
        content_frame.update_idletasks()  # Ensure the content is fully rendered
        canvas.config(scrollregion=canvas.bbox("all"))

    def __get_recipe(self, query):
        url = f"https://api.spoonacular.com/recipes/complexSearch?query={query}&apiKey={self.recipe_app_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data.get('results'):
                recipe_id = data['results'][0]['id']
                return self.__get_recipe_details(recipe_id)
        return None

    def __get_recipe_details(self, recipe_id):
        url = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={self.recipe_app_key}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        return None

    def __show_image(self, frame, image_url):
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        img = img.resize((RECIPE_IMAGE_WIDTH, RECIPE_IMAGE_HEIGHT))
        image = ImageTk.PhotoImage(img)

        holder = Label(frame, image=image)
        holder.photo = image  # Keep a reference to avoid garbage collection
        holder.grid(column=1, row=6, pady=10)

    def __get_ingredients(self, frame, recipe):
        ingredients_text = Text(frame, height=15, width=50, bg="#ffdada")
        ingredients_text.grid(column=1, row=4, pady=10)
        ingredients_text.delete("1.0", "end")

        # Display recipe details and ingredients
        ingredients_text.insert("end", "\n" + recipe['title'] + "\n")
        ingredients_text.insert("end", f"\nServings: {recipe['servings']}\n")
        ingredients_text.insert("end", f"\nReady in: {recipe['readyInMinutes']} minutes\n")

        if 'extendedIngredients' in recipe:
            for ingredient in recipe['extendedIngredients']:
                ingredients_text.insert("end", "\n- " + ingredient['original'])

    def run_app(self):
        self.main_window.resizable(False, False)
        self.main_window.mainloop()

# Helper function to manage asset paths
OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"C:\Users\Admin\Downloads\recipe-compleette-main\build\assets\frame0")

def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

# Main execution
if __name__ == "__main__":
    recipe_app_key = "8b4d854f3bb446afa28109f20019f126"  # Replace with your Spoonacular API Key
    recipe_app = RecipeApp(recipe_app_key)
    recipe_app.run_app()
