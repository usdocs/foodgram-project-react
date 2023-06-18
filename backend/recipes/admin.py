from django.contrib import admin

from recipes.models import Ingredient, Recipe, Tag, RecipeIngredient, RecipeTag


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 0


class RecipeTagInline(admin.TabularInline):
    model = RecipeTag
    min_num = 1
    extra = 0


class RecipeAdmin(admin.ModelAdmin):
    inlines = (RecipeIngredientInline, RecipeTagInline)


admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
admin.site.register(RecipeIngredient)
admin.site.register(RecipeTag)
