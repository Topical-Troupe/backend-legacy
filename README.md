# Topical: the Backend

Topical is an API

## Endpoints

`api/` – API root

`api/search` – The search endpoint, uses a query (`?name=` or `?upc=` to go straight to a product by UPC).

### Model Endpoints

#### Ingredient

`api/ingredient/fuzzy/<str>/` – Gets an ingredient by any of its names; redirects to the ingredient's proper endpoint.

`api/ingredient/<slug>/names` – View or change all the names of an ingredient. Allows `GET`, `POST`, and `DELETE` methods.

##### GET response

```json
{
    "names": [string]
}
```

##### POST/DELETE request body

```json
{
    'names': [string]
}
```

`api/ingredient/<slug>/exclude/` – Check or set whether an ingredient is excluded by the logged in user. Allows `GET`, `POST`, and `DELETE` methods.

##### GET response

```json
{ "excluded": boolean }
```

`api/ingredient/add/` - Adds an ingredient to the list of items excluded by the logged in user.  This endpoint will register a new ingredient in the database automatically if the ingredinet has not yet been created.  Allows `POST` method only.

##### POST body

```json
{
  "ingredients": [Ingredient]
}
```

`api/ingredient/<slug>/tag/<tag_name>/` – Gets stats on how common an ingredient is for a certain tag. An important note is that tag data is only refreshed every 3 days after the last update so it won't cost as much time for repeated checks.

##### GET response

```json
{
    "total": int,
    "matches": int,
    "percent": float,
    "common": boolean
}
```

`api/ingredient/<slug>/stats/` – Gets stats on the total exclusions of an ingredient.

##### GET response

```json
{
    "exclusion_count": int,
    "top_lists": [
        {
            "name": string,
            "author": string,
            "pk": int
        }, ...
    ],
    "top_tags": [string]
}
```

**NOTE**: `top_lists` and `top_tags` are limited to 5 items each.

#### Product

`api/product/<upc>/ingredients/` – View or change the list of ingredients on a product. Allows `GET`, `POST`, and `DELETE` methods.

##### GET response

```json
{
    "name": string,
    "image_url": string,
    "violations": [string],
    "ingredient_list": [Ingredient]
}
```

##### POST/DELETE request body

```json
{ "names": [string] }
```

`api/product/<upc>/tags/` – View or change the tags on a product. These tags are managed on the backend, so there is null-handling already in place.

##### GET response

```json
{ "tags": [string] }
```

##### POST/DELETE request body

```json
{ "tags": [string] }
```

#### User

`api/me/` – gets the profile of the current user

##### GET response

```json
{
    "username": string,
    "own_profiles": [
        {
            "name": string,
            "pk": int
        }, ...
    ],
    "subscribed_profiles": [
        {
        	"name": string,
        	"author": string,
        	"pk": int
        }
    ],
	"enabled_profiles": [
        {
            "name": string,
            "pk": int,
            "author": string or Undefined
        }
    ]
}
```

`api/usersetup/` – sets up the logged in user. This should be done after creating a user, but Django gets angry at me when I try to do this myself. :(

`api/user/exclusions` – gets all ingredients excluded by the user.

##### GET response

```json
{
  "count": int,
  "items": [
    {
      "name": string,
      "slug": string,
      "names": [string]
    },
    ...
  ]
}
```

#### Exclusion Profile

`api/profiles/<pk>/subscribe/` – view or change whether or not the user is subscribed to a profile. Allows `GET`, `POST`, and `DELETE` methods. `POST` is used to subscribe, and `DELETE` is used to unsubscribe. If the user tries to unsubscribe from a profile they own, this will return a `409 - Conflict` (instead of unsubscribing, they should be disabling or deleting their own profiles).

##### GET response

```json
{
    "subscribed": boolean,
    "enabled": boolean
}
```

**NOTE**: `"enabled"` is only present if `"subscribed"` is `true`.

`api/profiles/<pk>/enabled/` – view or change whether or not a profile is enabled. Allows `GET`, `POST`, and `DELETE` methods. Its `GET` response body is the same as `.../subscribed/`, since it literally calls it. `POST` and `DELETE` enable and disable a profile respectively.

`api/profiles/<pk>/excludes/` – view or change the ingredients excluded by this profile. Allows `GET` for all users, and allows `POST` and `DELETE` for the profile's author.

##### GET response

```json
{
    "count": int,
    "ingredients": [
        {
            "name": string,
            "slug": string,
            "names": [string]
        }, ...
    ]
}
```

##### POST/DELETE request body

```json
{ "names": [string] }
```

## Models

### User

```json
{
  "username": string,
  "first_name": string,
  "last_name": string,
  "excluded_ingredients": [Ingredient]
}
```

### Ingredient

```json
{
  "name": string,
  "description": string,
  "names": [IngredientName]
}
```

### Product

```json
{
    "name": string,
    "upc": string,
    "description": string
}
```

### Exclusion Profile

```json
{
    "url": string,
    "name": string,
    "description": string,
    "author": User,
    "excluded_ingredients": [Ingredient]
}
```

## Other JSON Responses

### Search

#### 'name' query

```json
{
	"count": int,
	"results": [
    {
			"upc": str,
			"image_url": string,
      "name": string,
      "violations": [
      		{Ingredient}, ...
      ]
    }, ...
	]
}
```

#### 'profile' query

```json
{
    "count": int,
    "results": [
        {
            "name": string,
            "author": string,
            "description": string,
            "pk": int,
            "exclusion_count": int
        }, ...
    ]
}
```