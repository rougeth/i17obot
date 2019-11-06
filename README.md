# 🐍💱 i17obot
[@i17obot](https://t.me/i17obot)

Telegram bot created to help the translation of the Python documentation to Brazilian Portuguese.

![](https://i.giphy.com/media/QsY8yp5q4atcQ/giphy.webp)


## Installing

#### Dependencies

```
$ pipenv install
```

If you don't have `pipenv` available, you can install via `pip`.

#### Configuration

Create a new `.env` file based on `local.env` and populate it with the listed variables:
```
$ cp local.env .env
```

## Running

#### To run the bot
```
$ pipenv run python i17obot/main.py
```

#### To run the reminder task
```
$ pipenv run python i17obot/reminder.py
```

## FAQ

### Why the project isn't in Portuguese?

Because we want to make it accessible to people translating the Python docs to other languages.


### But why **i17o**?  

**Internacionalização**  
**I** ---- 17 letters --- **O**

_"Internacionalização"_ is the Portuguese translation of _"Internationalization"_, which is frequently abbreviated to the numeronyms i18n.

> [...] means of adapting computer software to different languages, regional peculiarities and technical requirements of a target locale.

- reference: [Wikipedia](https://en.wikipedia.org/wiki/Internationalization_and_localization)


