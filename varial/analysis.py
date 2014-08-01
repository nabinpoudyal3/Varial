"""
This module containes all analysis specific information and various helpers.
"""
import os


################################################################### samples ###
import settings
import wrappers
active_samples = []  # list of samplenames without systematic samples
all_samples = {}


def samples():
    """Returns a dict of all MC samples."""
    return dict(
        (k, v)
        for k, v in all_samples.iteritems()
        if k in active_samples
    )


def mc_samples():
    """Returns a dict of all MC samples."""
    return dict(
        (k, v)
        for k, v in all_samples.iteritems()
        if k in active_samples and not v.is_data
    )


def data_samples():
    """Returns a dict of all real data samples."""
    return dict(
        (k, v)
        for k, v in all_samples.iteritems()
        if k in active_samples and v.is_data
    )


def data_lumi_sum():
    """Returns the sum of luminosity in data samples."""
    return float(sum(
        v.lumi
        for k, v in data_samples().iteritems()
        if k in active_samples
    )) or settings.default_data_lumi


def data_lumi_sum_wrp():
    """Returns the sum of data luminosity in as a FloatWrapper."""
    return wrappers.FloatWrapper(data_lumi_sum(), history="DataLumiSum")


def get_pretty_name(key):
    """Simple dict call for names, e.g. axis labels."""
    return settings.pretty_names.get(key, key)


def get_color(sample_or_legend_name, default=0):
    """Gives a ROOT color value back for sample or legend name."""
    name = sample_or_legend_name
    if name in all_samples:
        name = all_samples[name].legend
    if name in settings.colors:
        return settings.colors[name]
    if default:
        return default
    new_color = settings.default_colors[len(settings.colors)]
    settings.colors[name] = new_color
    return new_color


def get_stack_position(sample):
    """Returns the stacking position (integer)"""
    s = settings
    if sample in all_samples:
        legend = all_samples[sample].legend
        if legend in s.stacking_order:
            # need string to be comparable
            return str(s.stacking_order.index(legend) * 0.001)
        else:
            return legend
    else:
        return ''


################################################ result / folder management ###
cwd = settings.varial_working_dir
_tool_stack = []
_results_base = None
_current_result = None


def _mktooldir():
    global cwd
    cwd = (settings.varial_working_dir
           + "/".join(t.name for t in _tool_stack)
           + "/")
    if not os.path.exists(cwd):
        os.mkdir(cwd)


class _ResultProxy(object):
    def __init__(self, tool, parent):
        self.name = tool.name
        self.parent = parent
        self.children = {}
        self.result = None
        if parent:
            parent.children[self.name] = self

    def lookup(self, keys):
        if not keys:
            return self.result
        k = keys.pop(0)
        if k == '..' and self.parent:
            return self.parent.lookup(keys)
        elif k in self.children:
            return self.children[k].lookup(keys)


def push_tool(tool):
    _tool_stack.append(tool)
    _mktooldir()
    global _current_result
    global _results_base
    _current_result = _ResultProxy(tool, _current_result)
    if not _results_base:
        _results_base = _current_result


def pop_tool():
    t = _tool_stack.pop()
    _mktooldir()
    global _current_result
    _current_result.result = getattr(t, 'result', 0) or None
    _current_result = _current_result.parent


def lookup(key, default=None):
    keys = key.split('/')
    if keys[0] == '..':
        if not _current_result:
            return default
        return _current_result.lookup(keys) or default
    else:
        return _results_base.lookup(keys) or default


############################################################### fileservice ###
fs_aliases = []
fs_wrappers = {}


def fileservice(filename="fileservice", autosave=True):
    """Return FileService Wrapper for automatic storage."""
    if autosave:
        if not filename in fs_wrappers:
            fs_wrappers[filename] = wrappers.FileServiceWrapper(name=filename)
        return fs_wrappers[filename]
    else:
        return wrappers.FileServiceWrapper(name=filename)
