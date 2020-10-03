from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from recipe import serializers

from core.models import Tag, Ingredient, Recipe


class BaseRecipeAttrViewset(
    # viewsets.GenericViewSet,
    # mixins.ListModelMixin,
    # mixins.CreateModelMixin,
    viewsets.ModelViewSet
):
    """Base viewset for user owned recipe attribute"""
    authentication_classes = (BasicAuthentication, TokenAuthentication, )
    permission_classes = (IsAuthenticated,)

    """
    Uncomment the following lines if you wish to want the user to be able to see tags and ingredients
    that hee created and hide other user's content
    """
    def get_queryset(self):
        """Return object for current authenticated user only"""
        # return self.queryset.filter(user=self.request.user).order_by('-name')
        return self.queryset.filter(user=self.request.user).order_by('id')

    def perform_create(self, serializer):
        """Create a new recipe object"""
        serializer.save(user=self.request.user)


class TagViewset(BaseRecipeAttrViewset):
    """Manage tags in the database"""
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer


class IngredientViewset(BaseRecipeAttrViewset):
    """Manage Ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer


class RecipeViewset(viewsets.ModelViewSet):
    """Manage Recipes in DB"""
    serializer_class = serializers.RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = (BasicAuthentication, TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def _params_to_ints(self, qs):
        """Convert a list of string IDs to a list of integers"""
        return [str(str_name) for str_name in qs.split(',')]

    """
    Comment following lines of code to be able to see all available recipes in the app.
    """
    def get_queryset(self):
        """Retrieve the recipes for the authenticated user"""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            tag_names = self._params_to_ints(tags)
            queryset = queryset.filter(tags__name__in=tag_names)
        if ingredients:
            ingredient_names = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__name__in=ingredient_names)

        # return self.queryset.filter(user=self.request.user)
        return queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return a appropriate serializer class"""
        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)