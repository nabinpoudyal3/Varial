"""
Example on making your own tool.

MyHistoNormalizer must be used in a toolchain, e.g.

**Please click on [source] on right!**

>>> from varial import tools
>>> my_normalizer = MyHistoNormalizer(
...     lambda w: w.name == 'MyEtaSpektrumHistogram'
... )
>>> tc = tools.ToolChain(
...     'MyToolChain',
...     [my_normalizer]
... )
>>> tc.run()
"""

import itertools
from varial import generators as gen
from varial import tools


class MyHistoNormalizer(tools.Tool):
    """
    This tool normalizes histograms

    :param filter_keyfunc:  function, keyfunction with one argument,
                            e.g. ``lambda w: w.name == 'HistoName'``
    :param path:            str, path to look for rootfiles,
                            default: ``'.'``
    """
    def __init__(self, filter_keyfunc, path='.'):
        super(MyHistoNormalizer, self).__init__()
        self.filter_keyfunc = filter_keyfunc
        self.path = path

    def run(self):
        """
        Load, normalize, store. All done with generators.
        """
        # use a chain of generator, starting with aliases
        my_hists = gen.dir_content(dir_path=self.path)
        # my_hists is a _generator_ of aliases!
        # you could make a list with my_hists = list(my_hists)

        # filter them
        my_hists = itertools.ifilter(self.filter_keyfunc, my_hists)
        # my_hists is again a generator of aliases

        # for the remaining ones: load the histograms from file
        my_hists = gen.load(my_hists)
        # my_hists is again a generator, this time of histograms

        # perform the normalization
        my_hists = gen.gen_norm_to_integral(my_hists)
        # my_hists is again a generator, but the output is normalized

        # pull everything through the pipe (and thus perform the operations)
        my_hists = list(my_hists)

        # store data by pointing self.result to it
        self.result = my_hists
        # when finishing this module the histograms are written to disk

        # make a nice statement
        self.message('INFO: %d histograms normalized' % len(self.result))
