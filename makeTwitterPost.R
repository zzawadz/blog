library(rtweet)
library(dplyr)
library(lubridate)

makeRNews <- function(startDate, endDate) {

  startDate <- ymd_hms(startDate)
  endDate <- ymd_hms(endDate)

  date <- substring(endDate, 1, 10)

  applyr <- search_tweets("#applyrds", n=1500)
  applyr <- applyr %>% filter(screen_name == "zzawadz")
  applyr <- applyr %>% arrange(desc(favorite_count))
  applyr <- applyr %>% filter(created_at <= endDate, startDate < created_at)

  library(longurl)

  applyr$longurls <- lapply(applyr$urls_url, function(x) {
    strsplit(longurl::expand_urls(x)$expanded_url, split = "\\?utm_content=buffer") %>% sapply("[[", 1)
  })


  imagesNames <- sapply(applyr$media_url, function(img) {
    imgname <- file.path("static/img/2018-01-16", basename(img))
    download.file(img, destfile = imgname)
    gsub(imgname, pattern = "^static", replacement = "")
  })

  expandedText <- mapply(function(txt, urls) {
    while(length(urls) > 0) {
      txt <- stringi::stri_replace_first_regex(txt, pattern = "https://t.co/\\w+", replacement = urls[1])
      urls <- urls[-1]
    }
    txt
  }, applyr$text, applyr$longurls)

  code <- sprintf("
----------

%s

<p style='text-align:center'><img src='%s' width='80%%'></p>
", expandedText, imagesNames)
  code <- paste(code, collapse = "\n")

  date <- "2018-01-31"

  totalCode <- paste0(
  sprintf("---
title: RNews - %s
author: ~
date: '%s'
slug: news-%sRmd
categories:
  - R
tags:
  - rtips
  - applyr
---


### Some interesting Data Science stuff found between %s and %s.

", date, substring(endDate, 1, 10), substring(endDate,1,10), date, date, date),
  code, collapse = "\n\n")

  cat(totalCode, file = sprintf("content/post/%s-rnews-%s.Rmd", date, date))
}

endDate <- "2018-01-31 00:00:00"
startDate <- "2018-01-16 00:00:00"
makeRNews(startDate, endDate)
