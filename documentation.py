import dash_bootstrap_components as dbc
from dash import html

from navbar import Navbar

nav = Navbar()

vid1_card = dbc.Card(
    [
        dbc.CardHeader("Charging Station Placement Tutorial"),
        dbc.CardBody(
            [
                html.Video(
                    controls = True,
                    id = 'movie_player',
                    #src = "https://www.youtube.com/watch?v=gPtn6hD7o8g",
                    src = "/assets/CSP_demo.mov",
                    autoPlay=False,
                    style={"max-width":"-webkit-fill-available","max-height":"-webkit-fill-available"}
                )
            ]
        )
    ]
)

CONTAINER_STYLE = {
    "padding": "2rem 1rem",
}
body = dbc.Container(vid1_card,style=CONTAINER_STYLE)

def Documentation():
    layout = html.Div([
    nav,
    body
    ])

    return layout