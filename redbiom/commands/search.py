import click

from . import cli


@cli.group()
def search():
    """Observation and sample search support."""
    pass


@search.command(name="observations")
@click.option('--from', 'from_', type=click.File('r'), required=False,
              help='A file or stdin which provides observations to search for',
              default=None)
@click.option('--exact', is_flag=True, default=False,
              help="All found samples must contain all specified observations")
@click.option('--context', required=True, type=str,
              help="The context to search within.")
@click.argument('observations', nargs=-1)
def search_observations(from_, exact, context, observations):
    """Find samples containing observations."""
    import redbiom._requests
    import redbiom.util

    redbiom._requests.valid(context)

    it = redbiom.util.from_or_nargs(from_, observations)

    # determine the samples which contain the observations of interest
    samples = redbiom.util.samples_from_observations(it, exact, context)

    for sample in samples:
        click.echo(sample)


@search.command(name='metadata')
@click.option('--categories', is_flag=True, required=False, default=False,
              help="Search for metadata categories instead of metadata values")
@click.argument('query', nargs=1)
def search_metadata(query, categories):
    """Find samples or categories.

    The metadata search engine uses natural language processing to search for
    word stems within a samples metadata. A word stem disregards modifiers and
    plurals, so for instance, a search for "antibiotics" will actually perform
    a search for "antibiot". Similarly, a search for "crying" will actually
    search for "cry". The words specified can be combined with set-based
    operations, so for instance, a search for "antibiotics & crying" will
    obtain the set of samples in which each sample has "antibiot" in its
    metadata as well as "cry". N.B., the specific category in which a stem is
    found is not assured to be the same, "antibiot" could be in one category
    and "cry" in another. A set intersection can be performed with "&", a
    union with "|" and a difference with "-".

    The stem based search can also be applied to metadata categories when
    "--categories" is specified.

    In addition to the stem-based search, value based searches can also be a
    applied. These use a Python-like grammar and allow for a rich set of
    comparisons to be performed based on a metadata category of interest. For
    example, "where qiita_study_id == 10317" will find all samples which have
    the qiita_study_id metadata category, and in which the value for that
    sample is "10317."

    These two types of queries can be combined. A few examples are below.
    These queries make assumptions about the metadata available, and are
    only intended to be illustrative.

    Find all samples in which the word antibiotics exists in its metadata.

    $ redbiom search metadata antibiotics

    Find all samples in which the word infant exists, as well as antibiotics,
    where the infants are under a certain number of days old:

    $ redbiom search metadata "infant & antibiotics where age_days < 30"

    We can also use this engine to find metadata categories. In the next
    example, we're searching for all metadata categories which contain the
    "ph", and we'll go ahead and remove any category which contains the stem
    "water".

    $ redbiom search metadata --categories "ph - water"
    """
    import redbiom.search
    for i in redbiom.search.metadata_full(query, categories):
        click.echo(i)


@search.command(name='taxon')
@click.option('--context', required=True, type=str,
              help="The context to search within.")
@click.argument('query', nargs=1)
def search_taxon(context, query):
    """Find features associated with a taxon"""
    import redbiom.fetch
    for i in redbiom.fetch.taxon_descendents(context, query):
        click.echo(i)
