# import webbrowser

from samples.cascading_configuration import Page
from samples.cascading_configuration import background
from samples.cascading_configuration import border
from samples.cascading_configuration import button
from samples.cascading_configuration import style
from samples.cascading_configuration import text


def test_style_generation():
    assert style._css_style() == "border: 1.0px solid black; border-radius: 0px; background-color: white; color: black"


def test_cascading_style_definition():
    with border(color="#2A8387"):
        assert style._css_style() == "border: 1.0px solid #2A8387; border-radius: 0px; background-color: white; color: black"

        with background(color="#36A9AE"):
            assert style._css_style() == "border: 1.0px solid #2A8387; border-radius: 0px; background-color: #36A9AE; color: black"


def test_sample(tmp_path):
    page = Page()

    with border(color="#2A8387", corners="rounded"):

        with background(color="#36A9AE"), text(color="white"):
            page.add(button("Primary", 10, 10))

        page.add(button("Secondary", 80, 10))

    assert page.render() == (
        '<html><body>'
        '<button style="border: 1.0px solid #2A8387; border-radius: 4px; '
        'background-color: #36A9AE; color: white; position: absolute; left: 10px; '
        'top: 10px">Primary</button>'
        '<button style="border: 1.0px solid #2A8387; '
        'border-radius: 4px; background-color: white; color: black; position: '
        'absolute; left: 80px; top: 10px">Secondary</button>'
        '</body></html>'
    )

    # file_path = tmp_path / "test.html"
    # file_path.write_text(page.render())
    # webbrowser.open(f"file://{file_path}")