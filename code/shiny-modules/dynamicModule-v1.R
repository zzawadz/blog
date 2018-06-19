library(shiny)
##### Plot module

modulePlotUI <- function(id) {
  ns <- NS(id)
  fluidRow(
    column(6, sliderInput(ns("n"), label = "N:", min = 10, max = 100, value = 50)),
    column(6, plotOutput(ns("plot"), height = "200px"))
  )
}

modulePlot <- function(input, output, session, state) {

  output$plot <- renderPlot({

    # send all values from the module as a element of the `state` object
    state[[session$ns("id")]] <- list(N = input$n, type = "plot")
    plot(rnorm(input$n), rnorm(input$n))
  })

}

##### Text module
moduleTextUI <- function(id) {
  ns <- NS(id)
  fluidRow(
    column(6, sliderInput(ns("n"), label = "N:", min = 10, max = 20, value = 10)),
    column(6, verbatimTextOutput(ns("text")))
  )
}


moduleText <- function(input, output, session, state) {

  output$text <- renderPrint({
    state[[session$ns("id")]] <- list(N = input$n, type = "text") # save state to the state object
    sample(LETTERS, input$n, replace = TRUE)
  })

}

ui <- fluidPage(
  titlePanel("Dynamic modules"),
  sidebarLayout(
    sidebarPanel(
      selectInput(
        inputId = "type",
        label = "Select module",
        choices = c("plot", "text")),
      actionButton("Add", label = "Add module"),
      verbatimTextOutput("ModuleText"),
      verbatimTextOutput("AllModulesText")
    ),
    mainPanel(
      div(id = "addPlaceholder")
    )
  )
)

server <- function(input, output) {
  state <- reactiveValues()
  output$AllModulesText <- renderPrint(reactiveValuesToList(state))

  idCounter <- reactiveVal(value = 0)
  observeEvent(input$Add, {
    id <- idCounter()

    selected <- if(input$type == "plot") {
      list(ui = modulePlotUI, server = modulePlot)
    } else if(input$type == "text") {
      list(ui = moduleTextUI, server = moduleText)
    }

    insertUI(
      selector = "#addPlaceholder",
      where = "beforeBegin",
      ui = selected$ui(paste0("id",id)))

    callModule(
      module = selected$server,
      id = paste0("id",id),
      state = state)
    idCounter(id + 1)
  })

}

shinyApp(ui = ui, server = server)
