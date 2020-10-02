from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views


router = DefaultRouter()
router.register('tags', viewset=views.TagViewset)
router.register('ingredient', views.IngredientViewset)
router.register('recipe', views.RecipeViewset)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls))
]