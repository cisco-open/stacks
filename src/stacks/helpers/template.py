import glob
import pathlib

import jinja2

from .. import filters


def jinja2_render(ctx, patterns, data={}):
    """Overwrite files in 'patterns' with their Jinja2 render.

    Keyword arguments:
      patterns[list]: patterns of text files
      data[dict]: data to render files with
    """
    for pattern in patterns:
        for path in sorted(glob.glob(str(pattern))):
            path = pathlib.Path(path)
            if path.is_file():
                try:
                    with open(path, "r") as fin:
                        template = jinja2.Template(fin.read(), undefined=jinja2.StrictUndefined)
                    with open(path, "w") as fout:
                        filters_dict = {}
                        for filter in filters.__all__:
                            filter_name = filter.__name__

                            def filter_with_context(*args, filter_name=filter_name, **kwargs):
                                return getattr(filters, filter_name)(ctx, *args, **kwargs)

                            filters_dict[filter_name] = filter_with_context
                        fout.write(template.render(data | filters_dict))
                except jinja2.exceptions.UndefinedError as e:
                    raise Exception(f"Failure to render {path}: {e}")
                except jinja2.exceptions.TemplateSyntaxError as e:
                    raise Exception(f"Failure to render {path} at line {e.lineno}, in statement {e.source}: {e}")
