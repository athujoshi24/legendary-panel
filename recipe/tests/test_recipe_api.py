from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPE_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='cinnamon'):
    """Create ad return a sample ingreient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_nonveg_recipe(user, **params):
    defaults = {
        'title': 'Sample recipe',
        'type': 'NONVEG',
        # 'rcpCreatedOn':
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


def sample_veg_recipe(user, **params):
    defaults = {
        'title': 'Sample recipe',
        'type': 'VEG',
        # 'rcpCreatedOn':
    }
    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTest(TestCase):
    """Test unauthenticated recipe API access"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_self(self):
        """Test that authentication is required"""
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test unauthenticated recipe API access"""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpassword'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes"""
        sample_veg_recipe(user=self.user)
        # sample_nonveg_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = get_user_model().objects.create_user(
            'testother@test.com',
            'testotherpassword'
        )
        sample_veg_recipe(user=user2)
        sample_veg_recipe(user=self.user)
        sample_nonveg_recipe(user=user2)
        sample_veg_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_details(self):
        """Test viewing a recipe detail"""
        recipe = sample_veg_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Chocolate Cheesecake',
            'type': 'VEG'
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Desert')
        payload = {
            'title': 'Blackberry Cheesecake',
            'type': 'VEG',
            # 'tags': [tag1.id, tag2.id],
            'tags': [tag1.name, tag2.name],
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        # recipe = Recipe.objects.get(id=res.data['name'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Rice')
        ingredient2 = sample_ingredient(user=self.user, name='Curd')
        payload = {
            'title': 'Curd rice',
            'type': 'VEG',
            'ingredients': [ingredient1.name, ingredient2.name],
        }
        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = Ingredient.objects.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_veg_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {
            'title': 'Curd rice',
            'type': 'VEG',
            'tags': [new_tag.name]
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe_self(self):
        """"Test updating a recipe with PUT"""
        recipe = sample_veg_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Curd rice',
            'type': 'VEG',
        }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)

    def test_filter_recipe_by_tags(self):
        """Test returning recipes with specific tags"""
        recipe1 = sample_veg_recipe(user=self.user, title='Paneer pahadi')
        recipe2 = sample_nonveg_recipe(user=self.user, title='Chicken Pahadi')
        tag1 = sample_tag(user=self.user, name='BBQ-VEG')
        tag2 = sample_tag(user=self.user, name='BBQ-NONVEG')
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag2)
        recipe3 = sample_veg_recipe(user=self.user, title='Bechav recipe')

        res = self.client.get(
            RECIPE_URL,
            {'tags': f'{tag1.name},{tag2.name}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_recipe_by_ingredient(self):
        """Test returning recipes with specific ingredients"""
        recipe1 = sample_veg_recipe(user=self.user, title='Farazbi')
        recipe2 = sample_nonveg_recipe(user=self.user, title='Gavar')
        ingredient1 = sample_ingredient(user=self.user, name='Farazbi')
        ingredient2 = sample_ingredient(user=self.user, name='Gavar')
        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)
        recipe3 = sample_veg_recipe(user=self.user, title='bechav')

        res = self.client.get(
            RECIPE_URL,
            {'ingredients': f'{ingredient1.name},{ingredient2.name}'}
        )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
