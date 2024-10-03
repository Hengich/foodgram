from django.shortcuts import render
from rest_framework import viewsets

from recipes.models import Ingredient, Recipe, Tag


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
