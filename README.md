# Topical: the Backend

Topical is an API

## Endpoints

`api/` – API root

`api/search` – The search endpoint, uses a query (`?name=` or `?upc=` to go straight to a product by UPC).

### Model Endpoints

#### Ingredient

`api/ingredient/fuzzy/<str>/` – Gets an ingredient by any of its names; redirects to the ingredient's proper endpoint.

#### Product

`api/product/<upc>/ingredients/` – View or change the list of ingredients on a product. Supports `GET`, `POST`, and `DELETE` methods. To `POST` or `DELETE`, send a JSON body with a list `names` containing fuzzy names of the ingredients to add or remove (e.g. `{ "names": ["sls"] }`).

### User

`api/me/` – gets the profile of the current user

`api/usersetup/` – sets up the logged in user. This should be done after creating a user, but Django gets angry at me when I try to do this myself. :(

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

