# 750 Words

1. Make sure you have installed Python and [Chronist](../README.md).

2. Use the 750 Words Analysis tool by kinverarity1: https://github.com/kinverarity1/750words-analysis

    `git clone git@github.com:kinverarity1/750words-analysis.git`

    `cd 750words-analysis`

    `pip install pyquery requests lxml matplotlib`

3. Download your 750 Words entries.

    `mkdir ~/Desktop/750words`

    `python download_750words.py -u "YOUR EMAIL" -p "YOUR PASSWORD" -a -P ~/Desktop/750words`

3. Run `chronist 750words -i ~/Desktop/750words`

4. Your results will be saved to `~/Desktop/chronist-750words-<USERNAME>.csv`
