from kitchen import ElementWrapper, bake

if __name__ == '__main__':

    # README snippet 1:
    def my_recipe(document: ElementWrapper):
        for el in document.search("h|div.section"):
            el.set_name("section")
            el.remove_class("section")

    my_source = '<html xmlns="http://www.w3.org/1999/xhtml"><body><p/><div class="section"/></body></html>'
    bake(my_source, my_recipe)

    # README snippet 2
    def recipe2(doc: ElementWrapper):
        for div in doc.search("h|div.example"): # find all "div.example" elements in the document
            div.add_class("foo")                # add a class to each of those elements
            for p in div.search("h|p"):         # find all "p" elements inside the "div.example" elements
                p.set_name("div")               # change them to "div" tags

    bake(my_source, recipe2)

    # README snippet 3
    def recipe3(doc: ElementWrapper):
        for div in doc.search("h|div.example"):
            div.cut('my_special_clipboard')

        doc.first('h|p').copy('foo')

        new_html = doc.paste('my_special_clipboard')

    bake(my_source, recipe3)
