from nicegui import ui

with ui.row():
    for i in range(20):
        with ui.card().tight():
            ui.image("images/placeholder.png").classes('w-60 h-60')
            with ui.card_section():
                ui.label('Test')
        ui.image("images/arrow.png").classes('w-60 h-60')

with ui.footer().style('background-color: #FFFFFF').classes('h-20'):
    ui.input(placeholder='start typing').props('rounded outlined dense').classes('w-full h-full')

ui.left_drawer(top_corner=True, bottom_corner=True).props('bordered').style('background-color: #FFFFFF')

ui.run()