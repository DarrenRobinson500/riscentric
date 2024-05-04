def add_lines(text, gap=40):
    l = len(text)
    r = range(gap, l, gap)
    for x in r:
        position, found = x, False
        while not found and position < l:
            if text[position] == " ":
                text = text[:position] + "\n" + text[position + 1:]
                found = True
            position += 1
    return text


text = "I am concerned about an approach being taken within a business line, a project, or a process and its impact on my organisation, or our customers."

new_text = add_lines(text, 40)
print(text)
print(new_text)