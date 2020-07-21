# Topical: the Backend

Topical is an API

## Endpoints

`api/` – API root

`api/search` – The search endpoint, uses a query (`?q=`).

### User

`api/me/` – gets the profile of the current user

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
