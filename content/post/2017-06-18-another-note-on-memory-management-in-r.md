---
title: Another note on memory management in R
author: Zygmunt Zawadzki
date: '2017-06-18'
slug: another-note-on-memory-management-in-r
categories:
  - R
tags:
  - performance
---

In the last post where I described one issue related to usage of R's
data structures inside C++ code. The problem was caused by memory
management system in R, which allows R to store two variables in the
same place in the memory just after making an assignment.

See the following snippet:

    #include <Rcpp.h>
    #include <vector>

    // [[Rcpp::plugins(cpp11)]]
    // [[Rcpp::export]]
    void change(Rcpp::NumericVector x) {
      // The C++ function does not return anything (it's void),
      // it only modifies the first element of the vector.
      x.at(0) = 1000.0;
    }

    x <- c(1,2,3)
    y <- x
    # x and y have the same values
    x

    ## [1] 1 2 3

    y

    ## [1] 1 2 3

In C++ this might cause problems because C++ does not take into account
that changing variable's value affects other variables which temporary
shares the same space in the memory.

But in this post, I'm leaving C++ for a moment, and I will focus on R.

Passing parameters to functions.
================================

The memory management system used in R can save a lot of memory in
function calls. The new variable used inside a function can share the
same space as an input variable as long as no other value is assigned
inside the function body.

    library(pryr)

    xx <- rnorm(1e7)
    fnc <- function(val) {
      # address does not work well inside functions
      # so it is better to use inspect
      inspect(val)$address
    }
    fnc(xx) == address(xx)

    ## [1] TRUE

Note that `xx` is pretty big - it occupies about 80mb.

Lists
=====

Lists is a fascinating structure because it allows storing arbitrary
elements. It can contain vector, models or even other lists.

They have another, but essential property - when the element is inserted
into the list, it is not copied, but it behaves like any other
variables. It means that items in a list can share the same place in the
memory as standard variables.

I can quite easily show this property by creating a list with 10^6
repetitions of vector `xx` (which has 80mb). Without sharing the same
space in memory, such list would be 80TB... I don't have such amount of
RAM on my laptop;)

    xx <- rnorm(1e7)
    big.list <- list()
    object_size(xx)

    ## 80 MB

    n <- 1000000
    object_size(xx) * n

    ## 80 TB

    # Memory in my lap:
    system2("cat", args = "/proc/meminfo", stdout = TRUE)[1]

    ## [1] "MemTotal:        8036864 kB"

    for(i in 1:n) {
      big.list[[i]] <- xx  
    }

    big.addres <- inspect(big.list)
    big.addres <- vapply(big.addres$children, FUN.VALUE = "", "[[", "address")

    # All element point to the same space in the memory:
    unique(big.addres)

    ## [1] "0x7fb3dcd52010"

    # ... which is the same space as the original xx variable
    address(xx)

    ## [1] "0x7fb3dcd52010"

Summary.
========

List's elements behave in pretty similar fashion as other variables, so
you can put larger variables inside them without worrying about memory.
R is not bad in saving memory;)
