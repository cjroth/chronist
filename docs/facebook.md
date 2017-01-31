# Facebook

1. Make sure you have installed [Chronist](../README.md).

2. Go to [https://www.facebook.com/settings](https://www.facebook.com/settings) and click "Download a copy of your Facebook data" - this will email you a link to download your data.

3. Unzip the file and copy `html/messages.htm` to your desktop.

4. Run `chronist facebook -i ~/Desktop/messages.htm -n "YOUR NAME"`, being sure to replace `YOUR NAME` with your name as it appears on Facebook in quotes.

5. Your results will be saved to `~/Desktop/chronist-facebook-<USERNAME>.csv`

# No Python?

I did write a tool to parse Facebook messages that doesn't use Python, but it's **very** slow so I do not recommend using it unless you absolutely can't get the Python version working. You can run it with `chronist facebook --nopython -i ~/Desktop/messages.htm -n "YOUR NAME"`.
