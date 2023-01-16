with open("html_dependent_on_java.html", "r") as html_dependent:
    with open("main.js", "r", encoding="utf8") as main:
        main_text = main.read()
    with open("index.html", "w", encoding="utf8") as index:
        text = html_dependent.read()
        ind1 = text.find("<script") + 7
        ind2 = text.find("</script>")
        index.write(text[0:ind1] + ">" + main_text + text[ind2:])
