ps ux| grep tagger.py | grep -v "grep"| awk '{print $2}' | xargs kill -9
