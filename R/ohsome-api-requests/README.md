How to use the ohsome API with R
================
Lukas Loos
5 März 2019

Introduction
------------

There are different packages available to use for http requests with R. This tutorial will cover the packages **httr** and **rapiclient**.

Prerequisites
-------------

-   install packages: httr, jsonlite, rapiclient and readtext

------------------------------------------------------------------------

### rapiclient

-   <https://cran.r-project.org/web/packages/rapiclient/index.html>
-   <https://github.com/bergant/rapiclient>
-   generates functions for the API endpoints
-   no support for POST requests

``` r
library(rapiclient)

api <- get_api(url= "https://api.ohsome.org/v0.9-ignite/docs?group=dataAggregation")

operations <- get_operations(api)

schemas <- get_schemas(api)

result <- operations$elementsCount(bboxes = '85.31015,27.71919,85.31828,27.72459', keys = 'building', values = 'yes', time = '2014-01-01/2017-01-01/P1Y', types = 'way')

content <- httr::content(result)

content$result[[1]]
```

    ## $timestamp
    ## [1] "2014-01-01T00:00:00Z"
    ## 
    ## $value
    ## [1] 761

------------------------------------------------------------------------

### httr

-   <https://cran.r-project.org/web/packages/httr/index.html>
-   <https://cran.r-project.org/web/packages/httr/vignettes/quickstart.html>
-   use httr if you want to send POST requests.

``` r
library(httr)
library(readtext)
```

``` r
elementsCountGroupByBoundary <- function(x) {
  
  osmKeys <- "building"
  osmTime <- "2015-03-01/2015-12-01/P1M"
  osmTypes <- "way"
  osmValues <- "yes"

    r <- POST("https://api.ohsome.org/v0.9-ignite/elements/count/groupBy/boundary", 
            encode = "form", 
            body = list(
              bpolys = x, 
              keys = osmKeys, 
              time = osmTime, 
              types = osmTypes,
              values = osmValues)
  )  
  return(r)
}
```

#### POST requst using "|" delimited format

``` r
bpolysLine <- readLines("data/example-data.lineformat")
response <- elementsCountGroupByBoundary(bpolysLine)
response$status_code
```

    ## [1] 400

``` r
response
```

    ## Response [https://api.ohsome.org/v0.9/elements/count/groupBy/boundary]
    ##   Date: 2019-03-07 18:21
    ##   Status: 400
    ##   Content-Type: application/json;charset=UTF-8
    ##   Size: 238 B
    ## {
    ##   "timestamp" : "2019-03-07T18:21:52.687",
    ##   "status" : 400,
    ##   "message" : "You need to define one of the boundary parameters (bboxes...
    ##   "requestUrl" : "https://api.ohsome.org/v0.9/elements/count/groupBy/bou...

``` r
contentLine <- httr::content(response)
contentLine$groupByResult[[1]]$result[[1]]
```

    ## NULL

#### POST requst using geoJSON format

``` r
geoJSON <- readtext("data/example-data.geojson")
response <- elementsCountGroupByBoundary(geoJSON$text)
response
```

    ## Response [https://api.ohsome.org/v0.9/elements/count/groupBy/boundary]
    ##   Date: 2019-03-07 18:21
    ##   Status: 400
    ##   Content-Type: application/json;charset=UTF-8
    ##   Size: 238 B
    ## {
    ##   "timestamp" : "2019-03-07T18:21:53.011",
    ##   "status" : 400,
    ##   "message" : "You need to define one of the boundary parameters (bboxes...
    ##   "requestUrl" : "https://api.ohsome.org/v0.9/elements/count/groupBy/bou...

``` r
content <- httr::content(response)
content$groupByResult[[1]]$result[[1]]
```

    ## NULL

### request with CSV response

``` r
elementsCountGroupByBoundaryCSV <- function(x) {
  
  osmKeys <- "building"
  osmTime <- "2015-03-01/2015-12-01/P1M"
  osmTypes <- "way"
  osmValues <- "yes"

    r <- POST("https://api.ohsome.org/v0.9-ignite/elements/count/groupBy/boundary", 
            encode = "form", 
            body = list(
              format = "csv",
              bpolys = x, 
              keys = osmKeys, 
              time = osmTime, 
              types = osmTypes,
              values = osmValues)
  )  
  return(r)
}

geoJSON <- readtext("data/example-data.geojson")
response <- elementsCountGroupByBoundaryCSV(geoJSON$text)
response 
```

    ## Response [https://api.ohsome.org/v0.9/elements/count/groupBy/boundary]
    ##   Date: 2019-03-07 18:21
    ##   Status: 400
    ##   Content-Type: application/json;charset=UTF-8
    ##   Size: 238 B
    ## {
    ##   "timestamp" : "2019-03-07T18:21:53.363",
    ##   "status" : 400,
    ##   "message" : "You need to define one of the boundary parameters (bboxes...
    ##   "requestUrl" : "https://api.ohsome.org/v0.9/elements/count/groupBy/bou...
