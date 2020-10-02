from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """Test that publicly available tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """Test the authorized user tags API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpassword'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags_self(self):
        """Test retrieving tags"""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Desert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,  serializer.data)

    def test_tags_limited_to_user_self(self):
        """Test that the tags returned are authenticated user"""
        user2 = get_user_model().objects.create_user(
            'testother@test.com',
            'testotherpassword'
        )
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test creating a new tag"""
        payload = {
            'name': 'Test tag',
        }
        self.client.post(TAGS_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()
        self.assertTrue(exists)

    def test_create_tag_invalid(self):
        """Creating a new tag with invalid payload"""
        payload = {'name' : ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # def test_retrieve_tags_assigned_to_recipes(self):
    #     """Test filtering tags by those assigned to recipes"""
    #     tag1 = Tag.objects.create(user=self.user, name='breakfast')
    #     tag2 = Tag.objects.create(user=self.user, name='lunch')
    #     recipe = Recipe.objects.create(
    #         title='Timepass',
    #         type='VEG'
    #     )
    #     recipe.tags.addd(tag1)
    #
    #     res = self.client.get(TAGS_URL, {'assigned_only':1})
    #
    #     serializer1 = TagSerializer(tag1)
    #     serializer2 = TagSerializer(tag2)
    #     self.assertIn(serializer1.data, res.data)
    #     self.assertNotIn(serializer2.data, res.data)
    #
    # def test_retrieve_tags_assigned_unique(self):
    #     """Test filtering tags by assigned return unique items"""
    #     tag = Tag.objects.create(user=self.user, name='Timepass Tag')
    #     Tag.objects.create(user=self.user, name='Timepass Tag 2')
    #     recipe1 = Recipe.objects.create(
    #         title='Timepass Recipe 1',
    #         type='VEG'
    #     )
    #     recipe1.tags.add(tag)
    #     recipe2 = Recipe.objects.create(
    #         title='Timepass Recipe 2',
    #         type='VEG'
    #     )
    #     recipe2.tags.add(tag)
    #
    #     res = self.client.get(TAGS_URL, {'assigned_only':1})
    #
    #     self.assertEqual(len(res.data), 1)