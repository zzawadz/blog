---
title: Drag and Drop in Shiny
author: ~
date: '2017-11-24'
slug: drag-and-drop-in-shiny
categories:
  - R
tags:
  - shiny
---

Shiny application is a great way to deliver the result of statistical analysis, especially when it must be reproducible. I don't know why, but people prefer to use graphic interface, rather than run scripts;)

One of my clients recently requested to have an ability to move around elements in the dashboard. There are some R packages to attain such effect, and possibly it would be a bit easier to use them, but I had an unfinished project called `dragulaR`. It's a very simple wrapper around javascript library `dragula` (https://bevacqua.github.io/dragula/) which allows you to move around elements very, very easily. In the end, I decided to spend some time polishing `dragulaR`, and now it's something quite usable, and I hope useful for others.

For more information check the repo on Github - https://github.com/zzawadz/dragulaR.

### GIFs:

![](https://github.com/zzawadz/dragulaR/raw/master/media/basic.gif)

![](https://github.com/zzawadz/dragulaR/raw/master/media/model.gif)
