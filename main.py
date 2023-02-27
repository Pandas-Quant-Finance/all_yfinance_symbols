from usp.tree import sitemap_tree_for_homepage


if __name__ == '__main__':
    symbols = set()

    sitemap_tree = sitemap_tree_for_homepage('https://finance.yahoo.com')

    for i, p in enumerate(sitemap_tree.all_pages()):
        if p.url.startswith('https://finance.yahoo.com/quote'):
            symbols.add(p.url.split('/')[4])

    with open('yfinance.symbols', 'w') as f:
        for s in symbols:
            f.write(s + '\n')
