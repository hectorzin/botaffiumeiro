# 2.1.6.0

- Updating to release version 2.1.6
- refactor/pre-commit rules by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/78
- [pre-commit.ci] pre-commit autoupdate by @pre-commit-ci in https://github.com/hectorzin/botaffiumeiro/pull/79
- bug: bad links generated if a punctuation at the end of the link by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/81

# 2.1.5.0

- bug: Redirect URLs for Aliexpress are not working by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/75
- Updating to release version 2.1.5

# 2.1.4.2

- crashes because it is passigne creator percentage as an str not a number

# 2.1.4.1

- bug: Percentage donation to creators where not passing from addon configuration to Bottafiumeiro app.

# 2.1.4.0

- bug: If a short link has a . or , at the end won't expand and is not processed by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/69
- feat: Expand always URLs, to avoid loosing some links by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/70

# 2.1.3.0

- bug: Aliexpress codes showed two times by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/67

# 2.1.2.0

- addon bug, not updating to the latest version

# 2.1.1.1

- bug:rexexp error fixed, addon failed to work

# 2.1.1.0

- bug: amzn.eu not handled by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/62

# 2.1.0

### NEW!

Tradedoubler affiliate platform support: This platform allows affiliations to stores like mediamarkt, philips-hue, balay, boshc, dyson, HP, Huawey, PCBOX, etc.

### Improvements and fixes

- feat: Refactor pattern handlers by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/57
- bug: Short urls are not working by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/59
- Feat/tradedoubler by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/58

# 2.0.3

- bug: long Aliexpress links fails when asking API for an affiliate link by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/53
- feat: Show examples of HTML code in config.yaml by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/48
- doc: Add video tutorial to documentation by @hectorzin in https://github.com/hectorzin/botaffiumeiro/pull/50

**Full Changelog**: https://github.com/hectorzin/botaffiumeiro/compare/2.0.1...2.0.2

# 2.0.2

Bug/Amazon configuration error while sending from HA Addon to Botaffiumeiro

# 2.0.1

Bug/domain_added_two_times

# 2.0.0

## WARNING: BREAKING CHANGES

The way to configure Amazon links has changed.
This is because it has been unified with affiliate stores and now allows handling Amazon from different countries.
The new way to configure it is as follows:

amazon:
amazon.es: botaffiumeiro_cofee-21
amazon.com: hectorzindomo-20
amazon.com.au: hectorzindomo-22
amazon.co.uk: hectorzindomo-21
amazon.fr: hectorzindo0d-21
amazon.it: hectorzindo04-21
amazon.de: hectorzindo0e-21

## New features

- allow use of HTML in predefined messages: We can now use bold, italic, etc styles in the predefined messages as shown in the following image:
  ![image](https://github.com/user-attachments/assets/39fb1059-5e34-4c1e-b988-1ba6aebb51f8)
- You can use custom commands so that your Telegram group users can request AliExpress discount codes: /discount /aliexpress, etc.
- Improved Logging levels
- We've replaced the classic "give a coffee" with a parameter that represents the approximate % (as it is random) of times the affiliate link will belong to the creators. This parameter is entirely optional and can be set between 0 and 100%; by default, it is set to 10%. Thanks!
