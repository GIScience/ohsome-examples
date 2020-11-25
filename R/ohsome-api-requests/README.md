How to use the ohsome API with R
================

## Introduction

There are different packages available to use for http requests with R.
This tutorial will cover the packages **httr** and **rapiclient**.

## Prerequisites

  - install packages: httr, jsonlite, rapiclient and readtext

-----

### rapiclient

  - <https://cran.r-project.org/web/packages/rapiclient/index.html>
  - <https://github.com/bergant/rapiclient>
  - generates functions for the API endpoints
  - no support for POST requests

<!-- end list -->

``` r
library(rapiclient)

api <- get_api(url= "https://api.ohsome.org/v1/docs?group=Data%20Aggregation")

operations <- get_operations(api)

schemas <- get_schemas(api)

result <- operations$count(bboxes = '85.31015,27.71919,85.31828,27.72459', filter = 'building=yes and type:polygon', time = '2014-01-01/2017-01-01/P1Y')
```

    ## Warning in if (substr(type, 1, 1) == ".") {: the condition has length > 1 and
    ## only the first element will be used

``` r
content <- httr::content(result)

content$result[[1]]
```

    ## NULL

-----

### httr

  - <https://cran.r-project.org/web/packages/httr/index.html>
  - <https://cran.r-project.org/web/packages/httr/vignettes/quickstart.html>
  - use httr if you want to send POST requests.

<!-- end list -->

``` r
library(httr)
library(readtext)
```

``` r
elementsCountGroupByBoundary <- function(x) {

  osmTime <- "2015-03-01/2015-12-01/P1M"

    r <- POST("https://api.ohsome.org/v1/elements/count/groupBy/boundary",
            encode = "form",
            body = list(
              bpolys = x,
              filter = 'building=yes and geometry:polygon',
              time = osmTime)
  )  
  return(r)
}
```

#### POST requst using “|” delimited format

``` r
bpolysLine <- readLines("data/example-data.lineformat")
response <- elementsCountGroupByBoundary(bpolysLine)
response$status_code
```

    ## [1] 200

``` r
response
```

    ## Response [https://api.ohsome.org/v1/elements/count/groupBy/boundary]
    ##   Date: 2020-06-22 16:58
    ##   Status: 200
    ##   Content-Type: application/json;charset=UTF-8
    ##   Size: 5.86 kB
    ## {
    ##   "attribution" : {
    ##     "url" : "https://ohsome.org/copyrights",
    ##     "text" : "© OpenStreetMap contributors"
    ##   },
    ##   "apiVersion" : "1.0.0",
    ##   "groupByResult" : [ {
    ##     "result" : [ {
    ##       "timestamp" : "2015-03-01T00:00:00Z",
    ##       "value" : 305.0
    ## ...

``` r
contentLine <- httr::content(response)
contentLine$groupByResult[[1]]$result[[1]]
```

    ## $timestamp
    ## [1] "2015-03-01T00:00:00Z"
    ##
    ## $value
    ## [1] 305

#### POST requst using geoJSON format

``` r
geoJSON <- readtext("data/example-data.geojson")
response <- elementsCountGroupByBoundary(geoJSON$text)
response
```

    ## Response [https://api.ohsome.org/v1/elements/count/groupBy/boundary]
    ##   Date: 2020-06-22 16:58
    ##   Status: 200
    ##   Content-Type: application/json;charset=UTF-8
    ##   Size: 5.86 kB
    ## {
    ##   "attribution" : {
    ##     "url" : "https://ohsome.org/copyrights",
    ##     "text" : "© OpenStreetMap contributors"
    ##   },
    ##   "apiVersion" : "1.0.0",
    ##   "groupByResult" : [ {
    ##     "result" : [ {
    ##       "timestamp" : "2015-03-01T00:00:00Z",
    ##       "value" : 305.0
    ## ...

``` r
content <- httr::content(response)
content$groupByResult[[1]]$result[[1]]
```

    ## $timestamp
    ## [1] "2015-03-01T00:00:00Z"
    ##
    ## $value
    ## [1] 305

#### request with CSV response

``` r
elementsCountGroupByBoundaryCSV <- function(x) {

  osmTime <- "2015-03-01/2015-12-01/P1M"

    r <- POST("https://api.ohsome.org/v1/elements/count/groupBy/boundary",
            encode = "form",
            body = list(
              format = "csv",
              bpolys = x,
              filter = 'building=yes and geometry:polygon',
              time = osmTime)
  )  
  return(r)
}

geoJSON <- readtext("data/example-data.geojson")
response <- elementsCountGroupByBoundaryCSV(geoJSON$text)
response
```

    ## Response [https://api.ohsome.org/v1/elements/count/groupBy/boundary]
    ##   Date: 2020-06-22 16:58
    ##   Status: 200
    ##   Content-Type: text/csv;charset=UTF-8
    ##   Size: 850 B
    ## # Copyright URL: https://ohsome.org/copyrights
    ## # Copyright Text: © OpenStreetMap contributors
    ## # API Version: 1.0.0
    ## timestamp;feature1;feature2;feature3;feature4;feature5;feature6;feature7
    ## 2015-03-01T00:00:00Z;305.0;191.0;380.0;659.0;0.0;674.0;76.0
    ## 2015-04-01T00:00:00Z;305.0;191.0;380.0;659.0;0.0;674.0;76.0
    ## 2015-05-01T00:00:00Z;639.0;797.0;1067.0;934.0;520.0;1177.0;282.0
    ## 2015-06-01T00:00:00Z;1371.0;1244.0;1992.0;1509.0;675.0;1737.0;821.0
    ## 2015-07-01T00:00:00Z;1501.0;1274.0;1990.0;1570.0;675.0;1755.0;822.0
    ## 2015-08-01T00:00:00Z;1501.0;1274.0;1990.0;1570.0;675.0;1752.0;822.0
    ## ...
