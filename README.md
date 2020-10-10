# Laravel 7 to 8 routes converter
This script will convert your Laravel 7 compatible routes file to Laravel 8 style.


Yes it is Python. (Python 3)

# HowTo
> Do not update your "$namespace" variable of your RoutesServiceProvider before
> you run this script on your routes. The script will read the root namespace
> of the RSP.

1. Copy the script to your Laravel projects root directory.
2. Run the script for each routes file. Example: `python3 laravel-8-route-converter.py routes/web.php`
3. Control the new route files and copy or replace (with `-r` flag).
4. Delete the script.

```
usage: laravel-8-route-converter.py [-h] [-r] routes_file

Convert Laravel 7 to Laravel 8 route file.

positional arguments:
  routes_file    File to convert.

optional arguments:
  -h, --help     show this help message and exit
  -r, --replace  Replace the routes file.
```

# Laravel 7 supported syntax
Combinations of all these examples are possible as well.

The script will detect duplicate Controllers (by name) and sets an alias for this controller.

## Simple route syntax
```
Route::get('/foo/bars', 'FooBarsController@index');
Route::patch('/foo/bars/{bar}', 'FooBarsController@update');
```

## Route resources and apiResources
```
Route::apiResource('/blas', 'BlaController');
Route::resource('/blas', 'BlaController');
```

## Parameter on route
```
Route::apiResource('/foobars', 'FoobarController', ['parameters' => [
    'foobars' => 'bar',
]])
    ->only(['index', 'store', 'destroy',]);
```

## Multiline routes
```
Route::apiResource(
    '/foobars',
    'FoobarController'
)
    ->only(['index', 'store', 'destroy',]);

Route::apiResource(
    '/foo/bars',
    'FooBarsController',
    ['parameters' => [
        'bars' => 'foo',
    ]]);
```

## Nested Route groups
```
Route::group([
        'namespace' => 'Bla',
    ], function () {

        Route::patch('/foo/bars/{bar}', 'FooBarsController@update');

        Route::group([
            'namespace' => 'Tuut',
        ], function () {

            Route::apiResource('/blas', 'BlaController');
    });
});
```
