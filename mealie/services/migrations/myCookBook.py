import base64
import io
# import json
import lxml
import re
import tempfile
import zipfile
from gzip import GzipFile
from pathlib import Path

from slugify import slugify

from mealie.schema.recipe import RecipeNote

from ._migration_base import BaseMigrator
from .utils.migration_alias import MigrationAlias
from .utils.migration_helpers import import_image

# -----------------------------------------------------------------
# This class is for migrating recipes from myCookBook to Mealie
# -----------------------------------------------------------------
class myCookBookMigrator(BaseMigrator):

    # ------------------------------------
    # Initialization
    # ------------------------------------
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "myCookBook"
        re_num_list = re.compile(r"^\d+\.\s")

        self.key_aliases = [
            # key is the myCookBook tag
            # alias is the Mealie tag
            MigrationAlias(key="recipeIngredient", alias="ingredients", func=lambda x: x.split("\n")),
            # MigrationAlias(key="orgUrl", alias="source_url", func=None),
            # MigrationAlias(key="performTime", alias="cook_time", func=None),
            # MigrationAlias(key="recipeYield", alias="servings", func=None),
            # MigrationAlias(key="image", alias="image_url", func=None),
            MigrationAlias(key="dateAdded", alias="created", func=lambda x: x[: x.find(" ")]),
            # MigrationAlias(key="notes", alias="notes", func=lambda x: [z for z in [RecipeNote(title="", text=x) if x else None] if z], ),
            MigrationAlias(key="recipeCategory", alias="categories", func=self.helpers.get_or_set_category, ),
            MigrationAlias(key="recipeInstructions", alias="directions", func=lambda x: [{"text": re.sub(re_num_list, "", s)} for s in x.split("\n\n")], ),
            # Simple fields
            MigrationAlias(key="title", alias="title", func=None),
            MigrationAlias(key="preptime", alias="notes", func=None),    # TODO
            MigrationAlias(key="cooktime", alias="cook_time", func=None),
            MigrationAlias(key="quantity", alias="servings", func=None),
            MigrationAlias(key="url", alias="source_url", func=None),
            MigrationAlias(key="imageurl", alias="image_url", func=None),
            ]

    # ------------------------------------
    # Migration
    # ------------------------------------
    def _migrate(self) -> None:
        recipe_image_urls = {}
        recipes = []

        # Unzip file into temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(file) as zip_file:
                zip_file.extractall(tmpdir)
            name = "mycookbookrecipes/mycookbookrecipes.xml"
            #with open(name, "rb") as fd:
            # Read the file into an XML tree
            recipes_tree = etree.parse(name)
        
        recipes_root = recipes_tree.getroot()
        
        for recipe in recipes_tree.xpath("/cookbook/recipe"):
            # if we want to overwrite a previous recipe with the same name
            # if "name" in recipe:
            # recipe_model = self.clean_recipe_dictionary(recipe)
        
            recipes.append(recipe_model)

        results = self.import_recipes_to_database(recipes)

        for slug, recipe_id, status in results:
            if not status:
                continue

            try:
                # Images are stored as base64 encoded strings, so we need to decode them before importing.
                image = io.BytesIO(base64.b64decode(recipe_image_urls[slug]))
                with tempfile.NamedTemporaryFile(suffix=".jpeg") as temp_file:
                    temp_file.write(image.read())
                    path = Path(temp_file.name)
                    import_image(path, recipe_id)
            except Exception as e:
                self.logger.error(f"Failed to download image for {slug}: {e}")
