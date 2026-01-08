from dataclasses import dataclass
from english_words import get_english_words_set
from playwright.sync_api import sync_playwright

@dataclass
class Result:
    all_guesses: list[str]
    tries: int
    solution: str

def find_all_words(length: int) -> list[str]:
    web2lowerset = get_english_words_set(['web2'], lower=True)
    return sorted([word for word in web2lowerset if len(word) == length])

def find_midpoint(length: int, all_words: list[str], page) -> str:
    a, b = find_bounds(length, page)
    words = [word for word in all_words if word > a and word < b]
    return words[len(words) // 2]

def find_bounds(length: int, page) -> list[str]:
    letters = page.locator("div.tile-boundary").all_text_contents()
    return ["".join(letters[length*i:length*(i+1)]).lower() for i in range(2)]

def close_intro(page) -> None:
    page.get_by_role("button", name="×", exact=True).click()
    page.wait_for_timeout(1000)

def make_guess(guess: str, page) -> None:
    page.locator("button.tile-empty, button.tile-guess").first.click()
    [page.keyboard.press(x) for x in guess]
    page.keyboard.press("Enter")
    page.wait_for_timeout(3000)

def clear_guess(length: int, page) -> None:
    for _ in range(length):
        page.keyboard.press("Backspace")

def is_invalid(page) -> bool:
    return page.get_by_text("Word not in dictionary", exact=True).is_visible()

def is_win(page) -> bool:
    return page.get_by_role("button", name="Share Result", exact=True).is_visible()

def solve(length: int) -> Result:
    all_words = find_all_words(length)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://www.franticfive.com/")
        page.wait_for_timeout(5000)
        close_intro(page)

        guesses = []
        while not is_win(page):
            guess = find_midpoint(length, all_words, page)
            make_guess(guess, page)

            if is_invalid(page):
                all_words.remove(guess)
                clear_guess(length, page)
            else:
                guesses.append(guess)

        browser.close()
        return Result(guesses, len(guesses), guesses[-1])

if __name__ == '__main__':
    print(solve(5))

