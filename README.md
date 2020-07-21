# Topical: the Backend

Topical is an API

## Endpoints

`api/` – API root

### User

`api/me/` – gets the profile of the current user

### Ingredient

`api/ingredient/` – gets a list of ingredients

`api/ingredient/<str:name>/` – gets a specific ingredient.

## Models

### User

```json
{
  'username': string,
  'first_name': string,
  'last_name': string,
  'excluded_ingredients': [Ingredient]
}
```

### Ingredient

```json
{
  'name': string,
  'description': string,
  'names': [IngredientName]
}
```

### Product

```json
{
  'name': string,
  'brand': string,
  'ingredients': [Ingredient]
}
```

