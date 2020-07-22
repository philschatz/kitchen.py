from typing import Callable, List, Union
from copy import deepcopy
from lxml import etree
from lxml.etree import XPath
from cssselect import GenericTranslator
from cssselect2.compiler import CompiledSelector
from cssselect2.parser import parse
import cssselect2


class Counter:
    def __init__(self):
        self.value = 0

    def increment(self) -> None:
        self.value += 1

    def get(self) -> int:
        self.value

    def reset(self) -> None:
        self.value = 0


class ElementWrapper:
    def __init__(self, clipboards, counters, el: etree.ElementBase):
        self._clipboards = clipboards
        self._counters = counters
        self.el = el

    def search(self, selector: str) -> List["ElementWrapper"]:
        ns = {
            'h': 'http://www.w3.org/1999/xhtml'
        }

        sel = XPath(GenericTranslator().css_to_xpath(selector), namespaces=ns)
        children = sel.evaluate(self.el)
        return [ElementWrapper(self._clipboards, self._clipboards, e) for e in children]

        # expr = GenericTranslator().css_to_xpath(selector)
        # print(expr)
        # children = self.el.xpath(expr, namespaces=ns)
        # return [ElementWrapper(self.clipboards, e) for e in children]

        #
        # sels = [CompiledSelector(s) for s in parse(selector)]
        # matcher = cssselect2.Matcher()
        # for sel in sels:
        #     matcher.add_selector(sel)
        # matches = matcher.match(self.el)
        # if matches:
        #     for match in matches

    def first(self, selector: str) -> Union['ElementWrapper', None]:
        ret = self.search(selector)
        if len(ret) == 0:
            return None
        else:
            return ret[0]

    def contains(self, selector: str) -> bool:
        return self.first(selector) is not None

    def set_name(self, element_name: str) -> None:
        self.el.tag = element_name

    def add_class(self, class_name: str) -> None:
        cls = self.el.get('class')
        if cls is None:
            cls = ''
        classes = set(cls.strip().split(' '))
        classes.add(class_name)
        self.el.set('class', ' '.join(classes))

    def remove_class(self, class_name: str) -> None:
        cls = self.el.get('class')
        if cls is None:
            cls = ''
        classes = set(cls.strip().split(' '))
        classes.remove(class_name)
        if len(classes) == 0:
            del self.el.attrib['class']
        else:
            self.el.set('class', ' '.join(classes))

    def get_counter(self, name: str) -> Counter:
        if hasattr(self._counters, name):
            return self._counters[name]
        else:
            c = Counter()
            self._counters[name] = c
            return c

    def _get_board(self, clipboard_name: str) -> List['ElementWrapper']:
        if hasattr(self._clipboards, clipboard_name):
            return self._clipboards[clipboard_name]
        else:
            c = list()
            self._clipboards[clipboard_name] = c
            return c

    def cut(self, clipboard_name: str) -> None:
        self._get_board(clipboard_name).append(self)

    def copy(self, clipboard_name: str) -> None:
        c = deepcopy(self.el)
        self._get_board(clipboard_name).append(ElementWrapper(self._clipboards, self._counters, c))

    def paste(self, clipboard_name: str) -> List['ElementWrapper']:
        return self._get_board(clipboard_name)

    def trash(self) -> None:
        self.el.getparent().remove(self.el)

    def prepend(self, el: 'ElementWrapper') -> None:
        self.el.insert(0, el.el)

    def append(self, el: 'ElementWrapper') -> None:
        self.el.append(el.el)

    def replace_children(self, els: List['ElementWrapper']) -> None:
        # Remove all the existing children
        for c in self.el.getchildren():
            self.el.remove(c)

        # Add all the new children
        for c in els:
            self.el.append(c.el)

    def raw(self) -> etree.ElementBase:
        return self.el


def bake(source: str, recipe: Callable[[ElementWrapper], None]):
    document = etree.XML(source)
    clipboards = dict()
    counters = dict()
    root = ElementWrapper(clipboards, counters, document)
    recipe(root)
    print(etree.tostring(document))
