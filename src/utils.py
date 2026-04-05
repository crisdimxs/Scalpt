import csv
import os

from rich.console import Console

VERSION = '0.2.5-alpha'

def banner():
    Console().print(f"""
         _____________________      #######   ########   #######   #          ######   ########
        |                     |    #         #          #       #  #         #      #     #
        |[bold red]  Buy Bitcoin, HODL[/bold red]  |     ######   #          # ##### #  #         # #####      #
        |[bold red]    and FUCK BANKS [/bold red]  |           #  #          #       #  #         #            #
        |___________________  \\    #######    ########  #       #   #######  #            #
                            \\_\\
                                \   ^__^            [bold cyan]By:[/bold cyan] [bold green]crisdimxs[/bold green]
                                 \  (OO)\_______    [bold cyan]Github:[/bold cyan] [bold blue]https://github.com/crisdimxs/Scalpt[/bold blue]
                                    (__)\       )\/ [bold cyan]X:[/bold cyan] [bold blue]https://x.com/crisdimxs[/bold blue]
                                        ||----w |
                                        ||     ||   [bold cyan]Powered by:[/bold cyan] [bold yellow]FinRL[/bold yellow]
M__MMM___M_MM_MM_MM__M_MMM_MMM___MMM___MMM__MM_MM__ [bold cyan]Version:[/bold cyan] [bold green]{VERSION}[/bold green]                                         >
""")

def log_trade(date, price, action, force):
    file = "data/data.csv"
    exist = os.path.isfile(file)
    columns = ["date", "price", "action", "force"]

    with open(file, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)

        if not exist:
            writer.writeheader()

        writer.writerow({
            'date': date,
            'price': price,
            'action': action,
            'force': force
        })
