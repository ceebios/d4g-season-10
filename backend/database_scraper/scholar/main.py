from multiprocessing import Process
import click
import os
from . import biorxiv, nature, pnas, plos, royal_society, elsevier, springer

DATAHOME = os.environ.get("MVP_DATAHOME", "..\..\data")
HOME = os.path.join(DATAHOME, "articles")


engines = {
    "biorxiv": biorxiv.Biorxiv,
    "nature": nature.Nature,
    # "pnas": pnas.PNAS, # Doesn't work anymore
    "plos": plos.PLOS,
    "royal_society": royal_society.RoyalSociety,
    "elsevier": elsevier.Elsevier,
    "springer": springer.Springer,
}


def search_one(journal, location, query, page_range):
    engine = journal(location)
    engine.search(query, page_range)


def search(query, loc, start, end):
    ps = []
    for _, journal in engines.items():
        ps.append(Process(target=search_one, args=(journal, loc, query, [start, end])))
        ps[-1].start()
    [p.join() for p in ps]


@click.command()
@click.option("--query", help="List of keywords.")
@click.option("--loc", default=HOME, help="Home folder for articles.")
@click.option("--start", default=0, help="Start page")
@click.option("--end", default=1, help="End page")
def search_all(query, loc, start, end):
    search(query, loc, start, end)


if __name__ == "__main__":
    search_all()
