# Topical: the Backend

Topical is an API

## Endpoints

`api/` – API root

### User

`api/me/` – gets the profile of the current user

## Models

## User

```json
{
  'username': string,
  'first_name': string,
  'last_name': string,
  'excluded_ingredients': [Ingredient]
}
```

