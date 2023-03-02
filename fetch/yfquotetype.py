import hashlib
import itertools
import os
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import click
import pandas as pd
import yahooquery as yq


@click.command()
@click.option('-f', '--symbols-file', type=str, help='file where all symbols are stored')
@click.option('-o', '--out-folder', type=str, help='folder where all quote types will be stored in shards')
@click.option('-t', '--threads', type=int, default=8, help='number of threads used to fetch quote types')
@click.option(      '--fetch-shards', type=str, default=None, help='comma separated list of shard ranges 1-20,30-40,... to be fetched')
def fetch_quote_type(symbols_file, out_folder, threads, fetch_shards):
    print("using", symbols_file, "with", threads, "threads and out folder", out_folder)
    allowed_shards = shard_range_parser(fetch_shards)
    sharded_symbols = defaultdict(list)
    shards = 255

    with open(symbols_file, 'r') as f:
        for s in f.readlines():
            s = s.rstrip().replace('"', "%22")
            h = int(hashlib.md5(s.encode()).hexdigest(), 16) % shards

            sharded_symbols[h].append(s)

    # sort dictionary and values for convenience
    sharded_symbols = {k: sorted(v) for k, v in sharded_symbols.items()}
    sharded_symbols = dict(sorted(sharded_symbols.items()))

    for shard, symbols in sharded_symbols.items():
        if allowed_shards is not None and shard not in allowed_shards: continue
        started_time = datetime.now()

        print("fetch", len(symbols), "quote types in shard", shard, "from", shards, symbols[:5], "...")

        with ThreadPoolExecutor(threads) as executor:
            qtypes = [qt for qt in executor.map(get_quote_type, symbols)]

        out_file = Path(out_folder, f"{shard}.csv")
        out_file.parent.mkdir(parents=True, exist_ok=True)

        with open(out_file.absolute(), "w") as f:
            err = 0
            header = True
            for qtype in qtypes:
                try:
                    df = pd.DataFrame(qtype).T
                    df.index.name = 'symbol'
                    df.to_csv(f, header=header, index=True)

                    header = False
                    f.flush()
                except Exception as e:
                    print(e, qtype)
                    err += 1

        print("shard", shard, "from", shards, "done in", (datetime.now() - started_time).seconds, "seconds",
              err, "errors from", len(symbols), "symbols")

    print("saved quote types")


def shard_range_parser(fetch_shards):
    if fetch_shards is not None:
        return list(
            itertools.chain.from_iterable(
                [list(range(*[int(ss) for ss in r.split("-")])) for r in fetch_shards.split(",")]
            )
        )
    else:
        return None


def get_quote_type(symbol):
    return yq.Ticker(symbol).quote_type


if __name__ == '__main__':
    print(os.getcwd())
    fetch_quote_type()
