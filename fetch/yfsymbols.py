from usp.tree import sitemap_tree_for_homepage
from urllib.parse import unquote


import click

@click.command()
@click.option('-o', '--out-file', type=str, help='file where all symbols are written to')
def fetch_symbols(out_file):
    symbols = set()

    sitemap_tree = sitemap_tree_for_homepage('https://finance.yahoo.com')

    for i, p in enumerate(sitemap_tree.all_pages()):
        if p.url.startswith('https://finance.yahoo.com/quote'):
            symbols.add(unquote(p.url.split('/')[4]))

    symbols = sorted(symbols)

    with open(out_file, 'w') as f:
        for s in symbols:
            f.write(s + '\n')

    print("saved", len(symbols), "symbols")


if __name__ == '__main__':
    fetch_symbols()