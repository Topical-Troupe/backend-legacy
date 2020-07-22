# Topical: the Backend

Topical is an API

## Endpoints

`api/` – API root

`api/search` – The search endpoint, uses a query (`?name=` or `?upc=` to go straight to a product by UPC).

`api/ingredient/fuzzy/<str>` – Gets an ingredient by any of its names; redirects to the ingredient's proper endpoint.

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

## Other JSON Responses

### Search

```json
{
  'count': int,
  'results': [
    {
      'upc': str,
      'name': str,
      'violations': [
        {
          'slug': str,
          'description': str,
          'names': [str]
        }, ...
      ]
    }, ...
  ]
}
```

