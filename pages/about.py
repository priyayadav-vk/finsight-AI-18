"""Legacy Streamlit page wrapper. Delegates rendering to the frontend.pages package."""

from frontend.pages import about as page


def show():
    page.show()


if __name__ == '__main__':
    show()
